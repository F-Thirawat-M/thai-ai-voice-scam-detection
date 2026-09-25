"""Create a local evaluation manifest from the approved Thai SEA-Spoof export.

The metadata contains Colab/Drive audio paths. Only their filenames are used;
the audio is expected below data/raw/sea_spoof_th/audio/<split>/ locally.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data/raw/sea_spoof_th"


def prepare_manifest(
    metadata_path: Path,
    audio_root: Path,
    split: str,
    output_path: Path,
) -> dict[str, int]:
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    missing: list[Path] = []
    seen_row_ids: set[str] = set()
    seen_paths: set[Path] = set()

    with metadata_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            record = json.loads(line)
            if record.get("language") != "th" or record.get("split") != split:
                continue

            label = record.get("label")
            if label not in {"bonafide", "spoof"}:
                raise ValueError(f"Invalid label on metadata line {line_number}: {label!r}")

            row_id = record.get("row_id")
            if not row_id or row_id in seen_row_ids:
                raise ValueError(f"Missing or duplicate row_id on metadata line {line_number}")
            seen_row_ids.add(row_id)

            source_path = record.get("audio_path")
            if not source_path:
                raise ValueError(f"Missing audio_path on metadata line {line_number}")
            filename = Path(source_path).name
            if not filename.lower().endswith(".flac"):
                raise ValueError(f"Expected FLAC on metadata line {line_number}: {filename}")

            local_path = audio_root / split / filename
            if local_path in seen_paths:
                raise ValueError(f"Duplicate audio filename on metadata line {line_number}: {filename}")
            seen_paths.add(local_path)
            if not local_path.is_file():
                missing.append(local_path)

            try:
                manifest_path = local_path.relative_to(PROJECT_ROOT)
            except ValueError:
                manifest_path = local_path
            rows.append(
                {
                    "path": manifest_path.as_posix(),
                    "label": label,
                    "row_id": row_id,
                    "utterance_id": str(record.get("utterance_id", "")),
                    "language": "th",
                    "split": split,
                    "spoof_type": str(record.get("spoof_type", "")),
                    "category": str(record.get("category", "")),
                    "source_model": str(record.get("source_model", "")),
                    "source_dataset": str(record.get("source_dataset", "")),
                    "speaker_or_voice": str(record.get("speaker_or_voice", "")),
                }
            )
            counts[label] += 1

    if not rows:
        raise ValueError(f"No Thai records found for split {split!r}")
    if missing:
        examples = "\n".join(f"  - {path}" for path in missing[:5])
        raise FileNotFoundError(
            f"{len(missing)} of {len(rows)} audio files are missing for {split}. "
            f"First examples:\n{examples}\nManifest was not written."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return dict(counts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_DATA_ROOT / "thai_metadata.jsonl")
    parser.add_argument("--audio-root", type=Path, default=DEFAULT_DATA_ROOT / "audio")
    parser.add_argument("--split", choices=["train", "validation", "evaluation"], default="evaluation")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/manifests/thai_evaluation.csv")
    args = parser.parse_args()
    counts = prepare_manifest(args.metadata, args.audio_root, args.split, args.output)
    print(f"Manifest: {args.output}")
    print(f"Rows: {sum(counts.values())} ({counts})")


if __name__ == "__main__":
    main()
