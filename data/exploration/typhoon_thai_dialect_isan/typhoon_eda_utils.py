"""Pinned, metadata-only Typhoon reads; never request the audio column."""

from __future__ import annotations

import hashlib
import json
import math
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


DATASET = "typhoon-ai/thai-dialect-isan-dataset"
DEFAULT_REVISION = "dfc7e495b3069940880d184f0acfcc6b3cd4f364"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_string(value: object) -> str:
    return "" if value is None else str(value).strip()


def parse_age(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and 0 < number < 120 else None


def age_band(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "unknown"
    return "<18" if value < 18 else "18-29" if value < 30 else "30-44" if value < 45 else "45-59" if value < 60 else "60+"


def parse_filename(value: object) -> dict[str, str]:
    """Third filename component is only a candidate key, NOT verified identity."""
    parts = clean_string(value).split(";")
    if len(parts) != 5 or not re.fullmatch(r"[fmx]_\d+", parts[2]):
        return {"candidate_speaker_key": "", "prompt_domain_code": "", "filename_parse_status": "unparsed"}
    return {"candidate_speaker_key": parts[2], "prompt_domain_code": parts[3], "filename_parse_status": "parsed"}


def fetch_metadata(root: Path, revision: str = DEFAULT_REVISION, workers: int = 4) -> tuple[Path, dict]:
    """Save metadata columns only. Reuse only a validated, pinned snapshot.

    Hugging Face byte-range reads include Parquet footer/schema + selected
    metadata chunks; no audio column, decoded audio, or entire shards saved.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Use an explicit 40-character commit SHA, not a moving branch.")
    if workers < 1:
        raise ValueError("workers must be positive")
    snapshot_dir = root / "data/raw/typhoon_thai_dialect_isan/metadata" / revision
    snapshot = snapshot_dir / "metadata.parquet"
    provenance_path = snapshot_dir / "provenance.json"
    if snapshot.is_file() and provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        if provenance.get("revision") != revision or provenance.get("dataset") != DATASET:
            raise ValueError("Cached snapshot provenance mismatch; not overwriting.")
        if provenance.get("metadata_sha256") != file_sha256(snapshot):
            raise ValueError("Metadata snapshot checksum mismatch; inspect cache before retrying.")
        print("Using validated local metadata snapshot (no network/audio download).", flush=True)
        return snapshot, provenance
    if snapshot.exists() or provenance_path.exists():
        raise ValueError("Incomplete metadata snapshot exists; inspect it before retrying.")

    import pyarrow as pa
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem

    api = HfApi(token=False)
    files = sorted(f for f in api.list_repo_files(DATASET, repo_type="dataset", revision=revision)
                   if re.fullmatch(r"data/(train|test)-\d+-of-\d+\.parquet", f))
    if not files:
        raise ValueError("No train/test Parquet shards found at pinned revision.")

    def read_shard(filename: str):
        fs = HfFileSystem(token=False)
        remote = f"datasets/{DATASET}@{revision}/{filename}"
        with fs.open(remote, "rb", cache_type="none", block_size=64 * 1024) as handle:
            parquet = pq.ParquetFile(handle, pre_buffer=False)
            fields = [field.name for field in parquet.schema_arrow if field.name != "audio"]
            if "audio" not in parquet.schema_arrow.names:
                raise ValueError("Unexpected source schema: no audio field")
            if not {"id", "name", "age", "gender", "province", "district", "duration"}.issubset(fields):
                raise ValueError("Missing required source metadata")
            schema = [{"column": field.name, "arrow_type": str(field.type)} for field in parquet.schema_arrow]
            table = parquet.read(columns=fields, use_threads=False)
            if "audio" in table.column_names:
                raise AssertionError("Audio must never be read into metadata snapshot")
            split = filename.split("/")[-1].split("-")[0]
            table = table.append_column("official_split", pa.array([split] * table.num_rows))
            table = table.append_column("source_parquet", pa.array([filename] * table.num_rows))
            record = {"file": filename, "split": split, "rows": table.num_rows,
                      "source_schema": schema, "read_columns": fields}
        print(f"Metadata only: {filename} ({table.num_rows} rows)", flush=True)
        return table, record

    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(read_shard, files))
    table = pa.concat_tables([item[0] for item in fetched])
    # Never trust a schema evolution that would introduce audio-like fields.
    if any(name in table.column_names for name in ["audio", "bytes", "array"]):
        raise ValueError("Unexpected audio column in metadata table")
    if set(table["official_split"].to_pylist()) != {"train", "test"}:
        raise ValueError("Pinned snapshot must contain both train and test metadata.")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    temporary = snapshot.with_suffix(".parquet.tmp")
    pq.write_table(table, temporary, compression="zstd")
    temporary.replace(snapshot)
    provenance = {
        "dataset": DATASET, "revision": revision,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": table.num_rows, "shards": len(files),
        "source_columns": fetched[0][1]["source_schema"],
        "saved_columns": table.column_names, "audio_column_read": False,
        "audio_files_downloaded": 0, "metadata_sha256": file_sha256(snapshot),
        "files": [item[1] for item in fetched],
        "scope": "HTTP byte ranges: footer/schema and non-audio metadata columns only; no entire Parquet/audio files saved.",
    }
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snapshot, provenance
