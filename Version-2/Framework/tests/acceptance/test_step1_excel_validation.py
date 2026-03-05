"""
Acceptance tests — Step 1 Excel structure validation.

Tests the logic frozen into HPM.exe that validates an Excel spreadsheet
before it is accepted for processing (mirrored in conftest.find_mapping_row
and conftest.missing_mapping_headers).  Covers:

  - The "HST - DRUPAL FIELDS" sentinel row is found when present
  - Search range: rows 0-4 (any of the first 5 rows)
  - Sentinel not found returns None
  - All 7 required mapping headers must be present
  - Header check is case-insensitive
  - Missing headers are correctly identified
  - A well-formed DataFrame passes with zero missing headers
"""

import pandas as pd
import pytest

from tests.acceptance.conftest import (
    REQUIRED_MAPPING_HEADERS,
    find_mapping_row,
    missing_mapping_headers,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(rows: list[list]) -> pd.DataFrame:
    """Build a DataFrame from a list of row-lists (no header inference)."""
    return pd.DataFrame(rows)


def _mapping_row_data() -> list:
    """A well-formed mapping row containing all required headers."""
    return [
        "HST - DRUPAL FIELDS",
        "Title",
        "Accession Number",
        "Restrictions",
        "Scopenote",
        "Related Collection",
        "Source Photographer",
        "Institutional Creator",
        "productionDateMonth",
        "productionDateDay",
        "productionDateYear",
    ]


# ---------------------------------------------------------------------------
# find_mapping_row — sentinel detection
# ---------------------------------------------------------------------------

class TestFindMappingRow:
    """find_mapping_row must locate the 'HST - DRUPAL FIELDS' sentinel."""

    def test_sentinel_on_row_0(self):
        df = _make_df([_mapping_row_data(), ["data", "ACC-001"]])
        assert find_mapping_row(df) == 0

    def test_sentinel_on_row_1(self):
        df = _make_df([
            ["Some preamble"],
            _mapping_row_data(),
            ["data", "ACC-001"],
        ])
        assert find_mapping_row(df) == 1

    def test_sentinel_on_row_2(self):
        df = _make_df([
            ["Preamble 1"],
            ["Preamble 2"],
            _mapping_row_data(),
            ["data", "ACC-001"],
        ])
        assert find_mapping_row(df) == 2

    def test_sentinel_on_row_3(self):
        df = _make_df([
            ["Preamble 1"],
            ["Preamble 2"],
            ["Preamble 3"],
            _mapping_row_data(),
            ["data", "ACC-001"],
        ])
        assert find_mapping_row(df) == 3

    def test_sentinel_on_row_4(self):
        df = _make_df([
            ["Preamble 1"],
            ["Preamble 2"],
            ["Preamble 3"],
            ["Preamble 4"],
            _mapping_row_data(),
            ["data", "ACC-001"],
        ])
        assert find_mapping_row(df) == 4

    def test_sentinel_not_found_returns_none(self):
        df = _make_df([
            ["Preamble 1"],
            ["Preamble 2"],
            ["No sentinel here"],
            ["data", "ACC-001"],
        ])
        assert find_mapping_row(df) is None

    def test_sentinel_beyond_row_4_not_found(self):
        """Rows beyond index 4 must not be scanned."""
        df = _make_df([
            ["Preamble 1"],
            ["Preamble 2"],
            ["Preamble 3"],
            ["Preamble 4"],
            ["Preamble 5"],
            _mapping_row_data(),   # row index 5 — out of scan range
            ["data", "ACC-001"],
        ])
        assert find_mapping_row(df) is None

    def test_sentinel_substring_match(self):
        """The check uses 'in', so extra text around the sentinel is fine."""
        row = _mapping_row_data()
        row[0] = "BATCH 42 - HST - DRUPAL FIELDS - 2024"
        df = _make_df([row, ["data", "ACC-001"]])
        assert find_mapping_row(df) == 0

    def test_empty_dataframe_returns_none(self):
        df = pd.DataFrame()
        assert find_mapping_row(df) is None

    def test_nan_first_cell_skipped(self):
        """A NaN first cell must not raise an error and must not match."""
        df = _make_df([
            [None, "something"],
            _mapping_row_data(),
            ["data"],
        ])
        assert find_mapping_row(df) == 1


# ---------------------------------------------------------------------------
# missing_mapping_headers — required header validation
# ---------------------------------------------------------------------------

class TestMissingMappingHeaders:
    """missing_mapping_headers must return an empty list for a valid row."""

    def test_all_headers_present_returns_empty(self):
        df = _make_df([_mapping_row_data()])
        assert missing_mapping_headers(df, 0) == []

    def test_missing_one_header(self):
        row = _mapping_row_data()
        row.remove("Scopenote")
        df = _make_df([row])
        missing = missing_mapping_headers(df, 0)
        assert missing == ["Scopenote"]

    def test_missing_multiple_headers(self):
        row = _mapping_row_data()
        for h in ("Title", "Source Photographer", "Institutional Creator"):
            row.remove(h)
        df = _make_df([row])
        missing = missing_mapping_headers(df, 0)
        assert set(missing) == {"Title", "Source Photographer", "Institutional Creator"}

    def test_all_headers_missing(self):
        df = _make_df([["HST - DRUPAL FIELDS", "SomeOtherColumn"]])
        missing = missing_mapping_headers(df, 0)
        assert set(missing) == set(REQUIRED_MAPPING_HEADERS)

    def test_header_check_is_case_insensitive(self):
        row = ["HST - DRUPAL FIELDS"] + [h.upper() for h in REQUIRED_MAPPING_HEADERS]
        df = _make_df([row])
        assert missing_mapping_headers(df, 0) == []

    def test_extra_columns_do_not_cause_failure(self):
        row = _mapping_row_data() + ["ExtraCol1", "ExtraCol2"]
        df = _make_df([row])
        assert missing_mapping_headers(df, 0) == []

    def test_nan_cells_treated_as_empty(self):
        """NaN cells in the mapping row must not match any required header."""
        row = [None] * 5 + REQUIRED_MAPPING_HEADERS
        df = _make_df([row])
        assert missing_mapping_headers(df, 0) == []

    @pytest.mark.parametrize("header", REQUIRED_MAPPING_HEADERS)
    def test_each_required_header_individually(self, header):
        """Removing each required header one at a time must be caught."""
        row = _mapping_row_data().copy()
        row.remove(header)
        df = _make_df([row])
        assert header in missing_mapping_headers(df, 0)


# ---------------------------------------------------------------------------
# Integration: full validation flow
# ---------------------------------------------------------------------------

class TestFullValidationFlow:
    """End-to-end: find the sentinel row then check its headers."""

    def test_valid_spreadsheet_passes(self):
        df = _make_df([
            ["Batch: Pacific Fleet"],
            ["Created: 2024-01"],
            _mapping_row_data(),
            ["ACC-001", "Photo title", "Unrestricted"],
        ])
        idx = find_mapping_row(df)
        assert idx is not None
        assert missing_mapping_headers(df, idx) == []

    def test_spreadsheet_without_sentinel_fails(self):
        df = _make_df([
            ["Col A", "Col B"],
            ["ACC-001", "title"],
        ])
        assert find_mapping_row(df) is None

    def test_spreadsheet_with_missing_headers_fails(self):
        row = _mapping_row_data()
        row.remove("Accession Number")
        df = _make_df([row, ["data"]])
        idx = find_mapping_row(df)
        assert idx is not None
        assert "Accession Number" in missing_mapping_headers(df, idx)
