import numpy as np
import pytest

from thai_spoof.cvtts.windows import select_window


def test_short_audio_repeats_without_zero_padding():
    actual, start = select_window(np.array([0.2, -0.3]), 5)
    np.testing.assert_array_equal(actual, np.array([0.2, -0.3, 0.2, -0.3, 0.2], dtype=np.float32))
    assert start == 0


def test_equal_length_needs_no_random_draw_and_returns_copy():
    class NoDraw:
        def integers(self, *args):
            raise AssertionError("no draw expected")
    x = np.ones(6, dtype=np.float32)
    result, start = select_window(x, 6, rng=NoDraw())
    assert start == 0 and not np.shares_memory(x, result)


def test_random_crop_can_include_last_start():
    class LastStart:
        def integers(self, low, high):
            assert (low, high) == (0, 4)
            return high - 1
    result, start = select_window(np.arange(1, 9), 5, rng=LastStart())
    assert start == 3
    np.testing.assert_array_equal(result, [4, 5, 6, 7, 8])


def test_dev_uses_first_window_and_preserves_gain():
    result, start = select_window(np.array([2, 3, 4, 5]), 2)
    np.testing.assert_array_equal(result, [2, 3])
    assert start == 0


@pytest.mark.parametrize("x", [[], [[1]], [np.nan], [np.inf], [0, 0]])
def test_invalid_or_silent_window_rejected(x):
    with pytest.raises(ValueError):
        select_window(np.asarray(x), 2)


@pytest.mark.parametrize("size", [0, -1, True, 4.5])
def test_invalid_window_size_rejected(size):
    with pytest.raises(ValueError):
        select_window(np.ones(5), size)


def test_silent_first_window_does_not_silently_select_another_region():
    with pytest.raises(ValueError, match="silent"):
        select_window(np.array([0, 0, 1, 1]), 2)


def test_seeded_crop_reproducible():
    a, start_a = select_window(np.arange(1, 100), 20, rng=np.random.default_rng(42))
    b, start_b = select_window(np.arange(1, 100), 20, rng=np.random.default_rng(42))
    assert start_a == start_b
    np.testing.assert_array_equal(a, b)
