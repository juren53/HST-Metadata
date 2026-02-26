"""
Acceptance tests — source asset readiness for bundling.

Verifies that every file listed in HPM.spec's `datas` section exists in the
source tree and, where applicable, is a valid/executable binary.  A failure
here means the next PyInstaller build will silently omit the asset.
"""

import subprocess

import pytest

from tests.acceptance.conftest import (
    WATERMARK_PNG,
    EXIFTOOL_EXE,
    APP_ICON,
    LAUNCHER_ICON,
    HPM_SPEC,
    FRAMEWORK_DIR,
)


@pytest.mark.acceptance
class TestWatermarkAsset:
    """Copyright_Watermark.png is present and a valid PNG image."""

    def test_watermark_exists(self):
        assert WATERMARK_PNG.exists(), \
            f"Missing: {WATERMARK_PNG}"

    def test_watermark_is_valid_image(self):
        """PIL can open the watermark without errors."""
        from PIL import Image
        with Image.open(WATERMARK_PNG) as img:
            img.verify()   # raises if file is corrupt

    def test_watermark_is_png(self):
        """Watermark file has a .png extension."""
        assert WATERMARK_PNG.suffix.lower() == ".png"


@pytest.mark.acceptance
class TestExifToolAsset:
    """tools/exiftool.exe is present and executable."""

    def test_exiftool_exists(self):
        assert EXIFTOOL_EXE.exists(), (
            f"Missing: {EXIFTOOL_EXE} — "
            "place exiftool.exe in the tools/ directory before building."
        )

    def test_exiftool_is_file(self):
        assert EXIFTOOL_EXE.is_file()

    def test_exiftool_runs_and_returns_version(self):
        """
        tools/exiftool.exe -ver exits with code 0 and prints a version
        number.  This confirms the binary is not corrupt and is the
        correct architecture for the host machine.
        """
        result = subprocess.run(
            [str(EXIFTOOL_EXE), "-ver"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, \
            f"exiftool -ver exited {result.returncode}: {result.stderr}"
        version_output = result.stdout.strip()
        assert version_output, "exiftool -ver produced no output"
        # Version string looks like "12.60" or "13.05"
        assert "." in version_output, \
            f"Unexpected exiftool version output: '{version_output}'"


@pytest.mark.acceptance
class TestIconAssets:
    """Application icon files exist in the expected locations."""

    def test_app_icon_exists(self):
        """icons/app.ico referenced in HPM.spec `icon` field."""
        assert APP_ICON.exists(), \
            f"Missing app icon: {APP_ICON}"

    def test_app_icon_is_ico(self):
        assert APP_ICON.suffix.lower() == ".ico"

    def test_launcher_icon_exists(self):
        """launcher/HPM_icon.png referenced in HPM.spec datas."""
        assert LAUNCHER_ICON.exists(), \
            f"Missing launcher icon: {LAUNCHER_ICON}"


@pytest.mark.acceptance
class TestSpecDatasConsistency:
    """Every path listed in HPM.spec datas exists on disk."""

    def _parse_datas_paths(self):
        """
        Extract source paths from the `datas = [...]` block in HPM.spec.
        Returns a list of Path objects relative to FRAMEWORK_DIR.
        """
        import re
        text = HPM_SPEC.read_text(encoding="utf-8")
        # Match quoted first elements of tuples: ('path/to/file', 'dest')
        raw_paths = re.findall(r"\(\s*['\"]([^'\"]+)['\"]", text)
        # Filter to lines that look like file/directory paths (not dest labels)
        return [
            FRAMEWORK_DIR / p for p in raw_paths
            if "/" in p or "\\" in p
        ]

    def test_all_spec_data_sources_exist(self):
        """Every source path in HPM.spec datas is present on disk."""
        missing = [
            str(p) for p in self._parse_datas_paths()
            if not p.exists()
        ]
        assert not missing, (
            "The following HPM.spec datas sources are missing:\n"
            + "\n".join(f"  {m}" for m in missing)
        )
