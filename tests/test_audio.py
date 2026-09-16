import numpy as np

from thai_spoof.audio import repeat_or_trim


def test_repeat_short_waveform() -> None:
    waveform = np.asarray([1.0, 2.0, 3.0], dtype=np.float32)
    result = repeat_or_trim(waveform, 8)
    np.testing.assert_array_equal(result, [1, 2, 3, 1, 2, 3, 1, 2])


def test_trim_long_waveform() -> None:
    waveform = np.arange(10, dtype=np.float32)
    result = repeat_or_trim(waveform, 4)
    np.testing.assert_array_equal(result, [0, 1, 2, 3])


def test_empty_waveform_is_rejected() -> None:
    try:
        repeat_or_trim(np.asarray([], dtype=np.float32))
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("empty waveform should raise ValueError")

