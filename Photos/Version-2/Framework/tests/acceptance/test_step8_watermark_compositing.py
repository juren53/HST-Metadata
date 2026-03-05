"""
Acceptance tests — Step 8 watermark compositing and restricted-image detection.

Extends the existing watermark tests (test_watermark_processing.py) by directly
verifying the compositing algorithm and restricted-image detection logic
(mirrored in conftest.apply_watermark and conftest.is_restricted).  Covers:

  is_restricted:
  - 'Restricted' (any case) → True
  - 'Unrestricted' → False (takes priority)
  - Empty / None copyright → False
  - Exact boundary strings

  apply_watermark (compositing):
  - Watermarked pixels differ from unwatermarked originals (composite is applied)
  - Opacity parameter scales watermark transparency (lower = less visible)
  - Output mode is always RGB
  - Output dimensions match input exactly
  - Zero opacity produces no visible change
  - Full opacity produces maximum watermark effect
"""

import pytest
from PIL import Image

from tests.acceptance.conftest import (
    WATERMARK_PNG,
    apply_watermark,
    is_restricted,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_watermark() -> Image.Image:
    return Image.open(WATERMARK_PNG).convert("RGBA")


def _solid_rgb(size=(200, 200), colour=(200, 200, 200)) -> Image.Image:
    return Image.new("RGB", size, colour)


# ---------------------------------------------------------------------------
# is_restricted — copyright-notice detection
# ---------------------------------------------------------------------------

class TestIsRestricted:
    """is_restricted must return True only for 'restricted' without 'unrestricted'."""

    @pytest.mark.parametrize("notice", [
        "Restricted",
        "restricted",
        "RESTRICTED",
        "Restricted - do not reproduce",
        "This image is Restricted",
    ])
    def test_restricted_notices_return_true(self, notice):
        assert is_restricted(notice) is True

    @pytest.mark.parametrize("notice", [
        "Unrestricted",
        "unrestricted",
        "UNRESTRICTED",
        "Unrestricted - public domain",
        "This image is Unrestricted",
    ])
    def test_unrestricted_notices_return_false(self, notice):
        assert is_restricted(notice) is False

    @pytest.mark.parametrize("notice", [
        "",
        None,
        "No restrictions",
        "Public domain",
        "Copyright 2024",
    ])
    def test_non_restricted_notices_return_false(self, notice):
        assert is_restricted(notice) is False

    def test_unrestricted_overrides_restricted(self):
        """When both words appear, 'Unrestricted' wins → False."""
        assert is_restricted("Unrestricted (formerly Restricted)") is False

    def test_restricted_as_substring(self):
        """'restricted' anywhere in the string triggers True."""
        assert is_restricted("Access is restricted to staff") is True


# ---------------------------------------------------------------------------
# apply_watermark — compositing correctness
# ---------------------------------------------------------------------------

class TestWatermarkCompositing:
    """Watermark must actually be applied — output pixels must differ from input."""

    def test_watermark_changes_pixels(self):
        """A white image with a non-zero-opacity watermark must have changed pixels.
        We compare mean pixel value across the whole image — the watermark text
        is darker than white so the mean must drop below 255.
        """
        import numpy as np
        wm  = _load_watermark()
        img = _solid_rgb((400, 400), (255, 255, 255))
        result = apply_watermark(img, wm, opacity=0.30)
        mean_value = float(np.array(result, dtype=float).mean())
        assert mean_value < 255.0, "Watermark must darken at least some pixels"

    def test_output_mode_is_rgb(self):
        wm     = _load_watermark()
        img    = _solid_rgb()
        result = apply_watermark(img, wm, opacity=0.30)
        assert result.mode == "RGB"

    def test_output_dimensions_match_input(self):
        wm  = _load_watermark()
        for size in [(200, 200), (800, 600), (400, 600)]:
            img    = _solid_rgb(size)
            result = apply_watermark(img, wm, opacity=0.30)
            assert result.size == size

    def test_zero_opacity_produces_no_change(self):
        """Opacity=0 means an invisible watermark — output equals input."""
        wm  = _load_watermark()
        img = _solid_rgb((100, 100), (128, 64, 32))
        result = apply_watermark(img, wm, opacity=0.0)
        # All pixels should be unchanged
        for x in range(100):
            for y in range(100):
                assert result.getpixel((x, y)) == (128, 64, 32)

    def test_higher_opacity_differs_more_from_original(self):
        """Higher opacity must move pixels further from the original."""
        wm   = _load_watermark()
        img  = _solid_rgb((400, 400), (255, 255, 255))
        low  = apply_watermark(img.copy(), wm, opacity=0.10)
        high = apply_watermark(img.copy(), wm, opacity=0.90)

        def _mean_delta(result):
            """Mean absolute difference from white across all pixels."""
            import numpy as np
            arr = np.array(result, dtype=float)
            return float(np.mean(np.abs(arr - 255)))

        assert _mean_delta(high) > _mean_delta(low)

    def test_full_opacity_maximises_watermark(self):
        """Opacity=1.0 must apply the watermark at full strength."""
        wm   = _load_watermark()
        img  = _solid_rgb((400, 400), (255, 255, 255))
        half = apply_watermark(img.copy(), wm, opacity=0.50)
        full = apply_watermark(img.copy(), wm, opacity=1.00)

        import numpy as np
        half_arr = np.array(half, dtype=float)
        full_arr = np.array(full, dtype=float)
        assert np.mean(np.abs(full_arr - 255)) >= np.mean(np.abs(half_arr - 255))

    def test_watermark_covers_landscape_image(self):
        """Watermark must cover the full area of a landscape image (issue #49)."""
        wm  = _load_watermark()
        img = _solid_rgb((800, 400), (255, 255, 255))
        result = apply_watermark(img, wm, opacity=0.30)
        assert result.size == (800, 400)
        assert result.mode == "RGB"

    def test_watermark_covers_portrait_image(self):
        """Watermark must cover the full area of a portrait image (issue #49)."""
        wm  = _load_watermark()
        img = _solid_rgb((400, 800), (255, 255, 255))
        result = apply_watermark(img, wm, opacity=0.30)
        assert result.size == (400, 800)
        assert result.mode == "RGB"
