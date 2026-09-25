import csv
import json

import pytest

from scripts.prepare_thai_manifest import prepare_manifest


def test_prepare_manifest_uses_local_audio_and_labels(tmp_path):
    metadata = tmp_path / "thai_metadata.jsonl"
    audio_root = tmp_path / "audio"
    evaluation = audio_root / "evaluation"
    evaluation.mkdir(parents=True)
    (evaluation / "real.flac").write_bytes(b"example")
    (evaluation / "fake.flac").write_bytes(b"example")
    records = [
        {
            "row_id": "real-1",
            "utterance_id": "real",
            "language": "th",
            "label": "bonafide",
            "split": "evaluation",
            "audio_path": "/content/drive/audio/evaluation/real.flac",
        },
        {
            "row_id": "fake-1",
            "utterance_id": "fake",
            "language": "th",
            "label": "spoof",
            "split": "evaluation",
            "audio_path": "/content/drive/audio/evaluation/fake.flac",
        },
    ]
    metadata.write_text("\n".join(json.dumps(row) for row in records), encoding="utf-8")

    output = tmp_path / "manifest.csv"
    assert prepare_manifest(metadata, audio_root, "evaluation", output) == {
        "bonafide": 1,
        "spoof": 1,
    }
    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["label"] for row in rows] == ["bonafide", "spoof"]
    assert rows[0]["path"] == (evaluation / "real.flac").as_posix()


def test_prepare_manifest_refuses_incomplete_audio(tmp_path):
    metadata = tmp_path / "thai_metadata.jsonl"
    metadata.write_text(
        json.dumps(
            {
                "row_id": "missing-1",
                "language": "th",
                "label": "spoof",
                "split": "evaluation",
                "audio_path": "/content/drive/audio/evaluation/missing.flac",
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "manifest.csv"

    with pytest.raises(FileNotFoundError, match="Manifest was not written"):
        prepare_manifest(metadata, tmp_path / "audio", "evaluation", output)
    assert not output.exists()
