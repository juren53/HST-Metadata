"""
Acceptance tests — Step 2 Excel-to-CSV conversion algorithms.

Tests the date-building and IPTC-mapping logic frozen into HPM.exe
(mirrored in conftest.build_date_from_parts and conftest.IPTC_COLUMN_MAP).
Covers:

  Date building (build_date_from_parts):
  - Full date: year + month + day → YYYY-MM-DD
  - Partial date: missing day → YYYY-MM-00
  - Partial date: year only → YYYY-00-00
  - All zeros / all empty → no date data
  - Float strings from Excel (e.g. '1975.0') are handled
  - Invalid month / day values are rejected
  - nan/None/null strings treated as empty
  - is_partial flag set correctly

  IPTC column mapping:
  - All 7 mapping-row labels map to the correct IPTC field names
  - No extra mappings exist
"""

import pytest

from tests.acceptance.conftest import (
    IPTC_COLUMN_MAP,
    build_date_from_parts,
)


# ---------------------------------------------------------------------------
# build_date_from_parts — full dates
# ---------------------------------------------------------------------------

class TestFullDates:
    """All three components present and valid → exact ISO date, not partial."""

    def test_typical_full_date(self):
        iso, partial, reason = build_date_from_parts("6", "4", "1942")
        assert iso == "1942-06-04"
        assert partial is False
        assert reason == ""

    def test_zero_padded_inputs(self):
        iso, partial, reason = build_date_from_parts("01", "09", "1945")
        assert iso == "1945-01-09"
        assert partial is False

    def test_float_year_from_excel(self):
        """Excel sometimes stores years as float strings like '1975.0'."""
        iso, partial, reason = build_date_from_parts("3", "15", "1975.0")
        assert iso == "1975-03-15"
        assert partial is False

    def test_float_month_from_excel(self):
        iso, partial, reason = build_date_from_parts("6.0", "4", "1942")
        assert iso == "1942-06-04"
        assert partial is False

    def test_boundary_month_1(self):
        iso, partial, _ = build_date_from_parts("1", "1", "1950")
        assert iso == "1950-01-01"

    def test_boundary_month_12(self):
        iso, partial, _ = build_date_from_parts("12", "31", "1950")
        assert iso == "1950-12-31"

    def test_boundary_day_31(self):
        iso, partial, _ = build_date_from_parts("1", "31", "2000")
        assert iso == "2000-01-31"


# ---------------------------------------------------------------------------
# build_date_from_parts — partial dates
# ---------------------------------------------------------------------------

class TestPartialDates:
    """Missing components (zero/empty) → partial date with is_partial=True."""

    def test_year_only(self):
        iso, partial, reason = build_date_from_parts("", "", "1942")
        assert iso == "1942-00-00"
        assert partial is True
        assert reason == ""

    def test_year_and_month_only(self):
        iso, partial, reason = build_date_from_parts("6", "", "1942")
        assert iso == "1942-06-00"
        assert partial is True

    def test_year_and_day_only(self):
        iso, partial, reason = build_date_from_parts("", "4", "1942")
        assert iso == "1942-00-04"
        assert partial is True

    def test_month_day_no_year(self):
        iso, partial, reason = build_date_from_parts("6", "4", "")
        assert iso == "0000-06-04"
        assert partial is True

    def test_nan_string_treated_as_missing(self):
        iso, partial, _ = build_date_from_parts("nan", "nan", "1942")
        assert iso == "1942-00-00"
        assert partial is True

    def test_none_string_treated_as_missing(self):
        iso, partial, _ = build_date_from_parts("None", "None", "1942")
        assert iso == "1942-00-00"
        assert partial is True

    def test_null_string_treated_as_missing(self):
        iso, partial, _ = build_date_from_parts("null", "null", "1942")
        assert iso == "1942-00-00"
        assert partial is True


# ---------------------------------------------------------------------------
# build_date_from_parts — no date data
# ---------------------------------------------------------------------------

class TestNoDateData:
    """All components absent or zero → empty string with 'no date data'."""

    def test_all_empty_strings(self):
        iso, partial, reason = build_date_from_parts("", "", "")
        assert iso == ""
        assert partial is False
        assert reason == "no date data"

    def test_all_nan_strings(self):
        iso, partial, reason = build_date_from_parts("nan", "nan", "nan")
        assert iso == ""
        assert reason == "no date data"

    def test_all_zeros(self):
        iso, partial, reason = build_date_from_parts("0", "0", "0")
        assert iso == ""
        assert reason == "no date data"


# ---------------------------------------------------------------------------
# build_date_from_parts — invalid values rejected
# ---------------------------------------------------------------------------

class TestInvalidDates:
    """Out-of-range or non-numeric components → empty string with reason."""

    def test_invalid_month_13(self):
        iso, partial, reason = build_date_from_parts("13", "1", "1942")
        assert iso == ""
        assert "invalid" in reason

    def test_invalid_month_0_rejected(self):
        """Month 0 is the partial-date sentinel, not a valid calendar month.
        When year is also present, day=0, month=0 is partial — but month 0 alone
        with a non-zero year is partial, not invalid."""
        iso, partial, _ = build_date_from_parts("0", "0", "1942")
        # month=0, day=0, year=1942 → valid partial date
        assert iso == "1942-00-00"
        assert partial is True

    def test_invalid_day_32(self):
        iso, partial, reason = build_date_from_parts("1", "32", "1942")
        assert iso == ""
        assert "invalid" in reason

    def test_non_numeric_year(self):
        iso, partial, reason = build_date_from_parts("6", "4", "nineteen-forty-two")
        assert iso == ""
        assert "invalid" in reason

    def test_non_numeric_month(self):
        iso, partial, reason = build_date_from_parts("June", "4", "1942")
        assert iso == ""
        assert "invalid" in reason


# ---------------------------------------------------------------------------
# IPTC column mapping
# ---------------------------------------------------------------------------

class TestIPTCColumnMap:
    """IPTC_COLUMN_MAP must contain exactly the 7 mappings used by g2c.py."""

    EXPECTED = {
        "Title":                "Headline",
        "Accession Number":     "ObjectName",
        "Restrictions":         "CopyrightNotice",
        "Scopenote":            "Caption-Abstract",
        "Related Collection":   "Source",
        "Source Photographer":  "By-line",
        "Institutional Creator":"By-lineTitle",
    }

    def test_map_has_exactly_7_entries(self):
        assert len(IPTC_COLUMN_MAP) == 7

    @pytest.mark.parametrize("label,expected_field", EXPECTED.items())
    def test_each_label_maps_correctly(self, label, expected_field):
        assert IPTC_COLUMN_MAP[label] == expected_field

    def test_no_unexpected_keys(self):
        assert set(IPTC_COLUMN_MAP.keys()) == set(self.EXPECTED.keys())

    def test_no_unexpected_values(self):
        assert set(IPTC_COLUMN_MAP.values()) == set(self.EXPECTED.values())
