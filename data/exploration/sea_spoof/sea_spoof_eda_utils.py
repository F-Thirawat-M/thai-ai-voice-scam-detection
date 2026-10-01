"""Dataset-specific, read-only helpers for the SEA-Spoof EDA notebook."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf


def normalized_text(value: object) -> str:
    """NFC + whitespace only; do not erase Thai marks or punctuation."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(value))).strip()


def resolve_audio_path(project_root: Path, value: str) -> Path:
    """Refuse manifest paths outside the approved processed-audio directory."""
    root = project_root.resolve()
    allowed = (root / "data/processed/sea_spoof_th/audio").resolve()
    path = Path(value)
    path = (path if path.is_absolute() else root / path).resolve()
    if not path.is_relative_to(allowed):
        raise ValueError("Audio path is outside data/processed/sea_spoof_th/audio")
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_audio_header(task: tuple[Path, str, str, bool]) -> dict:
    """Inspect every local file; optional hash compares file bytes, not identity."""
    root, row_id, value, hash_audio = task
    result = {"row_id": row_id, "audio_status": "error", "audio_error": ""}
    try:
        path = resolve_audio_path(root, value)
        info = sf.info(path)
        if info.frames <= 0 or info.samplerate <= 0:
            raise ValueError("Empty audio or invalid sample rate")
        result.update(
            audio_status="ok",
            frames=int(info.frames),
            actual_sample_rate=int(info.samplerate),
            channels=int(info.channels),
            duration_s=float(info.frames / info.samplerate),
            format=info.format,
            subtype=info.subtype,
            file_bytes=path.stat().st_size,
            audio_sha256=file_sha256(path) if hash_audio else "",
        )
    except (OSError, ValueError, RuntimeError) as exc:
        result["audio_error"] = f"{type(exc).__name__}: {exc}"
    return result


def inspect_signal(task: tuple[Path, str, str, float]) -> dict:
    """Decode whole selected clips in blocks with bounded memory.

    near_zero_fraction is NOT VAD; near_full_scale_fraction is only a warning.
    Mono metrics use channel averaging to match the intended model input.
    """
    root, row_id, value, near_zero_threshold = task
    result = {"row_id": row_id, "signal_status": "error", "signal_error": ""}
    try:
        path = resolve_audio_path(root, value)
        count = zero_count = full_scale_count = crossings = 0
        square_sum = total = peak = 0.0
        previous = None
        with sf.SoundFile(path) as handle:
            for block in handle.blocks(blocksize=65_536, dtype="float64", always_2d=True):
                if not np.isfinite(block).all():
                    raise ValueError("Non-finite waveform samples")
                # Flag per-channel peaks before averaging can hide them.
                full_scale_count += int(np.count_nonzero(np.max(np.abs(block), axis=1) >= 0.999))
                mono = block.mean(axis=1)
                if not mono.size:
                    continue
                crossings += int(np.count_nonzero(mono[1:] * mono[:-1] < 0))
                if previous is not None:
                    crossings += int(previous * mono[0] < 0)
                previous = float(mono[-1])
                count += mono.size
                total += float(mono.sum())
                square_sum += float(np.dot(mono, mono))
                peak = max(peak, float(np.max(np.abs(mono))))
                zero_count += int(np.count_nonzero(np.abs(mono) < near_zero_threshold))
        if count == 0:
            raise ValueError("Empty audio")
        rms = float(np.sqrt(square_sum / count))
        result.update(
            signal_status="ok", decoded_frames=int(count), mono_peak=peak,
            mono_rms=rms, rms_dbfs=float(20 * np.log10(max(rms, 1e-12))),
            dc_offset=total / count, near_zero_fraction=zero_count / count,
            near_full_scale_fraction=full_scale_count / count,
            zero_crossing_rate=crossings / max(count - 1, 1),
            all_zero_mono=bool(peak == 0),
        )
    except (OSError, ValueError, RuntimeError) as exc:
        result["signal_error"] = f"{type(exc).__name__}: {exc}"
    return result


def input_window_summary(frames: int, sample_rate: int, target_samples: int = 64_600,
                         target_sample_rate: int = 16_000) -> dict:
    """Estimate crop/pad by duration; not an exact resampler simulation."""
    if frames <= 0 or sample_rate <= 0 or target_samples <= 0 or target_sample_rate <= 0:
        raise ValueError("Frame counts and sample rates must be positive")
    duration = frames / sample_rate
    window = target_samples / target_sample_rate
    return {
        "window_action": "trim" if duration > window else "repeat_pad" if duration < window else "exact",
        "retained_original_fraction": min(duration, window) / duration,
        "padded_fraction_of_input": max(window - duration, 0) / window,
    }
