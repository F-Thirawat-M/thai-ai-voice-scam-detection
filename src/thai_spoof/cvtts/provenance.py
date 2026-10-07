"""Verify historical code hashes across Git's LF-to-CRLF checkout conversion."""

import hashlib
from pathlib import Path


def verify_preparation_code(path: Path, expected_sha256: str) -> dict[str, str]:
    """Accept exact bytes or CRLF->LF only; never ignore content changes.

    Existing canonical reports were produced from LF source before Git checkout.
    Audio/manifest hashes remain strictly byte-exact; this is for code ONLY.
    """
    content = path.read_bytes()
    raw_hash = hashlib.sha256(content).hexdigest()
    lf_hash = hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()
    if raw_hash == expected_sha256:
        mode = "exact"
    elif lf_hash == expected_sha256:
        mode = "CRLF_to_LF_only"
    else:
        raise ValueError(f"preparation code changed beyond newline conversion: {path}")
    return {"expected_sha256": expected_sha256, "actual_file_sha256": raw_hash,
            "LF_normalized_sha256": lf_hash, "verification": mode}
