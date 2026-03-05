"""
Acceptance tests — Step 6 JPEG conversion mode-handling algorithm.

Tests the image-mode conversion logic frozen into HPM.exe
(mirrored in conftest.convert_mode_for_jpeg).  Covers:

  - RGBA images are composited onto a white background → RGB
  - LA (greyscale + alpha) images are composited onto white → RGB
  - P (palette) images are converted through RGBA → RGB on white
  - All other modes (L, RGB, CMYK, etc.) are converted directly to RGB
  - Output mode is always 'RGB'
  - Output dimensions are always preserved
  - White background is correct (255, 255, 255)
  - Fully opaque pixels are preserved through alpha compositing
  - Fully transparent pixels become white through alpha compositing
"""

import pytest
from PIL import Image

from tests.acceptance.conftest import convert_mode_for_jpeg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solid(mode: str, size=(100, 100), colour=None) -> Image.Image:
    """Create a solid-colour image in the given mode."""
    defaults = {
        "RGB":  (200, 100, 50),
        "RGBA": (200, 100, 50, 255),
        "L":    128,
        "LA":   (128, 255),
        "P":    0,
        "CMYK": (0, 128, 255, 0),
    }
    colour = colour if colour is not None else defaults.get(mode, 0)
    return Image.new(mode, size, colour)


# ---------------------------------------------------------------------------
# Output mode is always RGB
# ---------------------------------------------------------------------------

class TestOutputModeIsRGB:
    """convert_mode_for_jpeg must always return an RGB image."""

    @pytest.mark.parametrize("mode", ["RGBA", "LA", "P", "L", "RGB"])
    def test_output_is_rgb(self, mode):
        img = _solid(mode)
        result = convert_mode_for_jpeg(img)
        assert result.mode == "RGB"


# ---------------------------------------------------------------------------
# Output dimensions preserved
# ---------------------------------------------------------------------------

class TestDimensionsPreserved:
    """Output dimensions must match the input exactly."""

    @pytest.mark.parametrize("mode,size", [
        ("RGBA", (800, 600)),
        ("LA",   (400, 300)),
        ("P",    (200, 150)),
        ("L",    (1200, 900)),
        ("RGB",  (640, 480)),
    ])
    def test_dimensions_preserved(self, mode, size):
        img = _solid(mode, size=size)
        result = convert_mode_for_jpeg(img)
        assert result.size == size


# ---------------------------------------------------------------------------
# RGBA → RGB: white-background compositing
# ---------------------------------------------------------------------------

class TestRGBAConversion:

    def test_fully_opaque_pixel_preserved(self):
        """A fully opaque red pixel must survive compositing unchanged."""
        img = Image.new("RGBA", (1, 1), (255, 0, 0, 255))
        result = convert_mode_for_jpeg(img)
        assert result.getpixel((0, 0)) == (255, 0, 0)

    def test_fully_transparent_pixel_becomes_white(self):
        """A fully transparent pixel must become white (background)."""
        img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        result = convert_mode_for_jpeg(img)
        assert result.getpixel((0, 0)) == (255, 255, 255)

    def test_semitransparent_pixel_blended_with_white(self):
        """A 50%-transparent pixel must be blended towards white."""
        img = Image.new("RGBA", (1, 1), (0, 0, 0, 128))
        result = convert_mode_for_jpeg(img)
        r, g, b = result.getpixel((0, 0))
        # All channels must be between 0 and 255, and clearly not black
        assert r > 100
        assert g > 100
        assert b > 100


# ---------------------------------------------------------------------------
# LA → RGB: white-background compositing
# ---------------------------------------------------------------------------

class TestLAConversion:

    def test_fully_opaque_grey_preserved(self):
        """Fully opaque grey must stay grey (all channels equal)."""
        img = Image.new("LA", (1, 1), (200, 255))
        result = convert_mode_for_jpeg(img)
        r, g, b = result.getpixel((0, 0))
        assert r == g == b == 200

    def test_fully_transparent_becomes_white(self):
        """Fully transparent LA pixel must become white."""
        img = Image.new("LA", (1, 1), (0, 0))
        result = convert_mode_for_jpeg(img)
        assert result.getpixel((0, 0)) == (255, 255, 255)


# ---------------------------------------------------------------------------
# P (palette) → RGB: palette is expanded, then composited on white
# ---------------------------------------------------------------------------

class TestPaletteConversion:

    def test_palette_image_converts_to_rgb(self):
        """A plain palette image must produce an RGB output."""
        img = Image.new("P", (10, 10))
        # Set a simple palette entry
        palette = [0] * 768
        palette[0:3] = [255, 0, 0]  # index 0 = red
        img.putpalette(palette)
        result = convert_mode_for_jpeg(img)
        assert result.mode == "RGB"

    def test_palette_dimensions_unchanged(self):
        img = Image.new("P", (50, 30))
        result = convert_mode_for_jpeg(img)
        assert result.size == (50, 30)


# ---------------------------------------------------------------------------
# Direct-conversion modes (L, RGB, CMYK)
# ---------------------------------------------------------------------------

class TestDirectConversionModes:

    def test_rgb_passthrough_unchanged(self):
        """An RGB image must come back as RGB with pixels intact."""
        img = Image.new("RGB", (1, 1), (123, 45, 67))
        result = convert_mode_for_jpeg(img)
        assert result.getpixel((0, 0)) == (123, 45, 67)

    def test_greyscale_expands_to_rgb(self):
        """An L-mode image must expand each channel to the same grey value."""
        img = Image.new("L", (1, 1), 150)
        result = convert_mode_for_jpeg(img)
        r, g, b = result.getpixel((0, 0))
        assert r == g == b == 150
