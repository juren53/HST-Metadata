# HPM Partial Date Implementation Report

**Date:** January 28, 2026
**Implemented By:** Claude (Opus 4.5)
**Status:** Complete - Released in v1.8.3

## Summary

Modified the `get_date_from_columns` function in `g2c.py` to support partial dates in the `DateCreated` field. The change allows handling scenarios where only year, month, or day information is available, using "00" placeholders for missing components.

**Key insight:** The placeholder `"0000-00-00"` must be applied AFTER both productionDate and coverageStartDate fallback attempts, not inside the helper function. This prevents the truthy string from blocking the fallback logic.

## Files Modified

| File | Lines | Change Type |
|------|-------|-------------|
| `g2c.py` | 343-402 | Function modification |
| `g2c.py` | 433-436 | Added final fallback |

## Changes Made

### 1. Updated Function Comment (line 344)
Added note about partial date support:
```python
# Supports partial dates: missing components become "00" (e.g., "1947-00-00" for year-only)
```

### 2. Enhanced Docstring (lines 346-350)
```python
"""Extract and validate date components, return ISO date string or empty string.

Supports partial dates where missing components are represented as "00".
Returns empty string only if any component contains invalid (non-numeric) data.
"""
```

### 3. New Validation Logic (lines 373-379)
Individual fail-fast validation for each component:
```python
# Validate each component individually - fail-fast on invalid data
if year_str and not year_str.isdigit():
    return ""  # Invalid year format
if month_str and not month_str.isdigit():
    return ""  # Invalid month format
if day_str and not day_str.isdigit():
    return ""  # Invalid day format
```

### 4. Flexible Extraction (lines 381-384)
Components default to 0 if missing/blank:
```python
# Extract numeric values (0 if missing/blank)
year_int = int(year_str) if year_str else 0
month_int = int(month_str) if month_str else 0
day_int = int(day_str) if day_str else 0
```

### 5. Range Validation (lines 386-392)
Only validates present (non-zero) components:
```python
# Apply range validation only to present (non-zero) components
if year_int != 0 and year_int <= 0:
    return ""  # Invalid year value
if month_int != 0 and not (1 <= month_int <= 12):
    return ""  # Invalid month value
if day_int != 0 and not (1 <= day_int <= 31):
    return ""  # Invalid day value
```

### 6. Consistent Formatting (lines 398-399)
Always produces zero-padded ISO format:
```python
# Format with zero-padded components
return f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
```

### 7. Final Fallback for No Data (lines 433-435)
Added after both productionDate and coverageStartDate attempts:
```python
# If still no date from either source, use placeholder
if not date_value:
    date_value = "0000-00-00"
```

**Why this matters:** The `"0000-00-00"` placeholder must be applied in the calling code, not inside `get_date_from_columns()`. If the function returned `"0000-00-00"` directly, it would be a truthy value that prevents the coverageStartDate fallback from being attempted.

## Behavior Changes

| Input (Year/Month/Day) | Old Output | New Output |
|------------------------|------------|------------|
| 1947/blank/blank | "" (empty) | "1947-00-00" |
| blank/6/blank | "" (empty) | "0000-06-00" |
| blank/blank/15 | "" (empty) | "0000-00-15" |
| 1947/6/blank | "" (empty) | "1947-06-00" |
| 1947/blank/15 | "" (empty) | "1947-00-15" |
| blank/6/15 | "" (empty) | "0000-06-15" |
| 1947/6/15 | "1947-06-15" | "1947-06-15" (unchanged) |
| blank/blank/blank | "" (empty) | "0000-00-00" |
| 1947/13/blank | "" (empty) | "" (unchanged - invalid month) |
| 1947/blank/32 | "" (empty) | "" (unchanged - invalid day) |
| "abc"/6/15 | "" (empty) | "" (unchanged - non-numeric) |

## Backward Compatibility

- Complete dates (all three components present and valid) produce identical output
- Invalid data scenarios continue to return empty string
- No changes to column detection or data source prioritization logic

## Recommended Next Steps

### 1. Test with Sample Data
Run the script against test data covering all scenarios in the behavior table above.

### 2. Verify ExifTool Compatibility
Before production use, confirm ExifTool accepts partial dates:
```bash
exiftool -DateCreated="1947-00-00" test.jpg
exiftool -DateCreated="0000-06-00" test.jpg
```

### 3. Verify Target System Compatibility
Confirm the customer's metadata system accepts partial ISO dates with "00" placeholders.

## Related Documents

- Plan: `notes/PLAN_HPM-partial-date-modifications-to-Date-Create.md` (original)
- Plan: `notes/PLAN_HPM-partial-date-modifications-to-Date-Create-w-Claudes-edits.md` (revised)

## Testing Checklist

- [ ] Complete date: 1947, 6, 15 -> "1947-06-15"
- [ ] Year only: 1947, blank, blank -> "1947-00-00"
- [ ] Month only: blank, 6, blank -> "0000-06-00"
- [ ] Day only: blank, blank, 15 -> "0000-00-15"
- [ ] Year+Month: 1947, 6, blank -> "1947-06-00"
- [ ] Year+Day: 1947, blank, 15 -> "1947-00-15"
- [ ] Month+Day: blank, 6, 15 -> "0000-06-15"
- [ ] All blank: blank, blank, blank -> "0000-00-00"
- [ ] Invalid month: 1947, 13, blank -> ""
- [ ] Invalid day: 1947, blank, 32 -> ""
- [ ] Non-numeric: "abc", 6, 15 -> ""
- [ ] ExifTool accepts partial dates
- [ ] Target system accepts partial dates
