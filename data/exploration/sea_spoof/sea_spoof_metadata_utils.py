"""Remote, pinned SEA-Spoof metadata EDA. Never select the audio column."""

from __future__ import annotations

import hashlib
import io
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

DATASET = "Jack-ppkdczgx/SEA-Spoof"
DEFAULT_REVISION = "132f5dca9b6efe39cf1d3b54a858f167f5a421fc"
SPLITS = ("train", "validation", "evaluation")
SOURCE_COLUMNS = (
    "row_id", "utterance_id", "audio", "text", "language", "label",
    "spoof_type", "category", "split", "text_source", "mapping_source",
    "text_granularity", "is_text_exact", "source_model", "source_dataset",
    "speaker_or_voice", "sampling_rate", "audio_was_resampled",
)
READ_COLUMNS = tuple(name for name in SOURCE_COLUMNS if name != "audio")
MEANINGS = {
    "row_id": "รหัสแถวของ release; ใช้เชื่อมข้อมูล ไม่ใช่รหัสผู้พูด",
    "utterance_id": "รหัส utterance ต้นทาง; อาจซ้ำข้ามแหล่งข้อมูล",
    "audio": "FLAC bytes และ logical path; ไม่เลือกอ่านในงานนี้",
    "text": "ข้อความที่เชื่อมกับคลิป; ต้องพิจารณาความตรงและ provenance",
    "language": "รหัสภาษา; th ไม่ได้ยืนยันสำเนียง/ถิ่นของผู้พูด",
    "label": "bonafide=เสียงจริง; spoof=เสียงปลอมตาม label ต้นทาง",
    "spoof_type": "กลุ่มเสียงปลอมตามต้นทาง; ค่าว่างในเสียงจริงอาจไม่ applicable",
    "category": "หมวดเสียง/แหล่งเสียง เช่น bonafide, offline_spoof, online_spoof",
    "split": "ส่วนข้อมูล train/validation/evaluation ตามต้นทาง",
    "text_source": "รายละเอียดที่มาของข้อความ",
    "mapping_source": "ที่มาของการจับคู่ข้อความ เช่น local หรือ whisperx_backfill",
    "text_granularity": "ระดับการจับคู่ข้อความ เช่น utterance หรือ source/video",
    "is_text_exact": "flag ของต้นทางว่าคาดว่าข้อความตรงระดับ utterance; ไม่ใช่การฟังตรวจของเรา",
    "source_model": "ระบบสร้างเสียงปลอม; ไม่ใช่ detector AASIST/RawNet2",
    "source_dataset": "ชุดข้อมูลเดิมที่เสียงมาจาก; ว่างอาจไม่ applicable",
    "speaker_or_voice": "รหัสผู้พูดหรือ synthetic voice; ไม่ยืนยันจำนวนบุคคล",
    "sampling_rate": "sample rate ตาม metadata; ยังไม่ตรวจ header ของเสียง",
    "audio_was_resampled": "flag ว่าต้นทาง resample ตอน packaging หรือไม่",
    "official_split": "ชื่อ split จากตำแหน่ง shard; เราเพิ่มเพื่อตรวจเทียบ split",
    "source_parquet": "ชื่อ shard ต้นทางที่เราเพิ่มเพื่อสืบย้อน provenance",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Coalesce ONLY overlapping/adjacent selected chunks, never across gaps."""
    result: list[tuple[int, int]] = []
    for start, stop in sorted(ranges):
        if start < 0 or stop <= start:
            raise ValueError("Invalid byte range")
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(stop, result[-1][1]))
        else:
            result.append((start, stop))
    return result


def selected_metadata_ranges(metadata, size: int, columns=READ_COLUMNS):
    """Plan selected chunks plus structural reads; never bridge audio gaps."""
    footer_bytes = max(65536, metadata.serialized_size + 8)
    ranges = [(0, 4), (max(0, size - footer_bytes), size)]
    selected_bytes = 0
    for i in range(metadata.num_row_groups):
        group = metadata.row_group(i)
        for j in range(group.num_columns):
            column = group.column(j)
            if column.path_in_schema.split(".")[0] not in columns:
                continue
            start = column.dictionary_page_offset
            if start is None:
                start = column.data_page_offset
            ranges.append((start, start + column.total_compressed_size))
            selected_bytes += column.total_compressed_size
    return ranges, selected_bytes


class MetadataRangeReader(io.RawIOBase):
    """Only allow Parquet reads within selected metadata chunks/footer/header.

    Adjacent non-audio columns share one HTTP request. Selected chunks stay in
    RAM for one shard. Footer reads may include incidental trailing bytes; this
    is not a claim that literally zero audio-related bytes cross the network.
    """

    def __init__(self, remote, size: int, ranges: list[tuple[int, int]]):
        super().__init__()
        self.remote = remote
        self.size = size
        self.ranges = merge_ranges(ranges)
        if any(stop > size for _, stop in self.ranges):
            raise ValueError("Range exceeds remote file")
        self.position = 0
        self.blocks: dict[tuple[int, int], bytes] = {}
        self.fetched_bytes = 0
        self.range_requests = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        position = offset if whence == io.SEEK_SET else self.position + offset if whence == io.SEEK_CUR else self.size + offset if whence == io.SEEK_END else -1
        if position < 0:
            raise ValueError("Invalid seek")
        self.position = position
        return position

    def read(self, size=-1):
        if self.position >= self.size or size == 0:
            return b""
        stop = self.size if size is None or size < 0 else min(self.size, self.position + size)
        interval = next(((a, b) for a, b in self.ranges if a <= self.position and stop <= b), None)
        if interval is None:
            raise ValueError("Blocked read outside selected metadata ranges (possibly audio)")
        if interval not in self.blocks:
            start, end = interval
            for attempt in range(3):
                try:
                    self.remote.seek(start)
                    payload = self.remote.read(end - start)
                    if len(payload) != end - start:
                        raise OSError("Incomplete HTTP range response")
                    break
                except (OSError, TimeoutError):
                    if attempt == 2:
                        raise
                    time.sleep(attempt + 1)
            self.blocks[interval] = payload
            self.fetched_bytes += len(payload)
            self.range_requests += 1
        payload = self.blocks[interval][self.position - interval[0]:stop - interval[0]]
        self.position = stop
        return payload

    def readinto(self, buffer):
        payload = self.read(len(buffer))
        buffer[:len(payload)] = payload
        return len(payload)


def fetch_metadata(root: Path, revision: str = DEFAULT_REVISION, workers: int = 4):
    """First read ALWAYS uses HF; later reuse only this new verified snapshot.

    Does not inspect/reuse existing SEA-Spoof raw shards, manifests or audio.
    Uses the user's existing HF login; no token is printed or saved.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Use an explicit 40-character commit SHA, not main")
    if not 1 <= workers <= 8:
        raise ValueError("workers must be between 1 and 8")
    directory = root / "data/raw/sea_spoof_metadata" / revision
    snapshot = directory / "metadata.parquet"
    provenance_path = directory / "provenance.json"
    if snapshot.is_file() and provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        expected = (provenance.get("dataset") == DATASET and provenance.get("revision") == revision
                    and provenance.get("audio_column_read") is False
                    and provenance.get("read_columns") == list(READ_COLUMNS)
                    and provenance.get("splits") == list(SPLITS))
        if not expected or provenance.get("metadata_sha256") != file_sha256(snapshot):
            raise ValueError("Snapshot provenance/checksum mismatch; will not overwrite")
        print("Using verified NEW metadata snapshot; no original local dataset files used.", flush=True)
        return snapshot, provenance
    if snapshot.exists() or provenance_path.exists() or snapshot.with_suffix(".parquet.tmp").exists():
        raise ValueError("Incomplete metadata snapshot; inspect it before retrying")

    import pyarrow as pa
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem

    api = HfApi()  # Uses existing login/environment token, never serialize it.
    files = sorted(f for f in api.list_repo_files(DATASET, repo_type="dataset", revision=revision)
                   if re.fullmatch(r"data/(train|validation|evaluation)/[^/]+\.parquet", f))
    if {f.split("/")[1] for f in files} != set(SPLITS):
        raise ValueError("Remote revision must include all three official splits")

    def read_shard(filename):
        fs = HfFileSystem()
        remote_path = f"datasets/{DATASET}@{revision}/{filename}"
        with fs.open(remote_path, "rb", cache_type="none", block_size=64 * 1024) as remote:
            original = pq.ParquetFile(remote, pre_buffer=False)
            schema = original.schema_arrow
            if tuple(schema.names) != SOURCE_COLUMNS:
                raise ValueError(f"Unexpected schema in {filename}; refusing unknown columns")
            metadata = original.metadata
            ranges, selected_bytes = selected_metadata_ranges(metadata, remote.size)
            reader = MetadataRangeReader(remote, remote.size, ranges)
            parquet = pq.ParquetFile(reader, metadata=metadata, pre_buffer=False)
            table = parquet.read(columns=list(READ_COLUMNS), use_threads=False)
            if tuple(table.column_names) != READ_COLUMNS:
                raise AssertionError("Audio/unknown columns must never enter snapshot")
            split = filename.split("/")[1]
            table = table.append_column("official_split", pa.array([split] * table.num_rows))
            table = table.append_column("source_parquet", pa.array([filename] * table.num_rows))
            record = {
                "file": filename, "split": split, "rows": table.num_rows,
                "source_file_bytes": remote.size, "row_groups": metadata.num_row_groups,
                "selected_metadata_compressed_bytes": selected_bytes,
                "reader_fetched_bytes_excluding_initial_footer": reader.fetched_bytes,
                "reader_range_requests": reader.range_requests,
                "source_schema": [{"column": field.name, "arrow_type": str(field.type)} for field in schema],
                "read_columns": list(READ_COLUMNS),
            }
        print(f"Remote metadata: {filename}: {table.num_rows:,} rows; selected {selected_bytes / 1e6:.2f} MB, no audio column", flush=True)
        return table, record

    print(f"Reading {len(files)} remote shards at {revision}; metadata only.", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(read_shard, files))
    if any(item[1]["source_schema"] != fetched[0][1]["source_schema"] for item in fetched):
        raise ValueError("Source schemas differ across shards")
    table = pa.concat_tables([item[0] for item in fetched])
    if "audio" in table.column_names:
        raise AssertionError("Audio column forbidden")
    if any(a != b for a, b in zip(table["split"].to_pylist(), table["official_split"].to_pylist())):
        raise ValueError("Source split does not match shard directory")
    directory.mkdir(parents=True, exist_ok=True)
    temporary = snapshot.with_suffix(".parquet.tmp")
    pq.write_table(table, temporary, compression="zstd")
    temporary.replace(snapshot)
    provenance = {
        "dataset": DATASET, "revision": revision,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": table.num_rows, "shards": len(files), "splits": list(SPLITS),
        "source_columns": fetched[0][1]["source_schema"],
        "read_columns": list(READ_COLUMNS), "saved_columns": table.column_names,
        "audio_column_read": False, "audio_files_downloaded": 0,
        "original_local_dataset_files_used": False,
        "metadata_sha256": file_sha256(snapshot), "files": [item[1] for item in fetched],
        "scope": "Remote HTTP byte ranges for Parquet schema/footer and selected non-audio chunks. No complete source shards or audio files saved. Incidental footer bytes are not an audio download/inspection.",
    }
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snapshot, provenance


def blank_mask(series):
    """Missing = null OR whitespace-only; False/0/'none' are NOT missing."""
    return series.isna() | series.astype("string").str.strip().eq("").fillna(False)


def missing_profile(frame, columns):
    import pandas as pd
    rows = []
    for name in columns:
        series = frame[name]
        null = series.isna()
        missing = blank_mask(series)
        rows.append({"column": name, "dtype": str(series.dtype), "null_rows": int(null.sum()),
                     "blank_string_rows": int((missing & ~null).sum()),
                     "missing_rows": int(missing.sum()),
                     "missing_pct": 100 * float(missing.mean()) if len(series) else 0,
                     "unique_nonblank_values": int(series[~missing].nunique())})
    return pd.DataFrame(rows).sort_values("missing_rows", ascending=False, kind="stable").reset_index(drop=True)


def normalized_text(series):
    return series.astype("string").fillna("").str.normalize("NFC").str.replace(r"\s+", " ", regex=True).str.strip().str.casefold()


def overlap_table(frame, column):
    """Exact nonblank value overlap, NOT audio duplication or speaker identity."""
    import pandas as pd
    from itertools import combinations
    values = frame[column].astype("string").str.strip()
    groups = {s: set(values[(frame["official_split"] == s) & ~blank_mask(values)]) for s in SPLITS}
    rows = []
    for left, right in combinations(SPLITS, 2):
        shared = groups[left] & groups[right]
        rows.append({"field": column, "left_split": left, "right_split": right,
                     "shared_unique_values": len(shared),
                     "left_rows_with_shared_values": int(((frame["official_split"] == left) & values.isin(shared)).sum()),
                     "right_rows_with_shared_values": int(((frame["official_split"] == right) & values.isin(shared)).sum())})
    return pd.DataFrame(rows)


def namespaced_voice_keys(frame):
    """Keep source namespaces; still only candidate codes, never persons."""
    import pandas as pd
    fields = {name: frame[name].astype("string").fillna("").str.strip()
              for name in ("source_dataset", "source_model", "speaker_or_voice")}
    keys = [json.dumps([dataset, model, voice], ensure_ascii=False)
            if voice and (dataset or model) else ""
            for dataset, model, voice in zip(fields["source_dataset"], fields["source_model"], fields["speaker_or_voice"])]
    return pd.Series(keys, index=frame.index, dtype="string")
