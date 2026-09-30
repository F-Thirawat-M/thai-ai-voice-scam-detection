"""Extract Thai FLAC audio and a labeled manifest from SEA-Spoof Parquet shards.

The source Parquet files are never changed. Run this once for validation and
evaluation before scoring the pretrained models.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
import soundfile as sf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "data/raw/sea_spoof_hf/data"
DEFAULT_AUDIO_ROOT = PROJECT_ROOT / "data/processed/sea_spoof_th/audio"
MANIFEST_NAMES = {
    "train": "thai_train.csv",
    "validation": "thai_dev.csv",
    "evaluation": "thai_test.csv",
}
ROW_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]+\Z")
REQUIRED_FIELDS = {"row_id", "audio", "language", "label", "split", "sampling_rate"}


def extract_split(
    source_root: Path,
    audio_root: Path,
    manifest_path: Path,
    split: str,
    project_root: Path = PROJECT_ROOT,
) -> Counter[str]:
    """Write only Thai audio; preserve every non-audio source column in CSV."""
    if split not in MANIFEST_NAMES:
        raise ValueError(f"Unsupported split: {split}")
    source_dir = source_root / split
    shards = sorted(source_dir.glob("*.parquet"))
    if not shards:
        raise FileNotFoundError(f"No Parquet shards found in {source_dir}")

    source_fields = pq.ParquetFile(shards[0]).schema_arrow.names
    missing_fields = REQUIRED_FIELDS - set(source_fields)
    if missing_fields:
        raise ValueError(f"Missing source columns: {sorted(missing_fields)}")
    fieldnames = ["path", *[name for name in source_fields if name != "audio"]]
    fieldnames += ["source_audio_path", "condition", "source_parquet"]
    if len(fieldnames) != len(set(fieldnames)):
        raise ValueError("Source schema conflicts with generated manifest columns")

    split_audio_dir = audio_root / split
    split_audio_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_manifest = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    counts: Counter[str] = Counter()
    seen_row_ids: set[str] = set()

    with temporary_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for shard in shards:
            parquet = pq.ParquetFile(shard)
            if parquet.schema_arrow.names != source_fields:
                raise ValueError(f"Column mismatch in {shard}")
            for batch in parquet.iter_batches(batch_size=64):
                for record in batch.to_pylist():
                    if record["language"] != "th":
                        continue
                    if record["split"] != split:
                        raise ValueError(f"Wrong split in {shard}: {record['split']!r}")
                    label = record["label"]
                    if label not in {"bonafide", "spoof"}:
                        raise ValueError(f"Invalid label in {shard}: {label!r}")
                    row_id = record["row_id"]
                    if not isinstance(row_id, str) or not ROW_ID_PATTERN.fullmatch(row_id):
                        raise ValueError(f"Unsafe row_id in {shard}: {row_id!r}")
                    if row_id in seen_row_ids:
                        raise ValueError(f"Duplicate row_id: {row_id}")
                    seen_row_ids.add(row_id)

                    audio = record["audio"]
                    audio_bytes = audio.get("bytes") if isinstance(audio, dict) else None
                    if not isinstance(audio_bytes, bytes) or not audio_bytes.startswith(b"fLaC"):
                        raise ValueError(f"Missing or invalid FLAC bytes: {row_id}")
                    info = sf.info(io.BytesIO(audio_bytes))
                    if info.samplerate != 16_000 or record["sampling_rate"] != 16_000:
                        raise ValueError(f"Unexpected sample rate: {row_id}")

                    audio_path = split_audio_dir / f"{row_id}.flac"
                    if audio_path.exists():
                        if audio_path.read_bytes() != audio_bytes:
                            raise ValueError(f"Existing audio differs from source: {audio_path}")
                    else:
                        temporary_audio = audio_path.with_suffix(".flac.tmp")
                        with temporary_audio.open("wb") as audio_handle:
                            audio_handle.write(audio_bytes)
                        os.replace(temporary_audio, audio_path)

                    try:
                        manifest_audio_path = audio_path.relative_to(project_root).as_posix()
                    except ValueError:
                        manifest_audio_path = audio_path.as_posix()
                    metadata = {name: record[name] for name in source_fields if name != "audio"}
                    writer.writerow(
                        {
                            "path": manifest_audio_path,
                            **metadata,
                            "source_audio_path": audio.get("path") or "",
                            "condition": "clean",
                            "source_parquet": shard.name,
                        }
                    )
                    counts[label] += 1

    if not counts:
        raise ValueError(f"No Thai rows found in {source_dir}")
    os.replace(temporary_manifest, manifest_path)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=MANIFEST_NAMES, required=True)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--audio-root", type=Path, default=DEFAULT_AUDIO_ROOT)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    manifest = args.manifest or PROJECT_ROOT / "data/manifests" / MANIFEST_NAMES[args.split]
    counts = extract_split(args.source_root, args.audio_root, manifest, args.split)
    print(f"Manifest: {manifest}")
    print(f"Thai rows: {sum(counts.values())} (bonafide={counts['bonafide']}, spoof={counts['spoof']})")


if __name__ == "__main__":
    main()
