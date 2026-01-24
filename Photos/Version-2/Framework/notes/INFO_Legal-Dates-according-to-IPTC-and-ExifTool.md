## INFO_Legal-Dates-according-to-IPTC-and-ExifTool.md

IPTC metadata standard specifications regarding date formats.

Based on the IPTC metadata specification, here's what's legal for dates:

## Legal Date Formats in IPTC

**For XMP format (preferred):**
IPTC follows **ISO 8601** and supports **truncated dates**:
- `2025` (year only)
- `2025-04` (year and month)
- `2025-04-15` (complete date)
- Full date-times with timezone

**For IIM format (legacy):**
The IPTC specification explicitly states: *"Software embedding truncated dates as IIM DataSet 2:55 should use the value '00' for undefined days or months (like '19180000' for an image taken 'in the year 1918')"*

## Your Specific Questions:

**Is `2025-04-00` legal?**
- **NO** - This is NOT valid ISO 8601 or proper XMP format
- **Correct alternatives:** Use `2025-04` (truncated to year-month) or `2025-04-01` if you need to pick a day

**Is `0000-00-00` legal?**
- **NO** - This is not a valid date in any format
- **For XMP:** There's no meaningful way to represent "completely unknown date"
- **For IIM:** `00000000` might technically work to indicate "unknown" but is not recommended

## Best Practices:

1. **For unknown month/day in XMP:** Use truncated dates (`1984` or `1984-04`)
2. **For unknown entire date:** Leave the field empty rather than using zeros
3. **For IIM format only:** You can use `19840000` (year only known) or `19840400` (year and month known, day unknown)

**Important caveat:** Many software applications (Lightroom, ACDSee, etc.) don't properly handle the `00` convention even though it's in the IPTC spec, so truncated ISO 8601 dates in XMP are the safer choice for your HST-Metadata project.

## How ExifTool handles truncated dates:

## ExifTool's Approach to Truncated Dates

### For XMP Format (Modern/Recommended):
ExifTool **supports** ISO 8601 truncated dates in XMP fields:
- `XMP-photoshop:DateCreated` can accept:
  - `1984` (year only)
  - `1984-03` (year and month)
  - `1984-03-15` (complete date)
  - Full date-times with timezone

### For IPTC IIM Format (Legacy):
ExifTool's behavior is **more problematic**:

**Reading:** ExifTool will read `19840000` (the "00 convention" for unknown month/day) from IIM fields, but software compatibility varies widely.

**Writing:** ExifTool defines `IPTC:DateCreated` as `digits[8]`, requiring exactly 8 digits in `YYYYMMDD` format. Based on the forum discussions I found:
- ExifTool **can technically write** `19840000` for year-only dates
- However, this causes **compatibility problems** with many applications (Lightroom, ACDSee, Apple Photos, etc.) which either:
  - Reject the value entirely
  - Display incorrect dates
  - Strip the field on export

## Practical Recommendations for Your HST-Metadata Project:

**Best Practice: Use XMP, not IIM**
```python
# For year-only dates
exiftool -XMP-photoshop:DateCreated="1984" image.tif

# For year and month
exiftool -XMP-photoshop:DateCreated="1984-03" image.tif
```

**If you must use IIM format:**
- Be aware that `19840000` is technically valid per IPTC spec
- But it will cause problems with most modern software
- Consider **also** writing the XMP equivalent for better compatibility

**Tool Command Examples:**
```bash
# Write truncated date to XMP (recommended)
exiftool -XMP-photoshop:DateCreated="1918" historical_photo.jpg

# Write both IIM and XMP for maximum compatibility
exiftool -IPTC:DateCreated="19180000" -XMP-photoshop:DateCreated="1918" photo.jpg
```

For your historical photograph project, I'd strongly recommend sticking with XMP's ISO 8601 truncated dates rather than the IIM "00 convention" to avoid software compatibility headaches.