"""
Acceptance tests — JPEG resize algorithm (Step 7).

Tests the proportional resize logic frozen into HPM.exe
(mirrored in conftest.resize_jpeg).  Covers:

  - Images wider than max_dimension are scaled to max_dimension width
  - Images taller than max_dimension are scaled to max_dimension height
  - Aspect ratio is preserved in both cases
  - Images already within bounds are returned unchanged (no upscaling)
  - Output dimensions never exceed max_dimension in either axis
"""

import math

import pytest
from PIL import Image

from tests.acceptance.conftest import resize_jpeg

MAX_DIM = 800


@pytest.mark.acceptance
class TestResizeLandscape:
    """Wide landscape images (width > height) resize correctly."""

    def test_landscape_wider_than_max_is_resized(self):
        """1200 × 800 image must be downscaled."""
        img = Image.new("RGB", (1200, 800))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size != (1200, 800), "Expected resizing but got original size"

    def test_landscape_result_width_equals_max(self):
        """When width > height, result width is exactly max_dimension."""
        img = Image.new("RGB", (1200, 800))
        result = resize_jpeg(img, MAX_DIM)
        assert result.width == MAX_DIM, \
            f"Expected width {MAX_DIM}, got {result.width}"

    def test_landscape_aspect_ratio_preserved(self):
        """Landscape resize preserves the width/height ratio (±1 px rounding)."""
        orig = Image.new("RGB", (1200, 800))
        result = resize_jpeg(orig, MAX_DIM)
        orig_ratio   = orig.width / orig.height
        result_ratio = result.width / result.height
        assert math.isclose(orig_ratio, result_ratio, rel_tol=0.01), (
            f"Aspect ratio changed: {orig_ratio:.4f} → {result_ratio:.4f}"
        )

    def test_wide_landscape_fits_in_max(self):
        """2400 × 1080 image fits within 800 × 800 after resize."""
        img = Image.new("RGB", (2400, 1080))
        result = resize_jpeg(img, MAX_DIM)
        assert result.width <= MAX_DIM
        assert result.height <= MAX_DIM


@pytest.mark.acceptance
class TestResizePortrait:
    """Tall portrait images (height > width) resize correctly."""

    def test_portrait_taller_than_max_is_resized(self):
        """800 × 1200 image must be downscaled."""
        img = Image.new("RGB", (800, 1200))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size != (800, 1200), "Expected resizing but got original size"

    def test_portrait_result_height_equals_max(self):
        """When height > width, result height is exactly max_dimension."""
        img = Image.new("RGB", (800, 1200))
        result = resize_jpeg(img, MAX_DIM)
        assert result.height == MAX_DIM, \
            f"Expected height {MAX_DIM}, got {result.height}"

    def test_portrait_aspect_ratio_preserved(self):
        """Portrait resize preserves the width/height ratio (±1 px rounding)."""
        orig = Image.new("RGB", (800, 1200))
        result = resize_jpeg(orig, MAX_DIM)
        orig_ratio   = orig.width / orig.height
        result_ratio = result.width / result.height
        assert math.isclose(orig_ratio, result_ratio, rel_tol=0.01), (
            f"Aspect ratio changed: {orig_ratio:.4f} → {result_ratio:.4f}"
        )


@pytest.mark.acceptance
class TestResizeSquare:
    """Square images resize using the same scale factor on both axes."""

    def test_large_square_is_resized(self):
        """1000 × 1000 square is scaled to 800 × 800."""
        img = Image.new("RGB", (1000, 1000))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size == (MAX_DIM, MAX_DIM), \
            f"Expected {MAX_DIM}×{MAX_DIM}, got {result.size}"

    def test_large_square_stays_square(self):
        """Resizing a square image produces a square result."""
        img = Image.new("RGB", (1000, 1000))
        result = resize_jpeg(img, MAX_DIM)
        assert result.width == result.height


@pytest.mark.acceptance
class TestResizeNoUpscaling:
    """Images already within bounds are never enlarged."""

    def test_small_image_not_upscaled(self):
        """400 × 300 image is returned unchanged."""
        img = Image.new("RGB", (400, 300))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size == (400, 300), \
            f"Small image was modified: {result.size}"

    def test_exact_max_width_not_resized(self):
        """800 × 600 image already fits — returned unchanged."""
        img = Image.new("RGB", (800, 600))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size == (800, 600)

    def test_exact_max_height_not_resized(self):
        """600 × 800 image already fits — returned unchanged."""
        img = Image.new("RGB", (600, 800))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size == (600, 800)

    def test_exact_square_max_not_resized(self):
        """800 × 800 image already at exact limit — returned unchanged."""
        img = Image.new("RGB", (800, 800))
        result = resize_jpeg(img, MAX_DIM)
        assert result.size == (800, 800)


@pytest.mark.acceptance
class TestResizeOutputBounds:
    """All resized outputs stay within max_dimension on both axes."""

    @pytest.mark.parametrize("w,h", [
        (1600, 1067),  # landscape 3:2
        (1067, 1600),  # portrait  2:3
        (1200, 1200),  # square
        (3840, 2160),  # 4K landscape
        (2160, 3840),  # 4K portrait
    ])
    def test_output_fits_within_max_dimension(self, w, h):
        """resize_jpeg output is always within max_dimension × max_dimension."""
        img = Image.new("RGB", (w, h))
        result = resize_jpeg(img, MAX_DIM)
        assert result.width  <= MAX_DIM, \
            f"{w}×{h} → {result.size}: width exceeds {MAX_DIM}"
        assert result.height <= MAX_DIM, \
            f"{w}×{h} → {result.size}: height exceeds {MAX_DIM}"
