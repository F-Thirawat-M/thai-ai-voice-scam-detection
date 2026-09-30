from __future__ import annotations

import csv
import io

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import soundfile as sf

from scripts.extract_thai_parquet import extract_split


def _flac_bytes() -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, np.zeros(1600, dtype=np.float32), 16000, format="FLAC")
    return buffer.getvalue()


def _row(row_id: str, language: str, label: str) -> dict[str, object]:
    return {
        "row_id": row_id,
        "utterance_id": f"utterance_{row_id}",
        "audio": {"bytes": _flac_bytes(), "path": f"audio/{row_id}.flac"},
        "text": "เสียงทดสอบ",
        "language": language,
        "label": label,
        "spoof_type": "bonafide" if label == "bonafide" else "offline",
        "category": "bonafide" if label == "bonafide" else "offline_spoof",
        "split": "validation",
        "sampling_rate": 16000,
    }


def test_extracts_thai_audio_and_preserves_metadata(tmp_path):
    project_root = tmp_path / "project"
    source_dir = project_root / "data/raw/sea_spoof_hf/data/validation"
    source_dir.mkdir(parents=True)
    pq.write_table(
        pa.Table.from_pylist(
            [
                _row("th_real", "th", "bonafide"),
                _row("en_fake", "en", "spoof"),
                _row("th_fake", "th", "spoof"),
            ]
        ),
        source_dir / "validation-00000.parquet",
    )
    audio_root = project_root / "data/processed/sea_spoof_th/audio"
    manifest = project_root / "data/manifests/thai_dev.csv"

    for _ in range(2):
        counts = extract_split(source_dir.parent, audio_root, manifest, "validation", project_root)
        assert counts == {"bonafide": 1, "spoof": 1}

    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert {row["row_id"] for row in rows} == {"th_real", "th_fake"}
    assert {(row["row_id"], row["label"]) for row in rows} == {
        ("th_real", "bonafide"),
        ("th_fake", "spoof"),
    }
    assert rows[0]["text"] == "เสียงทดสอบ"
    assert rows[0]["condition"] == "clean"
    assert rows[0]["source_audio_path"] == "audio/th_real.flac"
    assert rows[0]["path"].startswith("data/processed/")
    assert len(list((audio_root / "validation").glob("*.flac"))) == 2
    assert sf.info(project_root / rows[0]["path"]).samplerate == 16000


def test_rejects_duplicate_row_id(tmp_path):
    source_dir = tmp_path / "source/validation"
    source_dir.mkdir(parents=True)
    pq.write_table(
        pa.Table.from_pylist([_row("duplicate", "th", "spoof")] * 2),
        source_dir / "validation-00000.parquet",
    )

    with pytest.raises(ValueError, match="Duplicate row_id"):
        extract_split(
            source_dir.parent,
            tmp_path / "audio",
            tmp_path / "thai_dev.csv",
            "validation",
            tmp_path,
        )
    assert not (tmp_path / "thai_dev.csv").exists()
