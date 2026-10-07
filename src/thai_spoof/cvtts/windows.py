"""Shared, explicit window policy for the clean feasibility pilot."""

from __future__ import annotations

import numpy as np


def select_window(
    waveform: np.ndarray,
    num_samples: int = 64_600,
    *,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, int]:
    """Random inclusive crop with rng; first crop without it; repeat if short.

    Returns a float32 copy and the source start offset (zero for repeats).
    No gain normalization, noise or telephone processing is performed.
    """
    if isinstance(num_samples, bool) or not isinstance(num_samples, int) or num_samples <= 0:
        raise ValueError("num_samples must be a positive integer")
    x = np.asarray(waveform, dtype=np.float32)
    if x.ndim != 1 or not x.size or not np.isfinite(x).all():
        raise ValueError("waveform must be finite, nonempty mono audio")
    if x.size < num_samples:
        result = np.tile(x, (num_samples + x.size - 1) // x.size)[:num_samples]
        start = 0
    else:
        start = int(rng.integers(0, x.size - num_samples + 1)) if rng is not None and x.size > num_samples else 0
        result = x[start:start + num_samples]
    if np.max(np.abs(result)) <= 1e-8:
        raise ValueError("selected window is effectively silent; review the clip")
    return result.astype(np.float32, copy=True), start
