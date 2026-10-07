import pytest

from thai_spoof.cvtts.artifacts import write_immutable_artifacts


def test_exclusive_writes_and_identical_reruns(tmp_path) -> None:
    files = {tmp_path / "nested/one.bin": b"one", tmp_path / "two.bin": b"two"}
    assert write_immutable_artifacts(files) == 2
    assert write_immutable_artifacts(files) == 0
    assert all(path.read_bytes() == content for path, content in files.items())


def test_conflict_is_checked_before_any_new_file_is_written(tmp_path) -> None:
    existing = tmp_path / "existing.bin"
    existing.write_bytes(b"original")
    new = tmp_path / "new.bin"
    with pytest.raises(FileExistsError, match="differs"):
        write_immutable_artifacts({new: b"new", existing: b"changed"})
    assert existing.read_bytes() == b"original"
    assert not new.exists()
