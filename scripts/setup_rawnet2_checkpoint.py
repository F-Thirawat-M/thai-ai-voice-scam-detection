"""Download and verify the official pretrained RawNet2 checkpoint."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints/rawnet2"
ARCHIVE = CHECKPOINT_DIR / "pre_trained_DF_RawNet2.zip"
CHECKPOINT = CHECKPOINT_DIR / "pre_trained_DF_RawNet2.pth"
ARCHIVE_SHA256 = "db0f3e4ba6fdba23752e6e57e1507cd5b3de344d6a36c9699d4439be142dfbf5"
CHECKPOINT_SHA256 = "52d8ad5f524a0f600c7c876d7a157a8f06c44a03504d0b2795c852f5e42c9127"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    if CHECKPOINT.is_file() and sha256(CHECKPOINT) == CHECKPOINT_SHA256:
        print(f"RawNet2 checkpoint ready: {CHECKPOINT}")
        return

    if not ARCHIVE.is_file():
        subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts/download_rawnet2_checkpoint.py"),
                "--output",
                str(ARCHIVE),
            ],
            check=True,
        )
    if sha256(ARCHIVE) != ARCHIVE_SHA256:
        raise ValueError(f"RawNet2 archive checksum mismatch: {ARCHIVE}")

    with zipfile.ZipFile(ARCHIVE) as package:
        matches = [
            item
            for item in package.infolist()
            if not item.is_dir() and Path(item.filename).name == CHECKPOINT.name
        ]
        if len(matches) != 1:
            raise ValueError("RawNet2 archive must contain exactly one checkpoint")
        temporary = CHECKPOINT.with_suffix(".pth.tmp")
        try:
            with package.open(matches[0]) as source, temporary.open("wb") as target:
                shutil.copyfileobj(source, target)
            if sha256(temporary) != CHECKPOINT_SHA256:
                raise ValueError("RawNet2 checkpoint checksum mismatch")
            temporary.replace(CHECKPOINT)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"RawNet2 checkpoint ready: {CHECKPOINT}")


if __name__ == "__main__":
    main()
