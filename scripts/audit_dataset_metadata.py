"""Audit local SEA-Spoof and public Typhoon metadata without downloading audio.

The candidate speaker key is parsed from Typhoon filenames, not an independently
verified person identifier. Remote reads select only metadata Parquet columns.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = "typhoon-ai/thai-dialect-isan-dataset"


def read_metadata_file(task):
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    revision, filename = task
    fs = HfFileSystem(token=False)
    remote = f"datasets/{DATASET}@{revision}/{filename}"
    fields = ["id", "name", "age", "gender", "province", "district", "duration"]
    with fs.open(remote, "rb", cache_type="none", block_size=64 * 1024) as handle:
        parquet = pq.ParquetFile(handle, pre_buffer=False)
        rows = parquet.read(columns=fields).to_pylist()
    print(f"Read metadata: {filename} ({len(rows)} rows)", flush=True)
    return ("test" if filename.startswith("data/test-") else "train"), rows


def age_value(value):
    try:
        n = float(value)
        return n if math.isfinite(n) and 0 < n < 120 else None
    except (ValueError, TypeError):
        return None


def speaker_key(row):
    parts = (row.get("name") or "").split(";")
    return parts[2] if len(parts) == 5 else None


def summarize(rows):
    fields = ("gender", "province", "district")
    ages = [age_value(r["age"]) for r in rows]
    speakers = defaultdict(list)
    for r in rows:
        key = speaker_key(r)
        if key:
            speakers[key].append(r)
    distributions = {}
    for field in fields:
        clips = Counter(str(r.get(field) or "unknown") for r in rows)
        people = Counter()
        for group in speakers.values():
            values = {str(r.get(field) or "unknown") for r in group}
            people[next(iter(values)) if len(values) == 1 else "conflicting"] += 1
        distributions[field] = {"clips": dict(clips), "candidate_speakers": dict(people)}
    def band(n):
        if n is None:
            return "unknown"
        return "under_18" if n < 18 else "18_29" if n < 30 else "30_44" if n < 45 else "45_59" if n < 60 else "60_plus"
    speaker_ages = Counter()
    conflicts = 0
    for group in speakers.values():
        values = {age_value(r["age"]) for r in group}
        conflicts += len(values) > 1
        speaker_ages[band(next(iter(values))) if len(values) == 1 else "conflicting"] += 1
    known = [a for a in ages if a is not None]
    return {
        "clips": len(rows), "unique_row_ids": len({r["id"] for r in rows}),
        "hours": round(sum(float(r.get("duration") or 0) for r in rows) / 3600, 3),
        "candidate_speakers": len(speakers),
        "unparsed_speaker_clips": sum(speaker_key(r) is None for r in rows),
        "age_known_clips": len(known), "age_range": [min(known), max(known)] if known else None,
        "age_bands_clips": dict(Counter(band(a) for a in ages)),
        "age_bands_candidate_speakers": dict(speaker_ages),
        "candidate_speakers_with_inconsistent_age": conflicts,
        "complete_age_gender_province_clips": sum(age_value(r["age"]) is not None and r["gender"] in ("m", "f") and bool(r["province"]) for r in rows),
        "distributions": distributions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--typhoon", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "results/dataset_metadata_audit.json")
    args = parser.parse_args()
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "sea_spoof": {}}
    for path in sorted((ROOT / "data/manifests").glob("thai_*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames
            rows = list(reader)
        result["sea_spoof"][path.name] = {
            "clips": len(rows), "columns": columns,
            "labels": dict(Counter(r["label"] for r in rows)),
            "bonafide_sources": dict(Counter(r.get("source_dataset", "") for r in rows if r["label"] == "bonafide")),
            "nonempty_bonafide_speaker_ids": sum(bool(r.get("speaker_or_voice")) for r in rows if r["label"] == "bonafide"),
        }
    if args.typhoon:
        from huggingface_hub import HfApi
        api = HfApi(token=False)
        revision = api.dataset_info(DATASET).sha
        files = [f for f in api.list_repo_files(DATASET, repo_type="dataset", revision=revision)
                 if f.startswith(("data/train-", "data/test-")) and f.endswith(".parquet")]
        if not files:
            raise ValueError("No source Parquet files found")
        split_rows = {"train": [], "test": []}
        with ThreadPoolExecutor(max_workers=4) as pool:
            for split, rows in pool.map(read_metadata_file, [(revision, f) for f in files]):
                split_rows[split].extend(rows)
        for split, rows in split_rows.items():
            if not rows or len({r["id"] for r in rows}) != len(rows):
                raise ValueError("Missing or duplicate rows")
        result["typhoon"] = {s: summarize(r) for s, r in split_rows.items()}
        result["typhoon"]["combined"] = summarize(split_rows["train"] + split_rows["test"])
        keys = {s: {speaker_key(r) for r in rows} - {None} for s, rows in split_rows.items()}
        result["typhoon"]["candidate_speaker_overlap_train_test"] = len(keys["train"] & keys["test"])
        result["typhoon"]["source"] = "https://huggingface.co/datasets/" + DATASET
        result["typhoon"]["revision"] = revision
        result["typhoon"]["parquet_files"] = files
        result["typhoon"]["limitations"] = "Pinned revision; metadata column reads only; candidate speaker IDs parsed from filenames; x/blank gender counted as unspecified."
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output, flush=True)


if __name__ == "__main__":
    main()
