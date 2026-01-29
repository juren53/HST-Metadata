# HPM Partial Date Modifications to DateCreated Field

## Overview
This document outlines the plan to modify the `g2c.py` script's date processing logic to support partial dates in the `DateCreated` field. The change allows handling scenarios where only year, month, or day information is available, using "00" placeholders for missing components.

## Current Issue Analysis
The existing `get_date_from_columns` function at `g2c.py:344-386` requires **all three date components** (month, day, year) to be present and valid. It returns an empty string if any component is missing, which doesn't meet the customer's requirement for partial date support.

### Current Logic Problems
- **All-or-nothing validation:** Returns empty string if any component is missing
- **No partial date support:** Cannot handle year-only (1947-00-00) or month-only (0000-06-00) scenarios
- **Rigid formatting:** Only accepts complete dates in ISO format

## Proposed Solution

### Core Logic Change
Replace the all-or-nothing validation with flexible partial date handling that fills missing components with "00".

### Key Modifications Required

#### 1. Validation Logic Changes (`g2c.py:368-383`)

**CURRENT CODE:**
```python
if (
    month_str
    and day_str
    and year_str
    and month_str.isdigit()
    and day_str.isdigit()
    and year_str.isdigit()
):
    year_int = int(year_str)
    month_int = int(month_str)
    day_int = int(day_str)

    # Basic date validation
    if 1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 0:
        return f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
```

**NEW CODE:**
```python
# Validate each component individually - fail-fast on invalid data
if year_str and not year_str.isdigit():
    return ""  # Invalid year format
if month_str and not month_str.isdigit():
    return ""  # Invalid month format
if day_str and not day_str.isdigit():
    return ""  # Invalid day format

# Extract numeric values (0 if missing/blank)
year_int = int(year_str) if year_str else 0
month_int = int(month_str) if month_str else 0
day_int = int(day_str) if day_str else 0

# If no components present at all, return empty string
if year_int == 0 and month_int == 0 and day_int == 0:
    return ""

# Apply range validation only to present (non-zero) components
if year_int != 0 and year_int <= 0:
    return ""  # Invalid year value
if month_int != 0 and not (1 <= month_int <= 12):
    return ""  # Invalid month value
if day_int != 0 and not (1 <= day_int <= 31):
    return ""  # Invalid day value

# Format with zero-padded components
return f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
```

#### 2. Component Processing Logic

**Key Changes:**
- **Independent validation:** Each component validated separately
- **Zero fallback:** Missing/blank components become "00"
- **Fail-fast:** Invalid data returns empty string immediately
- **All-blank guard:** Returns empty string when no date data exists
- **Range validation:** Only applied to present (non-zero) components
- **Consistent formatting:** Always produces valid ISO format

### Example Transformations

| Input (Year/Month/Day) | Current Output | New Output |
|-----------------------|---------------|------------|
| 1947/blank/blank | "" (empty) | "1947-00-00" |
| blank/6/blank | "" (empty) | "0000-06-00" |
| blank/blank/15 | "" (empty) | "0000-00-15" |
| 1947/6/blank | "" (empty) | "1947-06-00" |
| 1947/blank/15 | "" (empty) | "1947-00-15" |
| 1947/6/15 | "1947-06-15" | "1947-06-15" |
| blank/blank/blank | "" (empty) | "" (empty) |

### Edge Cases Handled

1. **Invalid numeric values** (month=13, day=32) -> Empty string
2. **Zero/negative years** -> Empty string
3. **Non-numeric values** -> Empty string
4. **Mixed valid/invalid components** -> Empty string (fail-fast)
5. **All components blank** -> Empty string (no date data to preserve)
6. **Single digit numbers** -> Zero-padded (6 -> "06", 7 -> "07")

### Data Source Compatibility

**Primary Source:** `productionDateMonth/Day/Year` columns
**Fallback Source:** `coverageStartDateMonth/Day/Year` columns

The new logic applies equally to both date sources without any changes to the column detection or prioritization logic.

### Implementation Benefits

- **Backward Compatible:** Complete dates still work identically
- **Flexible:** Supports any combination of partial dates
- **Robust:** Maintains strict validation for present components
- **Standardized:** Always produces valid ISO format
- **Clear:** Predictable "00" placeholders for unknown components
- **Minimal Impact:** Changes localized to single function

### Code Location Changes

#### Primary Target
**File:** `g2c.py`
**Function:** `get_date_from_columns` (lines 344-386)
**Change Type:** Complete function replacement

#### Secondary Updates
- **Logging messages:** Update to reflect partial date capability
- **Comments:** Add documentation for new partial date logic
- **No changes needed:** Column detection logic, row processing, error handling structure

### Implementation Steps

1. **Backup current implementation**
2. **Replace `get_date_from_columns` function** with new logic
3. **Update function documentation** to describe partial date support
4. **Test with sample data** covering all scenarios:
   - Complete dates
   - Year-only dates
   - Month-only dates
   - Day-only dates
   - Mixed partial dates
   - Invalid data scenarios
5. **Verify CSV output** contains proper ISO-formatted dates

### Testing Matrix

| Test Case | Input | Expected Output | Notes |
|-----------|-------|-----------------|-------|
| Complete date | 1947, 6, 15 | "1947-06-15" | Existing functionality |
| Year only | 1947, blank, blank | "1947-00-00" | New requirement |
| Month only | blank, 6, blank | "0000-06-00" | New requirement |
| Day only | blank, blank, 15 | "0000-00-15" | New requirement |
| Year+Month | 1947, 6, blank | "1947-06-00" | New requirement |
| Year+Day | 1947, blank, 15 | "1947-00-15" | New requirement |
| Month+Day | blank, 6, 15 | "0000-06-15" | New requirement |
| All blank | blank, blank, blank | "" | No date data |
| Invalid month | 1947, 13, blank | "" | Fail-fast on invalid |
| Invalid day | 1947, blank, 32 | "" | Fail-fast on invalid |
| Invalid year | -100, 6, blank | "" | Fail-fast on invalid |
| Non-numeric | "abc", 6, 15 | "" | Fail-fast on invalid |

### Impact Assessment

**Risk Level:** Low
- Changes localized to single function
- Backward compatibility maintained
- Fail-fast validation preserves data integrity

**Performance Impact:** Minimal
- Same computational complexity
- No additional database calls or external dependencies

**User Experience:** Improved
- More data captured instead of discarded
- Consistent ISO formatting maintained
- Clear placeholder system for unknown components

### Pre-Implementation Validation Required

Before implementing, verify that downstream consumers can handle partial dates:

1. **ExifTool compatibility:** Confirm ExifTool accepts `DateCreated` values like `1947-00-00` or `0000-06-00`. Test with:
   ```bash
   exiftool -DateCreated="1947-00-00" test.jpg
   ```

2. **Target system requirements:** Confirm the customer's metadata system accepts partial ISO dates with "00" placeholders.

3. **Decimal/float values:** Note that `isdigit()` rejects values like `"1947.0"` which pandas may produce from numeric columns. If this is a concern, consider adding `.split('.')[0]` handling or using a more permissive check.

---

**Date:** January 28, 2026
**Original Author:** OpenCode Assistant
**Reviewed By:** Claude (Opus 4.5)
**Status:** Ready for Implementation (pending downstream validation)
**Next Step:** Validate ExifTool compatibility with partial dates, then implement
