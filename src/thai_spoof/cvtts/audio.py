"""Shared, full-length canonical audio preparation for both detector models.

This is not the model's fixed-window crop/padding step. No peak normalization,
silence trimming, noise, telephone filtering, or amplitude clipping is applied.
"""

from __future__ import annotations

import io
from math import gcd
from numbers import Integral
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.io import wavfile
from scipy.signal import resample_poly

CANONICAL_POLICY = "mono16k_float_fullclip_v1"
TARGET_SAMPLE_RATE = 16_000


def _validate_rate(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
        raise ValueError("sample rate must be a positive integer")
    return int(value)


def _validate_mono(waveform: np.ndarray) -> None:
    if waveform.ndim != 1 or waveform.size == 0:
        raise ValueError("waveform must be nonempty, one-dimensional mono audio")
    if not np.isfinite(waveform).all():
        raise ValueError("waveform contains NaN or infinite samples")
    if float(np.abs(waveform).max()) <= 1e-8:
        raise ValueError("waveform is silent or nearly zero")


def to_mono_resampled(
    waveform: np.ndarray,
    source_sample_rate: int,
    target_sample_rate: int = TARGET_SAMPLE_RATE,
) -> np.ndarray:
    """Mean-downmix channels and resample, keeping the full clip and amplitude."""
    source_rate = _validate_rate(source_sample_rate)
    target_rate = _validate_rate(target_sample_rate)
    audio = np.asarray(waveform, dtype=np.float32)
    if audio.ndim not in (1, 2) or audio.size == 0:
        raise ValueError("audio must have nonempty frames and channels")
    if not np.isfinite(audio).all():
        raise ValueError("audio contains NaN or infinite samples")
    # Copy even for a same-rate mono input: never mutate or alias source data.
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio.copy()
    _validate_mono(mono)
    if source_rate != target_rate:
        common = gcd(source_rate, target_rate)
        mono = resample_poly(mono, target_rate // common, source_rate // common)
    mono = mono.astype(np.float32, copy=False)
    _validate_mono(mono)
    expected_frames = (audio.shape[0] * target_rate + source_rate - 1) // source_rate
    if mono.size != expected_frames:
        raise ValueError("resampler changed full-clip length unexpectedly")
    return mono


def read_and_resample(
    path: str | Path, target_sample_rate: int = TARGET_SAMPLE_RATE
) -> tuple[np.ndarray, dict[str, int | float]]:
    """Decode a source file and return canonical audio plus source measurements."""
    audio, source_rate = sf.read(path, dtype="float32", always_2d=True)
    output = to_mono_resampled(audio, source_rate, target_sample_rate)
    measurements = {
        "source_sample_rate": int(source_rate),
        "source_channels": int(audio.shape[1]),
        "source_frames": int(audio.shape[0]),
        "source_duration_s": audio.shape[0] / source_rate,
        "source_peak": float(np.abs(audio).max()),
    }
    return output, measurements


def encode_float32_wav(waveform: np.ndarray, sample_rate: int = TARGET_SAMPLE_RATE) -> bytes:
    """Produce deterministic FLOAT WAV bytes without clipping/PCM16 quantization."""
    rate = _validate_rate(sample_rate)
    audio = np.asarray(waveform, dtype=np.float32)
    _validate_mono(audio)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio)
    content = buffer.getvalue()
    decoded, decoded_rate = sf.read(io.BytesIO(content), dtype="float32")
    if decoded_rate != rate or not np.array_equal(decoded, audio):
        raise ValueError("FLOAT WAV roundtrip changed the waveform")
    return content
