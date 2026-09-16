from __future__ import annotations

from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


def load_audio(path: str | Path, target_sample_rate: int = 16_000) -> np.ndarray:
    """Load audio as finite, normalized mono float32 at the requested sample rate."""
    audio_path = Path(path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = sf.read(audio_path, dtype="float32", always_2d=True)
    if waveform.shape[0] == 0:
        raise ValueError(f"Audio file is empty: {audio_path}")

    waveform = waveform.mean(axis=1)
    if not np.isfinite(waveform).all():
        raise ValueError(f"Audio contains NaN or infinite samples: {audio_path}")

    if sample_rate != target_sample_rate:
        common = gcd(sample_rate, target_sample_rate)
        waveform = resample_poly(
            waveform,
            target_sample_rate // common,
            sample_rate // common,
        ).astype(np.float32, copy=False)

    peak = float(np.max(np.abs(waveform)))
    if peak > 1.0:
        waveform = waveform / peak
    return waveform.astype(np.float32, copy=False)


def repeat_or_trim(waveform: np.ndarray, num_samples: int = 64_600) -> np.ndarray:
    """Match the deterministic padding used by the upstream AASIST evaluation."""
    if waveform.ndim != 1:
        raise ValueError("waveform must be one-dimensional mono audio")
    if waveform.size == 0:
        raise ValueError("waveform must not be empty")
    if num_samples <= 0:
        raise ValueError("num_samples must be positive")
    if waveform.size >= num_samples:
        return waveform[:num_samples].astype(np.float32, copy=False)

    repeats = (num_samples + waveform.size - 1) // waveform.size
    return np.tile(waveform, repeats)[:num_samples].astype(np.float32, copy=False)

