from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "data/sample/smoke_tone.wav"


def main() -> None:
    """Create a synthetic signal only for checking the end-to-end code path."""
    sample_rate = 16_000
    seconds = 4.2
    time = np.arange(int(sample_rate * seconds), dtype=np.float32) / sample_rate
    envelope = np.minimum(time / 0.1, 1.0) * np.minimum((seconds - time) / 0.1, 1.0)
    waveform = 0.15 * envelope * (
        np.sin(2 * np.pi * 180 * time) + 0.3 * np.sin(2 * np.pi * 360 * time)
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sf.write(OUTPUT, waveform.astype(np.float32), sample_rate)
    print(f"Created technical smoke-test signal: {OUTPUT}")
    print("This is not speech; its model prediction has no research meaning.")


if __name__ == "__main__":
    main()

