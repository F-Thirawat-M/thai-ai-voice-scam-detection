from __future__ import annotations

import platform
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")

    try:
        import numpy
        import soundfile
        import torch
    except ImportError as exc:
        print(f"ERROR: missing dependency: {exc}")
        print("Run .\\scripts\\setup.ps1 first.")
        return 1

    print(f"NumPy: {numpy.__version__}")
    print(f"SoundFile: {soundfile.__version__}")
    print(f"PyTorch: {torch.__version__}")
    print(f"PyTorch CUDA runtime: {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"GPU memory: {total_gb:.1f} GB")

    required = [
        PROJECT_ROOT / "external/aasist/models/AASIST.py",
        PROJECT_ROOT / "external/aasist/models/weights/AASIST.pth",
        PROJECT_ROOT / "external/aasist/config/AASIST.conf",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        print("ERROR: AASIST files are missing:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print("AASIST source and pretrained checkpoint: OK")
    if not torch.cuda.is_available():
        print("WARNING: inference can use CPU, but it will be slower.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

