import io
import json

import pandas as pd
import pytest

from data.exploration.sea_spoof.sea_spoof_metadata_utils import (
    DEFAULT_REVISION, DATASET, READ_COLUMNS, SPLITS, MetadataRangeReader,
    blank_mask, fetch_metadata, file_sha256, merge_ranges, missing_profile,
    namespaced_voice_keys, normalized_text, overlap_table, selected_metadata_ranges,
)


def test_audio_is_not_selected():
    assert "audio" not in READ_COLUMNS
    assert len(READ_COLUMNS) == 17


def test_adjacent_ranges_merge_but_audio_gaps_do_not():
    assert merge_ranges([(10, 20), (20, 25), (0, 4), (100, 120)]) == [(0, 4), (10, 25), (100, 120)]


def test_reader_blocks_audio_and_caches_selected_chunks():
    remote = io.BytesIO(b"headMETAaudioDATAfoot")
    reader = MetadataRangeReader(remote, 21, [(4, 8), (13, 17)])
    reader.seek(4)
    assert reader.read(4) == b"META"
    reader.seek(5)
    assert reader.read(2) == b"ET"
    assert reader.range_requests == 1
    assert reader.fetched_bytes == 4
    reader.seek(8)
    with pytest.raises(ValueError, match="Blocked read"):
        reader.read(5)


def test_real_parquet_projection_uses_only_metadata_and_footer_ranges():
    import pyarrow as pa
    import pyarrow.parquet as pq
    # Uncompressed large audio deliberately separates metadata byte chunks.
    source = pa.table({"row_id": ["a", "b", "c", "d"],
                       "audio": [b"sound" * 30000 + bytes([i]) for i in range(4)],
                       "label": ["bonafide", "spoof", "spoof", "bonafide"]})
    remote = io.BytesIO()
    pq.write_table(source, remote, compression=None, use_dictionary=False, row_group_size=2)
    size = remote.tell()
    original = pq.ParquetFile(remote)
    ranges, selected_bytes = selected_metadata_ranges(original.metadata, size, ("row_id", "label"))
    reader = MetadataRangeReader(remote, size, ranges)
    projected = pq.ParquetFile(reader, metadata=original.metadata, pre_buffer=False).read(
        columns=["row_id", "label"], use_threads=False)
    assert projected.equals(source.select(["row_id", "label"]))
    assert reader.fetched_bytes < size / 2
    assert selected_bytes < 2000


def test_missing_does_not_treat_false_zero_or_none_string_as_blank():
    series = pd.Series([None, "", "  ", False, 0, "none", "x"])
    assert blank_mask(series).tolist() == [True, True, True, False, False, False, False]
    result = missing_profile(pd.DataFrame({"value": series}), ["value"]).iloc[0]
    assert result["null_rows"] == 1
    assert result["blank_string_rows"] == 2
    assert result["missing_rows"] == 3


def test_overlap_excludes_missing_and_counts_rows_separately_from_keys():
    frame = pd.DataFrame({"official_split": ["train", "train", "train", "validation", "validation", "evaluation"],
                          "key": ["same", "same", "", "same", None, "other"]})
    result = overlap_table(frame, "key")
    pair = result.iloc[0]
    assert pair["shared_unique_values"] == 1
    assert pair["left_rows_with_shared_values"] == 2
    assert pair["right_rows_with_shared_values"] == 1


def test_text_normalization_and_voice_namespaces():
    assert normalized_text(pd.Series([" A\n B ", None])).tolist() == ["a b", ""]
    frame = pd.DataFrame({"source_dataset": ["d1", "d2", "", "d1"],
                          "source_model": ["m", "m", "", "m"],
                          "speaker_or_voice": ["v", "v", "v", None]})
    keys = namespaced_voice_keys(frame)
    assert keys[0] != keys[1]
    assert keys[2] == keys[3] == ""


def test_revision_and_workers_validated_before_network(tmp_path):
    with pytest.raises(ValueError, match="commit SHA"):
        fetch_metadata(tmp_path, "main")
    with pytest.raises(ValueError, match="workers"):
        fetch_metadata(tmp_path, workers=0)


def test_valid_snapshot_offline_and_checksum_mismatch_not_overwritten(tmp_path):
    directory = tmp_path / "data/raw/sea_spoof_metadata" / DEFAULT_REVISION
    directory.mkdir(parents=True)
    snapshot = directory / "metadata.parquet"
    snapshot.write_bytes(b"test snapshot")
    provenance = {"dataset": DATASET, "revision": DEFAULT_REVISION, "audio_column_read": False,
                  "read_columns": list(READ_COLUMNS), "splits": list(SPLITS),
                  "metadata_sha256": file_sha256(snapshot)}
    path = directory / "provenance.json"
    path.write_text(json.dumps(provenance), encoding="utf-8")
    assert fetch_metadata(tmp_path)[0] == snapshot
    snapshot.write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        fetch_metadata(tmp_path)
    assert snapshot.read_bytes() == b"changed"
