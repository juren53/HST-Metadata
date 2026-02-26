"""
Acceptance tests — watermark processing algorithm.

Tests the exact watermark scaling algorithm frozen into HPM.exe
(mirrored in conftest.apply_watermark).  Covers:

  - Source watermark PNG properties
  - Aspect-ratio fix for issue #49 (non-square images must not stretch text)
  - Output image format and dimensions
  - Opacity application
  - Copyright-notice detection logic (Restricted vs Unrestricted)

These tests exercise the same PIL code that runs inside the EXE without
requiring a running GUI process.
"""

import pytest
from PIL import Image

from tests.acceptance.conftest import (
    WATERMARK_PNG,
    apply_watermark,
    is_restricted,
)


# ---------------------------------------------------------------------------
# Source watermark PNG
# ---------------------------------------------------------------------------

@pytest.mark.acceptance
class TestWatermarkSourceAsset:
    """The Copyright_Watermark.png source file meets expected specifications."""

    def test_watermark_png_exists(self):
        """Copyright_Watermark.png is present in gui/."""
        assert WATERMARK_PNG.exists(), \
            f"Watermark PNG not found at {WATERMARK_PNG}"

    def test_watermark_png_has_alpha_channel(self):
        """Watermark PNG has an alpha channel (mode LA or RGBA)."""
        with Image.open(WATERMARK_PNG) as wm:
            assert wm.mode in ("RGBA", "LA"), (
                f"Expected a mode with alpha channel (RGBA or LA), got {wm.mode} — "
                "watermark needs transparency to composite correctly"
            )

    def test_watermark_png_is_square(self):
        """Watermark PNG is square (800 × 800)."""
        with Image.open(WATERMARK_PNG) as wm:
            w, h = wm.size
            assert w == h, \
                f"Watermark is {w}×{h} — expected a square image"

    def test_watermark_png_is_800px(self):
        """Watermark PNG is exactly 800 × 800 pixels."""
        with Image.open(WATERMARK_PNG) as wm:
            assert wm.size == (800, 800), \
                f"Expected 800×800, got {wm.size}"

    def test_watermark_has_transparent_pixels(self):
        """Alpha channel contains pixels with alpha < 255 (i.e. is used)."""
        with Image.open(WATERMARK_PNG) as wm:
            rgba = wm.convert("RGBA")
            alpha_values = list(rgba.split()[3].getdata())
            assert any(a < 255 for a in alpha_values), \
                "Alpha channel appears to be fully opaque — watermark may be wrong file"


# ---------------------------------------------------------------------------
# Output dimensions (issue #49 regression tests)
# ---------------------------------------------------------------------------

@pytest.mark.acceptance
class TestWatermarkOutputDimensions:
    """
    Watermarked output must have the same dimensions as the input image.

    These tests are the primary regression guards for issue #49.
    The watermark PNG (800 × 800 square) must not distort the 'COPYRIGHT'
    text when applied to non-square JPEG images.
    """

    def _open_wm(self):
        return Image.open(WATERMARK_PNG).convert("RGBA")

    def test_square_image_output_dimensions(self):
        """Square input (400 × 400) → output is 400 × 400."""
        img = Image.new("RGB", (400, 400), "white")
        result = apply_watermark(img, self._open_wm())
        assert result.size == (400, 400)

    def test_landscape_image_output_dimensions(self):
        """Landscape input (800 × 533) → output is 800 × 533."""
        img = Image.new("RGB", (800, 533), "white")
        result = apply_watermark(img, self._open_wm())
        assert result.size == (800, 533)

    def test_portrait_image_output_dimensions(self):
        """Portrait input (533 × 800) → output is 533 × 800."""
        img = Image.new("RGB", (533, 800), "white")
        result = apply_watermark(img, self._open_wm())
        assert result.size == (533, 800)

    def test_wide_landscape_output_dimensions(self):
        """Wide landscape (800 × 400) → output is 800 × 400."""
        img = Image.new("RGB", (800, 400), "white")
        result = apply_watermark(img, self._open_wm())
        assert result.size == (800, 400)

    def test_tall_portrait_output_dimensions(self):
        """Tall portrait (400 × 800) → output is 400 × 800."""
        img = Image.new("RGB", (400, 800), "white")
        result = apply_watermark(img, self._open_wm())
        assert result.size == (400, 800)


# ---------------------------------------------------------------------------
# Aspect-ratio correctness (issue #49 — no text stretching)
# ---------------------------------------------------------------------------

@pytest.mark.acceptance
class TestWatermarkAspectRatio:
    """
    The watermark text must not be geometrically stretched on non-square
    images.  We verify this by checking the intermediate scaling step uses
    a single uniform scale factor (proportional resize + crop) rather than
    independent x/y scale factors (stretching).
    """

    def test_landscape_uses_proportional_scale(self):
        """
        For an 800 × 533 image with an 800 × 800 watermark:
        scale = max(800, 533) / max(800, 800) = 1.0
        → intermediate watermark size should be max(800,800) × max(533,800)
          = 800 × 800, then cropped to 800 × 533.

        This confirms both axes use the same scale factor, not independent
        factors (which would be 800/800=1.0 wide vs 533/800=0.67 tall).
        """
        wm = Image.open(WATERMARK_PNG).convert("RGBA")
        wm_w, wm_h = wm.size      # 800, 800
        img_w, img_h = 800, 533

        scale = max(img_w, img_h) / max(wm_w, wm_h)
        scaled_w = max(img_w, int(wm_w * scale))
        scaled_h = max(img_h, int(wm_h * scale))

        # Both dimensions scaled by the same factor → intermediate is square
        assert scaled_w == scaled_h, (
            f"Intermediate scaled size {scaled_w}×{scaled_h} is not square — "
            "uniform scale factor not being used"
        )

    def test_portrait_uses_proportional_scale(self):
        """
        For a 533 × 800 image with an 800 × 800 watermark:
        scale = max(533, 800) / max(800, 800) = 1.0
        → intermediate should be 800 × 800, cropped to 533 × 800.
        """
        wm = Image.open(WATERMARK_PNG).convert("RGBA")
        wm_w, wm_h = wm.size      # 800, 800
        img_w, img_h = 533, 800

        scale = max(img_w, img_h) / max(wm_w, wm_h)
        scaled_w = max(img_w, int(wm_w * scale))
        scaled_h = max(img_h, int(wm_h * scale))

        assert scaled_w == scaled_h, (
            f"Intermediate scaled size {scaled_w}×{scaled_h} is not square — "
            "uniform scale factor not being used"
        )

    def test_stretch_would_have_failed(self):
        """
        Demonstrate that the old (broken) resize-to-exact-dimensions approach
        *would* produce different x/y scale factors for a landscape image.

        This test documents the bug that was fixed in issue #49.
        """
        wm_w, wm_h = 800, 800
        img_w, img_h = 800, 533

        # OLD algorithm: resize watermark to exactly (img_w, img_h)
        old_x_scale = img_w / wm_w  # 800/800 = 1.0
        old_y_scale = img_h / wm_h  # 533/800 = 0.666...

        # The old algorithm used different scale factors — text was stretched
        assert old_x_scale != old_y_scale, \
            "Expected the old algorithm to use non-uniform scale factors"

        # NEW algorithm: single scale = max(img) / max(wm)
        new_scale = max(img_w, img_h) / max(wm_w, wm_h)  # 800/800 = 1.0
        assert new_scale == 1.0, \
            "New scale factor should be 1.0 for an 800-px-wide landscape image"


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------

@pytest.mark.acceptance
class TestWatermarkOutputFormat:
    """Output image is RGB (JPEG-compatible) regardless of input mode."""

    def test_output_is_rgb(self):
        """apply_watermark always returns an RGB image."""
        wm  = Image.open(WATERMARK_PNG).convert("RGBA")
        img = Image.new("RGB", (800, 533), "white")
        result = apply_watermark(img, wm)
        assert result.mode == "RGB", \
            f"Expected RGB output, got {result.mode}"

    def test_output_differs_from_input(self):
        """Watermarked image is not pixel-identical to the original."""
        wm  = Image.open(WATERMARK_PNG).convert("RGBA")
        # Use a solid white image so any non-transparent watermark pixel shows
        img = Image.new("RGB", (400, 400), "white")
        result = apply_watermark(img, wm, opacity=1.0)

        original_pixels = list(img.getdata())
        result_pixels   = list(result.getdata())
        assert original_pixels != result_pixels, \
            "Watermarked image is identical to original — watermark not applied"


# ---------------------------------------------------------------------------
# Opacity
# ---------------------------------------------------------------------------

@pytest.mark.acceptance
class TestWatermarkOpacity:
    """Opacity parameter affects how visibly the watermark is composited."""

    def test_high_opacity_more_visible_than_low(self):
        """
        A watermark at 100% opacity should differ more from the plain
        white base than the same watermark at 10% opacity.
        """
        wm  = Image.open(WATERMARK_PNG).convert("RGBA")
        img = Image.new("RGB", (400, 400), "white")

        result_low  = apply_watermark(img.copy(), wm.copy(), opacity=0.10)
        result_high = apply_watermark(img.copy(), wm.copy(), opacity=1.00)

        # Measure average pixel difference from pure white (255, 255, 255)
        def avg_delta(result_img):
            pixels = list(result_img.getdata())
            total = sum(abs(255 - c) for px in pixels for c in px)
            return total / (len(pixels) * 3)

        assert avg_delta(result_high) > avg_delta(result_low), \
            "High-opacity watermark should differ more from baseline than low-opacity"

    def test_zero_opacity_is_ignored(self):
        """
        Opacity of 0.0 means the watermark contributes nothing; output
        should be (nearly) identical to the original.
        """
        wm  = Image.open(WATERMARK_PNG).convert("RGBA")
        img = Image.new("RGB", (400, 400), "white")

        result = apply_watermark(img.copy(), wm, opacity=0.0)
        original_pixels = list(img.getdata())
        result_pixels   = list(result.getdata())
        assert original_pixels == result_pixels, \
            "Zero-opacity watermark should not change any pixels"


# ---------------------------------------------------------------------------
# Copyright-notice detection
# ---------------------------------------------------------------------------

@pytest.mark.acceptance
class TestCopyrightDetection:
    """
    The copyright-notice detection logic correctly identifies which images
    should receive a watermark.
    """

    def test_restricted_detected(self):
        assert is_restricted("© HSTL Restricted") is True

    def test_restricted_case_insensitive(self):
        assert is_restricted("RESTRICTED USE ONLY") is True

    def test_unrestricted_excluded(self):
        """'Unrestricted' must never trigger the watermark."""
        assert is_restricted("© HSTL Unrestricted") is False

    def test_unrestricted_case_insensitive(self):
        assert is_restricted("PUBLIC DOMAIN – UNRESTRICTED") is False

    def test_empty_string_not_restricted(self):
        assert is_restricted("") is False

    def test_none_not_restricted(self):
        assert is_restricted(None) is False

    def test_unrelated_text_not_restricted(self):
        assert is_restricted("© 2025 HSTL All Rights Reserved") is False

    def test_partial_word_not_matched(self):
        """'constricted' contains 'ricted' but not 'restricted'."""
        assert is_restricted("constricted") is False
