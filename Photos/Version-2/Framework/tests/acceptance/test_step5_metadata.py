"""
Acceptance tests — Step 5 metadata embedding helper algorithms.

Tests the date-conversion, artifact-filtering, and verso-detection logic
frozen into HPM.exe (mirrored in conftest).  Covers:

  convert_date_step5 — 8 input patterns:
  - 'None' literal → '0000-00-00'
  - 'YYYY-YYYY' year range → end year with -00-00
  - 'M/D/YY' short date → '20YY-MM-DD'
  - 'c. YYYY' / 'ca. YYYY' / 'Ca. YYYY' circa dates → 'YYYY-00-00'
  - 'YYYY' year only → 'YYYY-00-00'
  - 'DayName, MM/DD/YYYY' → 'YYYY-MM-DD'
  - 'Month YYYY' → 'YYYY-MM-00'
  - 'Month DD, YYYY' → 'YYYY-MM-DD'
  - Unknown format → original string returned unchanged

  is_artifact_record:
  - All 13 known artifact strings are filtered out
  - Valid accession numbers pass through
  - Empty / whitespace strings are filtered

  is_verso_filename:
  - Files containing '_verso' or '_Verso' with .tif / .tiff extension match
  - Files without the pattern don't match
  - Non-TIFF files with the pattern don't match
"""

import pytest

from tests.acceptance.conftest import (
    ARTIFACT_PATTERNS,
    convert_date_step5,
    is_artifact_record,
    is_verso_filename,
)


# ---------------------------------------------------------------------------
# convert_date_step5 — date format patterns
# ---------------------------------------------------------------------------

class TestConvertDateNone:
    def test_none_literal_returns_placeholder(self):
        assert convert_date_step5("None") == "0000-00-00"


class TestConvertDateYearRange:
    """'YYYY-YYYY' → end-year with -00-00"""

    def test_typical_year_range(self):
        assert convert_date_step5("1941-1945") == "1945-00-00"

    def test_single_decade_range(self):
        assert convert_date_step5("1950-1959") == "1959-00-00"

    def test_year_range_uses_second_year(self):
        result = convert_date_step5("1960-1965")
        assert result.startswith("1965")


class TestConvertDateShortYear:
    """'M/D/YY' → '20YY-MM-DD'"""

    def test_single_digit_month_and_day(self):
        assert convert_date_step5("6/4/42") == "2042-06-04"

    def test_two_digit_month_and_day(self):
        assert convert_date_step5("12/31/99") == "2099-12-31"

    def test_zero_padded_output(self):
        result = convert_date_step5("1/9/55")
        assert result == "2055-01-09"


class TestConvertDateCirca:
    """c. YYYY / ca. YYYY / Ca. YYYY → YYYY-00-00"""

    def test_c_dot_with_space(self):
        assert convert_date_step5("c. 1945") == "1945-00-00"

    def test_c_dot_no_space(self):
        assert convert_date_step5("c.1945") == "1945-00-00"

    def test_ca_dot_lowercase(self):
        assert convert_date_step5("ca. 1932") == "1932-00-00"

    def test_ca_dot_no_space(self):
        assert convert_date_step5("ca.1932") == "1932-00-00"

    def test_ca_dot_capitalised(self):
        assert convert_date_step5("Ca. 1918") == "1918-00-00"

    def test_ca_dot_capitalised_no_space(self):
        assert convert_date_step5("Ca.1918") == "1918-00-00"


class TestConvertDateYearOnly:
    """'YYYY' → 'YYYY-00-00'"""

    def test_typical_year(self):
        assert convert_date_step5("1942") == "1942-00-00"

    def test_early_century_year(self):
        assert convert_date_step5("1900") == "1900-00-00"

    def test_recent_year(self):
        assert convert_date_step5("2024") == "2024-00-00"


class TestConvertDateFullWithDayName:
    """'DayName, MM/DD/YYYY' → 'YYYY-MM-DD'"""

    def test_monday(self):
        assert convert_date_step5("Monday, 06/04/1945") == "1945-06-04"

    def test_friday(self):
        assert convert_date_step5("Friday, 12/07/1941") == "1941-12-07"

    def test_output_format(self):
        result = convert_date_step5("Tuesday, 01/01/1946")
        assert result == "1946-01-01"


class TestConvertDateMonthYear:
    """'Month YYYY' → 'YYYY-MM-00'"""

    def test_june_1944(self):
        assert convert_date_step5("June 1944") == "1944-06-00"

    def test_january_1945(self):
        assert convert_date_step5("January 1945") == "1945-01-00"

    def test_december_1941(self):
        assert convert_date_step5("December 1941") == "1941-12-00"


class TestConvertDateMonthDayYear:
    """'Month DD, YYYY' → 'YYYY-MM-DD'"""

    def test_june_6_1944(self):
        assert convert_date_step5("June 6, 1944") == "1944-06-06"

    def test_december_7_1941(self):
        assert convert_date_step5("December 7, 1941") == "1941-12-07"

    def test_single_digit_day(self):
        assert convert_date_step5("March 1, 1945") == "1945-03-01"


class TestConvertDateUnknownFormat:
    """Unknown format strings must be returned unchanged."""

    @pytest.mark.parametrize("date_str", [
        "Spring 1945",
        "Early 1940s",
        "undated",
        "unknown",
        "1940s",
        "",
    ])
    def test_unknown_format_passthrough(self, date_str):
        assert convert_date_step5(date_str) == date_str


# ---------------------------------------------------------------------------
# is_artifact_record — artifact-pattern filtering
# ---------------------------------------------------------------------------

class TestIsArtifactRecord:
    """Rows whose ObjectName matches a known artifact pattern must be excluded."""

    @pytest.mark.parametrize("pattern", sorted(ARTIFACT_PATTERNS))
    def test_each_artifact_pattern_is_filtered(self, pattern):
        assert is_artifact_record(pattern) is True

    def test_empty_string_is_filtered(self):
        assert is_artifact_record("") is True

    def test_whitespace_only_is_filtered(self):
        assert is_artifact_record("   ") is True

    @pytest.mark.parametrize("accession", [
        "2024-001",
        "ACC-001",
        "HST-0042",
        "2024.001.abc",
        "TL2024-001",
    ])
    def test_valid_accession_numbers_pass(self, accession):
        assert is_artifact_record(accession) is False

    def test_partial_match_does_not_filter(self):
        """'ObjectName-extra' is not in the artifact set and must pass."""
        assert is_artifact_record("ObjectName-extra") is False

    def test_case_sensitive_matching(self):
        """Artifact patterns are case-sensitive; 'objectname' is not filtered."""
        assert is_artifact_record("objectname") is False
        assert is_artifact_record("OBJECTNAME") is False


# ---------------------------------------------------------------------------
# is_verso_filename — verso file detection
# ---------------------------------------------------------------------------

class TestIsVersoFilename:
    """Verso files must match '_verso' or '_Verso' with .tif / .tiff extension."""

    @pytest.mark.parametrize("filename", [
        "ACC-001_verso.tif",
        "ACC-001_verso.tiff",
        "ACC-001_Verso.tif",
        "ACC-001_Verso.tiff",
        "photo_name_verso.tif",
        "photo_name_Verso.tiff",
    ])
    def test_verso_tif_files_match(self, filename):
        assert is_verso_filename(filename) is True

    @pytest.mark.parametrize("filename", [
        "ACC-001.tif",          # no verso suffix
        "ACC-001_verso.jpg",    # wrong extension
        "ACC-001_verso.jpeg",   # wrong extension
        "ACC-001_verso.png",    # wrong extension
        "verso_ACC-001.tif",    # verso at start, not after underscore
        "ACC-001recto.tif",     # different suffix
        "ACC-001.tiff",         # no verso suffix
        "",
    ])
    def test_non_verso_files_do_not_match(self, filename):
        assert is_verso_filename(filename) is False

    def test_case_sensitivity_verso(self):
        """'_VERSO' (all caps) must not match — only '_verso' and '_Verso' are valid."""
        assert is_verso_filename("ACC-001_VERSO.tif") is False

    def test_mixed_path_with_verso(self):
        """Only the filename stem and extension matter, not directory components."""
        assert is_verso_filename("some/path/ACC-001_verso.tif") is True
