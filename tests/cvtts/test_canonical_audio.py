import io

import numpy as np
import pytest
import soundfile as sf

from thai_spoof.cvtts.audio import encode_float32_wav, read_and_resample, to_mono_resampled


def test_same_rate_preserves_amplitude_and_does_not_alias() -> None:
    source = np.asarray([0.2, -0.5, 1.5, -2.0], dtype=np.float32)
    result = to_mono_resampled(source, 16_000)
    np.testing.assert_array_equal(result, source)
    assert not np.shares_memory(result, source)


def test_stereo_is_mean_downmixed_without_crop_or_pad() -> None:
    source = np.asarray([[0.2, 0.6], [1.0, 0.0], [-0.5, -0.1]], dtype=np.float32)
    result = to_mono_resampled(source, 16_000)
    np.testing.assert_array_equal(result, source.mean(axis=1))
    assert len(result) == len(source)


@pytest.mark.parametrize("source_rate,frames", [(48_000, 960), (24_000, 11), (32_000, 101)])
def test_resample_preserves_duration_to_one_target_sample(source_rate, frames) -> None:
    source = np.sin(2 * np.pi * 1000 * np.arange(frames) / source_rate).astype(np.float32)
    result = to_mono_resampled(source, source_rate)
    assert len(result) == (frames * 16_000 + source_rate - 1) // source_rate
    assert abs(len(result) / 16_000 - frames / source_rate) <= 1 / 16_000 + 1e-12
    assert result.dtype == np.float32 and np.isfinite(result).all()


@pytest.mark.parametrize("source", [np.zeros(0), np.zeros((0, 2)), np.zeros((2, 0)), np.zeros((2, 2, 2))])
def test_invalid_shapes_are_rejected(source) -> None:
    with pytest.raises(ValueError, match="frames and channels"):
        to_mono_resampled(source, 16_000)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_input_is_rejected_before_downmix(value) -> None:
    with pytest.raises(ValueError, match="NaN or infinite"):
        to_mono_resampled(np.asarray([[0.2, value]]), 16_000)


@pytest.mark.parametrize("rate", [0, -1, 16_000.5, True])
def test_invalid_sample_rates_are_rejected(rate) -> None:
    source = np.asarray([0.1, 0.2], dtype=np.float32)
    with pytest.raises(ValueError, match="positive integer"):
        to_mono_resampled(source, rate)
    with pytest.raises(ValueError, match="positive integer"):
        to_mono_resampled(source, 16_000, rate)


@pytest.mark.parametrize("source", [np.zeros(4), np.asarray([[0.5, -0.5], [0.2, -0.2]])])
def test_silence_or_stereo_cancellation_is_rejected(source) -> None:
    with pytest.raises(ValueError, match="silent or nearly zero"):
        to_mono_resampled(source, 16_000)


def test_float_wav_is_reproducible_and_does_not_clip() -> None:
    source = np.asarray([1.5, -2.0, 0.2], dtype=np.float32)
    content = encode_float32_wav(source)
    assert content == encode_float32_wav(source)
    decoded, sr = sf.read(io.BytesIO(content), dtype="float32")
    np.testing.assert_array_equal(decoded, source)
    assert sr == 16_000 and sf.info(io.BytesIO(content)).subtype == "FLOAT"


def test_read_and_resample_reports_source_properties(tmp_path) -> None:
    path = tmp_path / "stereo.wav"
    source = np.full((480, 2), [0.2, 0.4], dtype=np.float32)
    sf.write(path, source, 48_000, subtype="FLOAT")
    audio, measurements = read_and_resample(path)
    assert len(audio) == 160
    assert measurements["source_sample_rate"] == 48_000
    assert measurements["source_channels"] == 2
    assert measurements["source_frames"] == 480
    assert measurements["source_duration_s"] == 0.01
