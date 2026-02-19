"""
Shared fixtures for HPM EXE acceptance tests.

These tests treat HPM.exe as a black box and verify:
  - The compiled artifact is valid and correctly sized
  - The EXE launches without crashing
  - Core processing algorithms (watermark, resize) produce correct outputs
  - All source assets required for bundling are present

pywinauto is intentionally NOT used - GUI interaction is kept out of scope
for this suite. Output-file verification is the primary testing strategy.
"""

import tempfile
import shutil
from pathlib import Path

import pytest
from PIL import Image

# ---------------------------------------------------------------------------
# Repository paths
# ---------------------------------------------------------------------------

FRAMEWORK_DIR = Path(__file__).parent.parent.parent
DIST_EXE      = FRAMEWORK_DIR / "dist" / "HPM.exe"
WATERMARK_PNG = FRAMEWORK_DIR / "gui" / "Copyright_Watermark.png"
EXIFTOOL_EXE  = FRAMEWORK_DIR / "tools" / "exiftool.exe"
APP_ICON      = FRAMEWORK_DIR / "icons" / "app.ico"
LAUNCHER_ICON = FRAMEWORK_DIR / "launcher" / "HPM_icon.png"
HPM_SPEC      = FRAMEWORK_DIR / "HPM.spec"
INIT_PY       = FRAMEWORK_DIR / "__init__.py"
CHANGELOG_MD  = FRAMEWORK_DIR / "CHANGELOG.md"


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def exe_path() -> Path:
    """Path to the compiled HPM.exe in dist/."""
    return DIST_EXE


@pytest.fixture(scope="session")
def watermark_path() -> Path:
    """Path to the Copyright_Watermark.png source asset."""
    return WATERMARK_PNG


@pytest.fixture(scope="session")
def exiftool_path() -> Path:
    """Path to the bundled exiftool.exe."""
    return EXIFTOOL_EXE


@pytest.fixture
def temp_output_dir():
    """Temporary directory, cleaned up after each test."""
    tmp = tempfile.mkdtemp(prefix="hpm_accept_")
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Image factory helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def make_jpeg(temp_output_dir):
    """
    Factory fixture: create a JPEG file of a given size and colour.

    Usage::
        img_path = make_jpeg(800, 533, colour='white', name='landscape.jpg')
    """
    created = []

    def _make(width: int, height: int, colour: str = "white",
               name: str = "test.jpg") -> Path:
        path = temp_output_dir / name
        img = Image.new("RGB", (width, height), colour)
        img.save(path, "JPEG", quality=95)
        created.append(path)
        return path

    return _make


# ---------------------------------------------------------------------------
# Algorithm mirrors
#
# These functions replicate the exact logic frozen inside HPM.exe so that
# acceptance tests can run without launching the GUI.  If the source
# algorithms in step7_dialog.py or step8_dialog.py change, update here too.
# ---------------------------------------------------------------------------

def apply_watermark(img: Image.Image,
                    watermark: Image.Image,
                    opacity: float = 0.30) -> Image.Image:
    """
    Mirror of the watermark scaling algorithm in step8_dialog.py.

    Scales the watermark proportionally to cover the image's larger
    dimension, crops to exact image size, applies opacity, then
    composites onto the image.  Returns an RGB Image.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    img_width, img_height = img.size
    wm_w, wm_h = watermark.size

    # Proportional scale-to-fill + crop (the aspect-ratio fix for issue #49)
    scale = max(img_width, img_height) / max(wm_w, wm_h)
    scaled_wm = watermark.resize(
        (max(img_width, int(wm_w * scale)),
         max(img_height, int(wm_h * scale))),
        Image.Resampling.LANCZOS,
    )
    watermark_resized = scaled_wm.crop((0, 0, img_width, img_height))

    # Apply opacity
    wm_with_opacity = watermark_resized.copy()
    alpha = wm_with_opacity.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    wm_with_opacity.putalpha(alpha)

    # Composite and return as RGB
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(wm_with_opacity, (0, 0), wm_with_opacity)
    result = Image.alpha_composite(img, layer)
    return result.convert("RGB")


def resize_jpeg(img: Image.Image, max_dimension: int = 800) -> Image.Image:
    """
    Mirror of the resize algorithm in step7_dialog.py.

    If the image fits within max_dimension x max_dimension it is returned
    unchanged.  Otherwise it is downscaled proportionally so the longer
    edge equals max_dimension.
    """
    width, height = img.size

    if width <= max_dimension and height <= max_dimension:
        return img.copy()

    if width > height:
        new_width  = max_dimension
        new_height = int((height / width) * max_dimension)
    else:
        new_height = max_dimension
        new_width  = int((width / height) * max_dimension)

    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def is_restricted(copyright_notice: str) -> bool:
    """
    Mirror of the copyright-detection logic in step8_dialog.py.

    Returns True only when 'restricted' is present (case-insensitive)
    and 'unrestricted' is NOT present.
    """
    if not copyright_notice:
        return False
    lower = copyright_notice.lower()
    return "restricted" in lower and "unrestricted" not in lower
