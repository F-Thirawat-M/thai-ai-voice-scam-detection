from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from data.exploration.sea_spoof.sea_spoof_eda_utils import (
    inspect_audio_header, inspect_signal, input_window_summary,
    normalized_text, resolve_audio_path,
)


def make_audio(root: Path, samples: np.ndarray) -> Path:
    path = root / "data/processed/sea_spoof_th/audio/validation/example.flac"
    path.parent.mkdir(parents=True)
    sf.write(path, samples, 16_000, subtype="PCM_16")
    return path


def test_headers_signal_and_hash(tmp_path):
    waveform = 0.25 * np.sin(2 * np.pi * 440 * np.arange(16_000) / 16_000)
    path = make_audio(tmp_path, waveform)
    task = (tmp_path, "row-1", path.relative_to(tmp_path).as_posix())
    header = inspect_audio_header((*task, True))
    signal = inspect_signal((*task, 1e-4))
    assert header["audio_status"] == signal["signal_status"] == "ok"
    assert header["duration_s"] == 1
    assert header["channels"] == 1
    assert len(header["audio_sha256"]) == 64
    assert signal["decoded_frames"] == 16_000
    assert signal["mono_rms"] == pytest.approx(0.25 / np.sqrt(2), abs=1e-4)
    assert not signal["all_zero_mono"]


def test_silence_and_errors_are_explicit(tmp_path):
    path = make_audio(tmp_path, np.zeros(1_000))
    signal = inspect_signal((tmp_path, "silent", str(path), 1e-4))
    assert signal["all_zero_mono"]
    assert signal["near_zero_fraction"] == 1
    missing = path.with_name("missing.flac")
    result = inspect_audio_header((tmp_path, "missing", str(missing), False))
    assert result["audio_status"] == "error"
    assert result["audio_error"]


def test_audio_paths_cannot_escape_processed_root(tmp_path):
    with pytest.raises(ValueError, match="outside"):
        resolve_audio_path(tmp_path, "../outside.wav")


def test_text_normalization_and_window_scope():
    assert normalized_text("  ภาษาไทย\n  ทดสอบ ") == "ภาษาไทย ทดสอบ"
    assert normalized_text(None) == ""
    assert input_window_summary(64_600, 16_000)["window_action"] == "exact"
    assert input_window_summary(160_000, 16_000)["retained_original_fraction"] == pytest.approx(0.40375)
    assert input_window_summary(16_000, 16_000)["window_action"] == "repeat_pad"
    with pytest.raises(ValueError):
        input_window_summary(0, 16_000)
