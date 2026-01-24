# Consensus Critique: g2c.py

**Date:** 2026-01-23
**Sources:** ChatGPT, Claude, Gemini, Qwen critiques
**Purpose:** Synthesize four independent code reviews into actionable findings

---

## Executive Summary

All four reviewers agree that `g2c.py` serves a valid purpose—converting Excel spreadsheets to IPTC-mapped CSV files—but suffers from significant technical debt. The script has a solid core design with clever features (row-3 semantic mapping, mojibake cleanup), but contains dead code, duplicate definitions, and legacy artifacts that should be removed.

---

## What g2c.py Does

**Purpose:** Convert Excel metadata spreadsheets to CSV with IPTC field mapping for the HPM photo processing workflow.

**Key Features (Consensus):**
- Reads `.xlsx` (openpyxl) and `.xls` (xlrd) files
- Uses **row 3** as semantic field labels (not column headers)
- Maps spreadsheet columns to IPTC metadata fields
- Fixes mojibake/encoding artifacts (UTF-8 ↔ Windows-1252)
- Constructs `DateCreated` in ISO 8601 format (YYYY-MM-DD)
- Exports clean UTF-8 CSV

---

## Strengths (All Reviewers Agree)

| Strength | Description |
|----------|-------------|
| **Row-3 semantic mapping** | Clever approach—spreadsheet is self-describing via row 3 labels |
| **Mojibake cleanup** | Robust encoding artifact repair (Ã± → ñ, â€™ → ', etc.) |
| **Engine auto-detection** | Correctly switches between openpyxl and xlrd based on extension |
| **IPTC date formatting** | Proper ISO 8601 output from split date columns |
| **Fuzzy matching** | Handles variations like "Related Collection" vs "Related collections" |
| **Diagnostic output** | Good logging and summary functions for debugging |

---

## Critical Issues (Unanimous Agreement)

### 1. Dead/Unreachable Code in `read_excel_file()`

**Identified by:** ChatGPT, Claude, Qwen

After `return df` (around line 77), there are **~50+ lines of unreachable code** including:
- Duplicate header handling logic
- References to undefined variables (`headers`, `data_rows`)
- Google Sheets API remnants (`HttpError`)

```python
return df  # Line ~77

# Everything below this NEVER EXECUTES
# Check for duplicate headers ...
# except HttpError as error:
```

**Impact:** Technical debt, confusing for maintainers
**Fix:** Delete all code after `return df`

---

### 2. Duplicate Argument Definitions

**Identified by:** ChatGPT, Claude, Qwen

The argparse arguments are defined **twice**:

```python
parser.add_argument("--excel-file", "-f", ...)  # First definition
parser.add_argument("--excel-file", "-f", ...)  # Duplicate!
```

**Impact:** Sloppy, confusing, potential for subtle bugs
**Fix:** Remove duplicate `add_argument()` calls

---

### 3. Duplicate Exception Handling

**Identified by:** Claude, Qwen

Error handling blocks are duplicated with redundant `sys.exit(1)` calls:

```python
except Exception as e:
    print(f"\nERROR: Error reading Excel file: {e}")
    sys.exit(1)
    print(f"\n❌ Error reading Excel file: {e}")  # Never reached!
    sys.exit(1)
```

**Impact:** Dead code, misleading
**Fix:** Consolidate to single exception block

---

### 4. Undefined/Missing Imports

**Identified by:** ChatGPT, Claude, Qwen

References to `HttpError` from Google API libraries that are:
- Never imported
- Part of legacy Google Sheets code
- In unreachable code blocks

**Impact:** Would cause `NameError` if that code path were reachable
**Fix:** Remove legacy Google Sheets code entirely

---

## Moderate Issues

### 5. Hard Dependency on Row 3 Layout

**Identified by:** ChatGPT

The script assumes row 3 contains semantic labels. If someone inserts a row above row 3, the entire mapping breaks silently.

**Recommendation:** Add validation that row 3 contains expected field names, or make row index configurable.

---

### 6. Mixed DataFrame References in Date Logic

**Identified by:** Qwen

Date processing uses `df_cleaned` but date columns may reference the original DataFrame, leading to potential index mismatches.

**Recommendation:** Ensure consistent DataFrame usage throughout date processing.

---

## Minor Issues

| Issue | Identified By | Recommendation |
|-------|---------------|----------------|
| No timezone handling for dates | ChatGPT | Probably fine for IPTC use case |
| `str()` conversion flattens mixed-type columns | ChatGPT | Intentional for CSV export |
| xlrd must be installed separately | ChatGPT | Document in requirements.txt |

---

## IPTC Field Mapping (Reference)

All reviewers documented the same mapping table:

| Spreadsheet Label (Row 3) | IPTC Field |
|---------------------------|------------|
| Title | Headline |
| Accession Number | ObjectName |
| Restrictions | CopyrightNotice |
| Scopenote | Caption-Abstract |
| Related Collection | Source |
| Source Photographer | By-line |
| Institutional Creator | By-lineTitle |

Plus date synthesis:
- `productionDateMonth` + `productionDateDay` + `productionDateYear` → `DateCreated`

---

## Recommended Actions

### Priority 1: Must Fix (Before Next Release)

1. **Delete unreachable code** after `return df` in `read_excel_file()`
2. **Remove duplicate argparse definitions**
3. **Remove duplicate exception blocks**
4. **Remove all Google Sheets/HttpError references**

### Priority 2: Should Fix (Technical Debt)

5. **Add row 3 validation** - Verify expected labels are present
6. **Add unit tests** - Ensure IPTC mapping works correctly
7. **Make row index configurable** - Don't hardcode row 3

### Priority 3: Nice to Have

8. **Refactor into clean module** - Separate concerns (read, clean, map, export)
9. **Add schema validation** - Validate spreadsheet structure before processing
10. **Improve error messages** - More actionable guidance when things fail

---

## Reviewer Agreement Matrix

| Issue | ChatGPT | Claude | Gemini | Qwen |
|-------|:-------:|:------:|:------:|:----:|
| Dead code after `return df` | ✓ | ✓ | — | ✓ |
| Duplicate argparse args | ✓ | ✓ | — | ✓ |
| Duplicate exception blocks | — | ✓ | — | ✓ |
| HttpError/Google remnants | ✓ | ✓ | — | — |
| Row 3 fragility | ✓ | — | — | — |
| Mojibake cleanup is good | ✓ | ✓ | ✓ | — |
| IPTC mapping is solid | ✓ | ✓ | ✓ | ✓ |

**Legend:** ✓ = Explicitly mentioned, — = Not mentioned

---

## Conclusion

`g2c.py` is functional and serves its purpose in the HPM pipeline, but carries significant technical debt from its evolution (likely from a Google Sheets-based original). The core logic is sound—the row-3 semantic mapping and encoding cleanup are well-designed. However, the script needs cleanup to remove dead code, duplicates, and legacy artifacts before it can be considered maintainable.

**Estimated cleanup effort:** 1-2 hours for Priority 1 fixes.

---

*This consensus was synthesized from four independent AI code reviews conducted on 2026-01-22/23.*
