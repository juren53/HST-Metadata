# Analysis: IPTC Standards and ExifTool Metadata Tagging

## Problem Statement

During Step 5 of HPM processing, certain fields in export.csv (notably Source
and By-line) are truncated when embedded into TIFF images. The truncation is
not caused by the Python code, which passes values to ExifTool without any
length checks. The truncation occurs because **ExifTool enforces IPTC IIM
field length limits** when writing to IPTC tags.

## Current ExifTool Command (step5_dialog.py, lines 206-220)

```python
et.execute(
    "-overwrite_original_in_place",
    "-IPTC:CodedCharacterSet=UTF8",
    f"-Headline={row.get('Headline', '')}",
    "-Credit=Harry S. Truman Library",
    f"-By-line={row.get('By-line', '')}",
    f"-SpecialInstructions={row.get('SpecialInstructions', '')}",
    f"-ObjectName={row.get('ObjectName', '')}",
    f"-Source={row.get('Source', '')}",
    f"-Caption-Abstract={row.get('Caption-Abstract', '')}",
    f"-DateCreated={converted_date}",
    f"-CopyrightNotice={row.get('CopyrightNotice', '')}",
    f"-By-lineTitle={row.get('By-lineTitle', '')}",
    str(dest_path)
)
```

Tags are written without an explicit group prefix (except CodedCharacterSet).
ExifTool resolves these to IPTC as the preferred group, meaning only IPTC IIM
tags are written. IPTC IIM has strict byte-length limits per field.

---

## IPTC IIM Field Length Limits

These limits are from the **IPTC IIM Specification v4.2** (frozen since 1997).
Limits are in **bytes, not characters** -- UTF-8 non-ASCII characters consume
2-4 bytes each, so the effective character count may be lower.

| DataSet | IPTC IIM Tag Name    | Max Bytes | Risk Level     |
|---------|----------------------|-----------|----------------|
| 2:05    | ObjectName           | 64        | Low            |
| 2:40    | SpecialInstructions  | 256       | Low            |
| 2:55    | DateCreated          | 8 digits  | None (fixed)   |
| 2:80    | **By-line**          | **32**    | **HIGH**       |
| 2:85    | **By-lineTitle**     | **32**    | **HIGH**       |
| 2:105   | Headline             | 256       | Low            |
| 2:110   | **Credit**           | **32**    | Low (hardcoded)|
| 2:115   | **Source**            | **32**    | **HIGH**       |
| 2:116   | CopyrightNotice      | 128       | Medium         |
| 2:120   | Caption-Abstract     | 2000      | Low            |

**Fields most at risk of truncation:**
- **Source (32 bytes)** -- collection names frequently exceed 32 characters
- **By-line (32 bytes)** -- photographer names can exceed 32 characters
- **By-lineTitle (32 bytes)** -- institutional creator names can be long
- Credit (32 bytes) -- currently hardcoded to "Harry S. Truman Library" (23 chars, safe)

---

## ExifTool Truncation Behavior

When a value exceeds the IPTC IIM byte limit, ExifTool:

1. Issues a **minor warning**: `Warning: [Minor] IPTC:By-line exceeds length limit (truncated)`
2. **Truncates** the value to fit within the limit
3. The operation **succeeds** -- it does not error or abort

The `-m` flag (IgnoreMinorErrors) can suppress the warning and write the
full value, but non-conforming IPTC values may cause problems in other
software.

---

## XMP Equivalents (No Length Limits)

XMP (Extensible Metadata Platform) is the modern replacement for IPTC IIM.
XMP fields are stored as XML and have **no practical length limits**.

| IPTC IIM Tag         | XMP Equivalent                     | XMP Namespace     |
|----------------------|------------------------------------|-------------------|
| ObjectName           | `XMP-dc:Title`                     | Dublin Core       |
| SpecialInstructions  | `XMP-photoshop:Instructions`       | Adobe Photoshop   |
| DateCreated          | `XMP-photoshop:DateCreated`        | Adobe Photoshop   |
| By-line              | `XMP-dc:Creator`                   | Dublin Core       |
| By-lineTitle         | `XMP-photoshop:AuthorsPosition`    | Adobe Photoshop   |
| Headline             | `XMP-photoshop:Headline`           | Adobe Photoshop   |
| Credit               | `XMP-photoshop:Credit`             | Adobe Photoshop   |
| Source               | `XMP-photoshop:Source`             | Adobe Photoshop   |
| CopyrightNotice      | `XMP-dc:Rights`                    | Dublin Core       |
| Caption-Abstract     | `XMP-dc:Description`               | Dublin Core       |

**Note:** `XMP-dc:Title`, `XMP-dc:Rights`, and `XMP-dc:Description` are
**lang-alt** type tags (language alternatives). `XMP-dc:Creator` is a
**list** (bag) type tag.

---

## Fix Options

### Option 1: Write Both IPTC + XMP (Recommended)

Keep existing IPTC tags for backward compatibility and add explicit XMP tags
to store full-length values. Tools that support XMP (Adobe products, modern
DAM systems) will read the complete data.

```python
et.execute(
    "-overwrite_original_in_place",
    "-IPTC:CodedCharacterSet=UTF8",
    # IPTC tags (may be truncated at IPTC limits)
    f"-IPTC:Headline={headline}",
    "-IPTC:Credit=Harry S. Truman Library",
    f"-IPTC:By-line={byline}",
    f"-IPTC:SpecialInstructions={special}",
    f"-IPTC:ObjectName={objectname}",
    f"-IPTC:Source={source}",
    f"-IPTC:Caption-Abstract={caption}",
    f"-IPTC:DateCreated={date}",
    f"-IPTC:CopyrightNotice={copyright}",
    f"-IPTC:By-lineTitle={bylinetitle}",
    # XMP tags (no length limits, full values preserved)
    f"-XMP-photoshop:Headline={headline}",
    "-XMP-photoshop:Credit=Harry S. Truman Library",
    f"-XMP-dc:Creator={byline}",
    f"-XMP-photoshop:Instructions={special}",
    f"-XMP-dc:Title={objectname}",
    f"-XMP-photoshop:Source={source}",
    f"-XMP-dc:Description={caption}",
    f"-XMP-photoshop:DateCreated={date}",
    f"-XMP-dc:Rights={copyright}",
    f"-XMP-photoshop:AuthorsPosition={bylinetitle}",
    str(dest_path)
)
```

**Pros:** Maximum compatibility. Older IPTC-only tools see truncated but
valid data. Modern XMP-aware tools see complete data.

**Cons:** Slight increase in file size from storing metadata twice. ExifTool
will still issue minor warnings for truncated IPTC values.

### Option 2: Switch to XMP Only

Replace IPTC tags with XMP equivalents entirely. No length limits apply.

**Pros:** Simple, no truncation, modern standard.

**Cons:** Older tools and workflows that only read IPTC will not see the
metadata.

### Option 3: Use ExifTool -m Flag

Add `-m` to suppress minor errors and allow over-length IPTC writes.

**Pros:** Minimal code change.

**Cons:** Non-conforming IPTC data may cause issues in downstream tools.
Not a standards-compliant solution.

---

## ExifTool Tag Resolution Without Group Prefix

When tags are written without a group prefix (e.g., `-Headline=...` instead
of `-IPTC:Headline=...`), ExifTool resolves to the highest-priority group:
**EXIF > IPTC > XMP**. Since the tag names used in Step 5 are native IPTC
names, they resolve to IPTC by default.

ExifTool does **not** automatically write to both IPTC and XMP. To write to
both, you must explicitly specify both group prefixes.

---

## References

- [ExifTool IPTC Tags](https://exiftool.org/TagNames/IPTC.html)
- [ExifTool XMP Tags](https://exiftool.org/TagNames/XMP.html)
- [ExifTool Writing Meta Information](https://exiftool.org/writing.html)
- [IPTC IIM Specification v4.2](https://www.iptc.org/std/IIM/4.2/specification/IIMV4.2.pdf)
- [IPTC Photo Metadata Standard 2024.1](https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata)
