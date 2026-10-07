import hashlib

import pytest

from thai_spoof.cvtts.provenance import verify_preparation_code


def test_exact_and_checkout_newlines_are_recorded(tmp_path):
    path = tmp_path / "code.py"
    content = b"x = 1\ny = 2\n"
    expected = hashlib.sha256(content).hexdigest()
    path.write_bytes(content)
    assert verify_preparation_code(path, expected)["verification"] == "exact"
    path.write_bytes(content.replace(b"\n", b"\r\n"))
    result = verify_preparation_code(path, expected)
    assert result["verification"] == "CRLF_to_LF_only"
    assert result["actual_file_sha256"] != expected and result["LF_normalized_sha256"] == expected


@pytest.mark.parametrize("content", [b"x = 3\ny = 2\n", b"x=1\ny=2\n", b"x = 1\ry = 2\r"])
def test_content_or_other_whitespace_changes_are_rejected(tmp_path, content):
    path = tmp_path / "code.py"
    path.write_bytes(content)
    expected = hashlib.sha256(b"x = 1\ny = 2\n").hexdigest()
    with pytest.raises(ValueError, match="changed beyond newline"):
        verify_preparation_code(path, expected)
