"""
Acceptance tests — Step 4 TIFF bit depth conversion algorithms.

Tests the bit-depth detection and pixel-scaling logic frozen into HPM.exe
(mirrored in conftest.is_16bit_tiff, scale_16bit_to_8bit, detect_converted_mode).
Covers:

  is_16bit_tiff:
  - BitsPerSample values that are 16-bit → True
  - BitsPerSample values that are 8-bit → False
  - Ambiguous / mixed strings → correct behaviour

  scale_16bit_to_8bit:
  - Scaling formula: output = (input / 256).astype(uint8)
  - Boundary values (0, 65535, midpoints)
  - All image modes (grayscale 2D, RGB 3-channel, RGBA 4-channel)
  - Output dtype is uint8

  detect_converted_mode:
  - 2D array → 'L' (grayscale)
  - 3D array with 3 channels → 'RGB'
  - 3D array with 4 channels → 'RGBA'
"""

import numpy as np
import pytest

from tests.acceptance.conftest import (
    detect_converted_mode,
    is_16bit_tiff,
    scale_16bit_to_8bit,
)


# ---------------------------------------------------------------------------
# is_16bit_tiff — BitsPerSample detection
# ---------------------------------------------------------------------------

class TestIs16BitTiff:
    """is_16bit_tiff returns True only when BitsPerSample indicates 16-bit."""

    @pytest.mark.parametrize("bits_str", [
        "16",
        "16 16 16",       # RGB channels
        "16 16 16 16",    # RGBA channels
        " 16 ",           # whitespace
    ])
    def test_16bit_strings_are_true(self, bits_str):
        assert is_16bit_tiff(bits_str) is True

    @pytest.mark.parametrize("bits_str", [
        "8",
        "8 8 8",
        "8 8 8 8",
        "",
        "16 8 16",   # contains both 16 and 8 → ambiguous, treated as NOT 16-bit
        "32",
        "4",
    ])
    def test_non_16bit_strings_are_false(self, bits_str):
        assert is_16bit_tiff(bits_str) is False

    def test_empty_string_is_false(self):
        assert is_16bit_tiff("") is False

    def test_mixed_channels_with_8_is_false(self):
        """If any channel reports 8 bits the image is not treated as 16-bit."""
        assert is_16bit_tiff("16 8 16") is False


# ---------------------------------------------------------------------------
# scale_16bit_to_8bit — pixel-value scaling
# ---------------------------------------------------------------------------

class TestScale16BitTo8Bit:
    """scale_16bit_to_8bit must implement (arr / 256).astype(uint8) exactly."""

    def test_output_dtype_is_uint8(self):
        arr = np.array([[0, 65535]], dtype=np.uint16)
        result = scale_16bit_to_8bit(arr)
        assert result.dtype == np.uint8

    def test_zero_maps_to_zero(self):
        arr = np.array([[0]], dtype=np.uint16)
        assert scale_16bit_to_8bit(arr)[0, 0] == 0

    def test_max_16bit_maps_to_255(self):
        arr = np.array([[65535]], dtype=np.uint16)
        assert scale_16bit_to_8bit(arr)[0, 0] == 255

    def test_midpoint_256_maps_to_1(self):
        arr = np.array([[256]], dtype=np.uint16)
        assert scale_16bit_to_8bit(arr)[0, 0] == 1

    def test_midpoint_512_maps_to_2(self):
        arr = np.array([[512]], dtype=np.uint16)
        assert scale_16bit_to_8bit(arr)[0, 0] == 2

    def test_midpoint_32768_maps_to_128(self):
        arr = np.array([[32768]], dtype=np.uint16)
        assert scale_16bit_to_8bit(arr)[0, 0] == 128

    def test_value_255_maps_to_0(self):
        """Values < 256 all map to 0 (integer division)."""
        arr = np.array([[255]], dtype=np.uint16)
        assert scale_16bit_to_8bit(arr)[0, 0] == 0

    def test_shape_preserved_grayscale(self):
        arr = np.zeros((100, 100), dtype=np.uint16)
        result = scale_16bit_to_8bit(arr)
        assert result.shape == (100, 100)

    def test_shape_preserved_rgb(self):
        arr = np.zeros((100, 100, 3), dtype=np.uint16)
        result = scale_16bit_to_8bit(arr)
        assert result.shape == (100, 100, 3)

    def test_shape_preserved_rgba(self):
        arr = np.zeros((100, 100, 4), dtype=np.uint16)
        result = scale_16bit_to_8bit(arr)
        assert result.shape == (100, 100, 4)

    def test_all_pixel_values_in_0_255_range(self):
        rng = np.random.default_rng(42)
        arr = rng.integers(0, 65536, size=(50, 50), dtype=np.uint16)
        result = scale_16bit_to_8bit(arr)
        assert result.min() >= 0
        assert result.max() <= 255

    def test_exact_scaling_formula(self):
        """Verify the formula is division by 256, not by 257 or right-shift."""
        values = np.array([0, 256, 512, 1024, 32768, 65535], dtype=np.uint16)
        result = scale_16bit_to_8bit(values.reshape(1, -1))[0]
        expected = (values / 256).astype(np.uint8)
        np.testing.assert_array_equal(result, expected)


# ---------------------------------------------------------------------------
# detect_converted_mode — image mode selection
# ---------------------------------------------------------------------------

class TestDetectConvertedMode:
    """detect_converted_mode maps numpy array shape to PIL image mode string."""

    def test_2d_array_is_grayscale(self):
        arr = np.zeros((100, 100), dtype=np.uint8)
        assert detect_converted_mode(arr) == "L"

    def test_3d_3channel_is_rgb(self):
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        assert detect_converted_mode(arr) == "RGB"

    def test_3d_4channel_is_rgba(self):
        arr = np.zeros((100, 100, 4), dtype=np.uint8)
        assert detect_converted_mode(arr) == "RGBA"

    def test_3d_1channel_is_unknown(self):
        arr = np.zeros((100, 100, 1), dtype=np.uint8)
        assert detect_converted_mode(arr) == "unknown"

    def test_3d_2channel_is_unknown(self):
        arr = np.zeros((100, 100, 2), dtype=np.uint8)
        assert detect_converted_mode(arr) == "unknown"

    def test_different_sizes_do_not_affect_mode(self):
        """Mode depends only on the number of channels, not image dimensions."""
        for h, w in [(10, 10), (1, 1), (4000, 6000)]:
            assert detect_converted_mode(np.zeros((h, w, 3), dtype=np.uint8)) == "RGB"
