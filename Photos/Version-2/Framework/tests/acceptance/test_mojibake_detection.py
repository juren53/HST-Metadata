"""
Acceptance tests — Step 3 mojibake detection algorithm.

Tests the exact mojibake-detection logic frozen into HPM.exe
(mirrored in conftest.scan_for_mojibake / conftest.apply_mojibake_fixes).
Covers:

  - ftfy is importable (confirms EXE bundling is correct)
  - Clean UTF-8 text is not flagged
  - Known mojibake artifacts are detected and corrected in every checked field
  - ObjectName is never scanned (it is an identifier, not content)
  - Rows with multiple fields affected are reported correctly
  - Row numbering starts at 2 (row 1 is the CSV header)
  - apply_fixes row_num → data_index conversion is correct
  - Fix suggestions are idempotent (applying ftfy twice = applying once)
  - An all-clean CSV returns an empty issue list
  - A mixed CSV returns only the affected rows

These tests run against the algorithm mirrors in conftest.py and do not
require a running GUI process.
"""

import csv
import io

import pytest

from tests.acceptance.conftest import (
    MOJIBAKE_TEXT_FIELDS,
    apply_mojibake_fixes,
    scan_for_mojibake,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(**kwargs) -> dict:
    """Return a CSV row dict pre-filled with empty strings for all HPM fields."""
    base = {
        "Headline": "",
        "ObjectName": "",
        "CopyrightNotice": "",
        "Caption-Abstract": "",
        "Source": "",
        "By-line": "",
        "By-lineTitle": "",
        "DateCreated": "",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# ftfy availability
# ---------------------------------------------------------------------------

class TestFtfyAvailability:
    """ftfy must be importable — confirms it is bundled correctly in HPM.exe."""

    def test_ftfy_importable(self):
        import ftfy  # noqa: F401  — just verifying it doesn't raise

    def test_ftfy_fix_text_callable(self):
        import ftfy
        assert callable(ftfy.fix_text)

    def test_ftfy_version_present(self):
        import ftfy
        assert hasattr(ftfy, "__version__")


# ---------------------------------------------------------------------------
# Clean text — must NOT be flagged
# ---------------------------------------------------------------------------

class TestCleanTextNotFlagged:
    """Properly encoded UTF-8 text must produce no mojibake records."""

    def test_plain_ascii_is_clean(self):
        rows = [_make_row(Headline="Pacific Fleet Operations 1942")]
        assert scan_for_mojibake(rows) == []

    def test_valid_spanish_utf8_is_clean(self):
        rows = [_make_row(Headline="Fotografía de la flota del Pacífico")]
        assert scan_for_mojibake(rows) == []

    def test_valid_accented_french_is_clean(self):
        rows = [_make_row(Caption__Abstract="Débarquement en Normandie")]
        # Note: field key uses Python identifier — actual CSV field name tested separately
        rows = [_make_row(**{"Caption-Abstract": "Débarquement en Normandie"})]
        assert scan_for_mojibake(rows) == []

    def test_empty_fields_are_clean(self):
        rows = [_make_row()]  # all fields empty
        assert scan_for_mojibake(rows) == []

    def test_all_clean_rows_return_empty_list(self):
        rows = [
            _make_row(Headline="Pacific Fleet 1942", ObjectName="ACC-001"),
            _make_row(Headline="Battle of Midway", ObjectName="ACC-002"),
            _make_row(Headline="USS Enterprise 1944", ObjectName="ACC-003"),
        ]
        assert scan_for_mojibake(rows) == []


# ---------------------------------------------------------------------------
# Mojibake detection — known artifacts must be flagged
# ---------------------------------------------------------------------------

class TestMojibakeDetected:
    """Rows containing known UTF-8→Windows-1252 artifacts must be flagged."""

    # Representative mojibake strings and their correct UTF-8 equivalents
    MOJIBAKE_CASES = [
        ("Ã±",  "ñ"),   # Spanish ñ
        ("Ã¡",  "á"),   # Spanish á
        ("Ã©",  "é"),   # Spanish é
        ("Ã­",  "í"),   # Spanish í
        ("Ã³",  "ó"),   # Spanish ó
        ("Ãº",  "ú"),   # Spanish ú
        ("Ã¼",  "ü"),   # German ü
        ("Ã¤",  "ä"),   # German ä
        ("Ã¶",  "ö"),   # German ö
        ("â€™", "\u2019"),  # Right single quotation mark
        ("â€œ", "\u201c"),  # Left double quotation mark
    ]

    @pytest.mark.parametrize("mojibake,_expected", MOJIBAKE_CASES)
    def test_headline_mojibake_is_flagged(self, mojibake, _expected):
        rows = [_make_row(Headline=f"Foto de la Comisio{mojibake}n")]
        records = scan_for_mojibake(rows)
        assert len(records) == 1
        assert "Headline" in records[0]["issues"]

    @pytest.mark.parametrize("field", MOJIBAKE_TEXT_FIELDS)
    def test_each_checked_field_is_scanned(self, field):
        """Every field in MOJIBAKE_TEXT_FIELDS must be individually checked."""
        rows = [_make_row(**{field: "CafÃ© au lait"})]
        records = scan_for_mojibake(rows)
        assert len(records) == 1, f"Mojibake in '{field}' was not detected"
        assert field in records[0]["issues"]

    def test_suggested_fix_corrects_spanish_n(self):
        rows = [_make_row(Headline="EspaÃ±a")]
        records = scan_for_mojibake(rows)
        assert records[0]["issues"]["Headline"]["suggested"] == "España"

    def test_suggested_fix_corrects_accented_e(self):
        rows = [_make_row(**{"Caption-Abstract": "CafÃ© on the plaza"})]
        records = scan_for_mojibake(rows)
        assert records[0]["issues"]["Caption-Abstract"]["suggested"] == "Café on the plaza"

    def test_original_text_preserved_in_issue(self):
        original = "ResoluciÃ³n"
        rows = [_make_row(Headline=original)]
        records = scan_for_mojibake(rows)
        assert records[0]["issues"]["Headline"]["original"] == original


# ---------------------------------------------------------------------------
# ObjectName must NOT be scanned
# ---------------------------------------------------------------------------

class TestObjectNameNotScanned:
    """ObjectName is an accession-number identifier — never scanned for mojibake."""

    def test_mojibake_in_object_name_not_flagged(self):
        # If ObjectName were scanned, this row would be flagged.
        rows = [_make_row(ObjectName="CafÃ©-001")]
        assert scan_for_mojibake(rows) == []

    def test_object_name_not_in_checked_fields(self):
        assert "ObjectName" not in MOJIBAKE_TEXT_FIELDS


# ---------------------------------------------------------------------------
# Row numbering
# ---------------------------------------------------------------------------

class TestRowNumbering:
    """row_num must start at 2 (row 1 is the CSV header)."""

    def test_first_data_row_is_row_2(self):
        rows = [_make_row(Headline="CafÃ©")]
        records = scan_for_mojibake(rows)
        assert records[0]["row_num"] == 2

    def test_second_data_row_is_row_3(self):
        rows = [
            _make_row(Headline="Clean"),
            _make_row(Headline="CafÃ©"),
        ]
        records = scan_for_mojibake(rows)
        assert records[0]["row_num"] == 3

    def test_row_numbers_are_sequential(self):
        rows = [
            _make_row(Headline="CafÃ©"),       # row 2
            _make_row(Headline="Clean"),
            _make_row(Headline="EspaÃ±a"),     # row 4
        ]
        records = scan_for_mojibake(rows)
        assert [r["row_num"] for r in records] == [2, 4]


# ---------------------------------------------------------------------------
# object_name capture
# ---------------------------------------------------------------------------

class TestObjectNameCapture:
    """The object_name key in each record must reflect the ObjectName column."""

    def test_object_name_captured_correctly(self):
        rows = [_make_row(Headline="CafÃ©", ObjectName="ACC-2024-001")]
        records = scan_for_mojibake(rows)
        assert records[0]["object_name"] == "ACC-2024-001"

    def test_missing_object_name_defaults_to_unknown(self):
        row = _make_row(Headline="CafÃ©")
        row.pop("ObjectName")  # simulate absent column
        records = scan_for_mojibake([row])
        assert records[0]["object_name"] == "Unknown"


# ---------------------------------------------------------------------------
# Multiple issues in a single row
# ---------------------------------------------------------------------------

class TestMultipleIssuesPerRow:
    """A row with mojibake in several fields should yield one record listing all fields."""

    def test_two_fields_in_one_record(self):
        rows = [_make_row(
            Headline="CafÃ©",
            **{"Caption-Abstract": "EspaÃ±a"},
        )]
        records = scan_for_mojibake(rows)
        assert len(records) == 1
        assert "Headline" in records[0]["issues"]
        assert "Caption-Abstract" in records[0]["issues"]

    def test_all_six_fields_in_one_record(self):
        rows = [_make_row(
            Headline="CafÃ©",
            **{
                "Caption-Abstract": "EspaÃ±a",
                "Source":           "BibliotecaÃ±",
                "By-line":          "GonzÃ¡lez",
                "By-lineTitle":     "FotÃ³grafo",
                "CopyrightNotice":  "RestriccioÃ³n",
            }
        )]
        records = scan_for_mojibake(rows)
        assert len(records) == 1
        assert len(records[0]["issues"]) == 6


# ---------------------------------------------------------------------------
# Mixed CSV — only affected rows returned
# ---------------------------------------------------------------------------

class TestMixedCSV:
    """A CSV with some clean and some mojibake rows returns only the bad ones."""

    def test_only_bad_rows_returned(self):
        rows = [
            _make_row(Headline="Pacific Fleet",     ObjectName="ACC-001"),  # clean
            _make_row(Headline="CafÃ©",             ObjectName="ACC-002"),  # bad
            _make_row(Headline="Battle of Midway",  ObjectName="ACC-003"),  # clean
            _make_row(Headline="EspaÃ±a",           ObjectName="ACC-004"),  # bad
        ]
        records = scan_for_mojibake(rows)
        assert len(records) == 2
        assert records[0]["object_name"] == "ACC-002"
        assert records[1]["object_name"] == "ACC-004"


# ---------------------------------------------------------------------------
# apply_mojibake_fixes — row_num → data_index conversion
# ---------------------------------------------------------------------------

class TestApplyFixes:
    """Verify the row_num → data_index mapping and that edits are written correctly."""

    def test_row_2_maps_to_index_0(self):
        rows = [
            _make_row(Headline="CafÃ©",    ObjectName="ACC-001"),
            _make_row(Headline="Original", ObjectName="ACC-002"),
        ]
        edits = {2: {"Headline": "Café"}}
        result = apply_mojibake_fixes(rows, edits)
        assert result[0]["Headline"] == "Café"

    def test_row_3_maps_to_index_1(self):
        rows = [
            _make_row(Headline="Clean",   ObjectName="ACC-001"),
            _make_row(Headline="CafÃ©",  ObjectName="ACC-002"),
        ]
        edits = {3: {"Headline": "Café"}}
        result = apply_mojibake_fixes(rows, edits)
        assert result[1]["Headline"] == "Café"

    def test_unedited_rows_are_unchanged(self):
        rows = [
            _make_row(Headline="CafÃ©",   ObjectName="ACC-001"),
            _make_row(Headline="Untouched", ObjectName="ACC-002"),
        ]
        edits = {2: {"Headline": "Café"}}
        result = apply_mojibake_fixes(rows, edits)
        assert result[1]["Headline"] == "Untouched"

    def test_multiple_fields_edited_in_one_row(self):
        rows = [_make_row(
            Headline="CafÃ©",
            **{"Caption-Abstract": "EspaÃ±a"},
            ObjectName="ACC-001",
        )]
        edits = {2: {"Headline": "Café", "Caption-Abstract": "España"}}
        result = apply_mojibake_fixes(rows, edits)
        assert result[0]["Headline"] == "Café"
        assert result[0]["Caption-Abstract"] == "España"

    def test_original_rows_not_mutated(self):
        """apply_mojibake_fixes must return a new list, not modify in place."""
        rows = [_make_row(Headline="CafÃ©")]
        edits = {2: {"Headline": "Café"}}
        _ = apply_mojibake_fixes(rows, edits)
        assert rows[0]["Headline"] == "CafÃ©"

    def test_out_of_range_row_num_ignored(self):
        rows = [_make_row(Headline="Clean")]
        edits = {99: {"Headline": "Should not appear"}}
        result = apply_mojibake_fixes(rows, edits)
        assert result[0]["Headline"] == "Clean"


# ---------------------------------------------------------------------------
# Idempotency — applying ftfy twice equals applying it once
# ---------------------------------------------------------------------------

class TestFixIdempotency:
    """ftfy.fix_text must be idempotent: fix(fix(x)) == fix(x)."""

    @pytest.mark.parametrize("mojibake", [
        "CafÃ©",
        "EspaÃ±a",
        "GonzÃ¡lez",
        "â€™s history",
    ])
    def test_fix_text_is_idempotent(self, mojibake):
        import ftfy
        once  = ftfy.fix_text(mojibake)
        twice = ftfy.fix_text(once)
        assert once == twice

    def test_already_fixed_text_unchanged_by_scan(self):
        """A row that was already fixed must not appear in a second scan."""
        import ftfy
        original = "CafÃ©"
        fixed_row = _make_row(Headline=ftfy.fix_text(original))
        assert scan_for_mojibake([fixed_row]) == []


# ---------------------------------------------------------------------------
# CSV round-trip — scan on a real CSV string
# ---------------------------------------------------------------------------

class TestCSVRoundTrip:
    """Simulate the full Step 3 pipeline: write CSV → DictReader → scan."""

    def _parse_csv(self, csv_text: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(csv_text))
        return list(reader)

    def test_clean_csv_produces_no_records(self):
        csv_text = (
            "Headline,ObjectName,CopyrightNotice,Caption-Abstract,Source,By-line,By-lineTitle,DateCreated\n"
            "Pacific Fleet,ACC-001,Unrestricted,Operations in 1942,NARA,Smith J.,Photographer,1942-06-00\n"
            "Battle of Midway,ACC-002,Unrestricted,Carrier battle,NARA,Jones R.,Photographer,1942-06-04\n"
        )
        rows = self._parse_csv(csv_text)
        assert scan_for_mojibake(rows) == []

    def test_mojibake_csv_produces_correct_record(self):
        csv_text = (
            "Headline,ObjectName,CopyrightNotice,Caption-Abstract,Source,By-line,By-lineTitle,DateCreated\n"
            "CafÃ© Society,ACC-001,Unrestricted,A story of EspaÃ±a,NARA,Smith J.,Photographer,1942-06-00\n"
        )
        rows = self._parse_csv(csv_text)
        records = scan_for_mojibake(rows)
        assert len(records) == 1
        assert records[0]["row_num"] == 2
        assert records[0]["object_name"] == "ACC-001"
        assert "Headline" in records[0]["issues"]
        assert "Caption-Abstract" in records[0]["issues"]

    def test_only_mojibake_rows_flagged_in_mixed_csv(self):
        csv_text = (
            "Headline,ObjectName,CopyrightNotice,Caption-Abstract,Source,By-line,By-lineTitle,DateCreated\n"
            "Pacific Fleet,ACC-001,Unrestricted,Clean row,NARA,Smith J.,Photographer,1942-06-00\n"
            "CafÃ© Society,ACC-002,Unrestricted,Clean caption,NARA,Jones R.,Photographer,1943-01-00\n"
            "Clean again,ACC-003,Unrestricted,Also clean,NARA,Brown K.,Photographer,1944-01-00\n"
        )
        rows = self._parse_csv(csv_text)
        records = scan_for_mojibake(rows)
        assert len(records) == 1
        assert records[0]["object_name"] == "ACC-002"
        assert records[0]["row_num"] == 3
