"""Exclusive, immutable writes for derived experiment artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path


def write_immutable_artifacts(files: Mapping[Path, bytes]) -> int:
    """Check all conflicts first, then create missing files without overwriting.

    Returns the number of new files. A concurrent writer can still interrupt
    the batch, but exclusive creation never overwrites that writer's files.
    """
    for path, content in files.items():
        if path.exists() and path.read_bytes() != content:
            raise FileExistsError(f"Existing artifact differs; use a new version: {path}")
    created = 0
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(content)
            created += 1
    return created
