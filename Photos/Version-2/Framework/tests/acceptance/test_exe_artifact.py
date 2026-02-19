"""
Acceptance tests — EXE artifact validation.

Verifies the compiled HPM.exe and related release artefacts are correct
without launching the executable.  These tests are fast (file-system only).
"""

import re
from pathlib import Path

import pytest

from tests.acceptance.conftest import (
    DIST_EXE, INIT_PY, CHANGELOG_MD, HPM_SPEC, WATERMARK_PNG
)


@pytest.mark.acceptance
class TestExeFile:
    """The compiled executable exists and is a plausible size."""

    def test_exe_exists(self, exe_path):
        """dist/HPM.exe is present."""
        assert exe_path.exists(), f"HPM.exe not found at {exe_path}"

    def test_exe_is_file(self, exe_path):
        """dist/HPM.exe is a regular file, not a directory."""
        assert exe_path.is_file()

    def test_exe_min_size_mb(self, exe_path):
        """HPM.exe is at least 50 MB — guards against a failed/truncated build."""
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        assert size_mb >= 50, f"HPM.exe is only {size_mb:.1f} MB — build may be incomplete"

    def test_exe_max_size_mb(self, exe_path):
        """HPM.exe is no larger than 300 MB — guards against accidental bloat."""
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        assert size_mb <= 300, f"HPM.exe is {size_mb:.1f} MB — unexpectedly large"


@pytest.mark.acceptance
class TestVersionConsistency:
    """Version string is consistent across __init__.py and CHANGELOG.md."""

    def _read_version(self) -> str:
        """Extract __version__ from __init__.py."""
        text = INIT_PY.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
        assert match, "__version__ not found in __init__.py"
        return match.group(1)

    def test_version_defined_in_init(self):
        """__init__.py defines a non-empty __version__."""
        version = self._read_version()
        assert version, "__version__ is empty"
        assert re.match(r'\d+\.\d+\.\d+', version), \
            f"__version__ '{version}' does not look like a semantic version"

    def test_changelog_has_current_version(self):
        """CHANGELOG.md contains an entry for the current __version__."""
        version = self._read_version()
        text = CHANGELOG_MD.read_text(encoding="utf-8")
        assert version in text, \
            f"CHANGELOG.md has no entry for version {version}"

    def test_changelog_entry_is_at_top(self):
        """The current version's changelog entry appears before older entries."""
        version = self._read_version()
        text = CHANGELOG_MD.read_text(encoding="utf-8")
        lines = text.splitlines()

        version_positions = [
            i for i, line in enumerate(lines) if version in line
        ]
        older_positions = [
            i for i, line in enumerate(lines)
            if re.search(r'##\s+HPM\s+\[\d+\.\d+\.\d+', line)
            and version not in line
        ]

        assert version_positions, f"Version {version} not found in CHANGELOG"
        if older_positions:
            assert min(version_positions) < min(older_positions), \
                f"Version {version} entry is not at the top of the CHANGELOG"


@pytest.mark.acceptance
class TestSpecFile:
    """HPM.spec bundles the expected entry point and critical assets."""

    def test_spec_entry_point(self):
        """HPM.spec references gui/hstl_gui.py as the entry script."""
        text = HPM_SPEC.read_text(encoding="utf-8")
        assert "hstl_gui.py" in text, \
            "HPM.spec does not reference hstl_gui.py as the entry point"

    def test_spec_bundles_watermark(self):
        """HPM.spec includes Copyright_Watermark.png in datas."""
        text = HPM_SPEC.read_text(encoding="utf-8")
        assert "Copyright_Watermark.png" in text, \
            "HPM.spec does not bundle Copyright_Watermark.png"

    def test_spec_bundles_exiftool(self):
        """HPM.spec includes exiftool.exe in datas."""
        text = HPM_SPEC.read_text(encoding="utf-8")
        assert "exiftool.exe" in text, \
            "HPM.spec does not bundle exiftool.exe"

    def test_spec_console_is_false(self):
        """HPM.spec builds a windowed (no-console) executable."""
        text = HPM_SPEC.read_text(encoding="utf-8")
        assert "console=False" in text, \
            "HPM.spec does not set console=False — EXE may open a console window"
