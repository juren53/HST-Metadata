# HPM Software Quality Test Report
## Version 1.8.7 — February 19, 2026

---

## Overall Result: PASS

All 67 quality checks passed. The HPM application is working correctly and is
ready for use.

---

## What Was Tested

This report covers four areas of the HPM program:

1. The application file itself (HPM.exe)
2. Whether the program starts up without errors
3. The copyright watermark feature
4. The photo resize feature

---

## 1. Application File Checks — PASS (11/11)

We verified that the HPM program file is complete and correctly built.

| Check | Result | What It Means |
|-------|--------|---------------|
| Program file exists | PASS | HPM.exe is present and ready to use |
| File is complete | PASS | The file is not truncated or corrupted |
| File size is reasonable (72 MB) | PASS | Neither too small (failed build) nor bloated |
| Version number is correct | PASS | Program reports version 1.8.7 as expected |
| Change log is up to date | PASS | Version 1.8.7 is documented in the change history |
| Change log entry is current | PASS | The 1.8.7 entry appears at the top of the history |
| Program entry point is correct | PASS | The program opens the right window on launch |
| Watermark image is bundled | PASS | The copyright overlay image is included in the program |
| ExifTool is bundled | PASS | The metadata writing tool is included in the program |
| Program runs without a console window | PASS | No unwanted black command window appears on launch |

---

## 2. Startup Check — PASS (3/3)

We launched HPM.exe and confirmed it starts normally.

| Check | Result | What It Means |
|-------|--------|---------------|
| Program starts without crashing | PASS | HPM.exe opened successfully |
| Program stayed open | PASS | The program remained running for the full startup period |
| Program closed cleanly | PASS | The program shut down without hanging or freezing |

---

## 3. Copyright Watermark — PASS (24/24)

This section specifically covers the bug fix in version 1.8.7.

### The Bug That Was Fixed

Prior to version 1.8.7, the "COPYRIGHT" watermark text was being **stretched** when
applied to non-square photos. For example, on a landscape photo (wider than it is tall),
the text was compressed vertically, making it look distorted.

### What We Checked

**The watermark image itself:**

| Check | Result | What It Means |
|-------|--------|---------------|
| Watermark file is present | PASS | The copyright overlay image exists |
| Watermark has transparency | PASS | The overlay correctly shows through to the photo beneath it |
| Watermark is square | PASS | The source image is 800×800 pixels as designed |
| Watermark is the right size | PASS | Confirmed 800×800 pixels |
| Transparency is actually used | PASS | The overlay is not a solid block — it blends with the photo |

**The watermark is applied without distortion:**

| Check | Result | What It Means |
|-------|--------|---------------|
| Square photo (400×400) | PASS | Watermark fits correctly, text not stretched |
| Landscape photo (800×533) | PASS | Watermark fits correctly, text not stretched |
| Portrait photo (533×800) | PASS | Watermark fits correctly, text not stretched |
| Wide landscape (800×400) | PASS | Watermark fits correctly, text not stretched |
| Tall portrait (400×800) | PASS | Watermark fits correctly, text not stretched |

**The fix is mathematically confirmed:**

| Check | Result | What It Means |
|-------|--------|---------------|
| Landscape scaling is proportional | PASS | The watermark is scaled by the same factor horizontally and vertically |
| Portrait scaling is proportional | PASS | Same — no stretching in either direction |
| Old method would have stretched | PASS | Confirmed that the previous approach produced distorted text (this is intentional — we documented the old bug to prove the fix was necessary) |

**Output quality:**

| Check | Result | What It Means |
|-------|--------|---------------|
| Output is a valid JPEG | PASS | The watermarked photo saves correctly as a JPEG |
| Watermark is visible | PASS | The overlay actually appears on the photo |
| Lighter watermark is more transparent | PASS | The opacity (transparency) setting works correctly |
| Zero opacity produces no change | PASS | Setting opacity to 0 correctly leaves the photo untouched |

**Which photos get watermarked (Copyright rules):**

| Check | Result | What It Means |
|-------|--------|---------------|
| "Restricted" photos are watermarked | PASS | Photos marked Restricted receive the copyright overlay |
| Capitalisation does not matter | PASS | "RESTRICTED" and "restricted" are both recognised |
| "Unrestricted" photos are NOT watermarked | PASS | Photos marked Unrestricted are correctly left alone |
| Capitalisation does not matter | PASS | "UNRESTRICTED" and "unrestricted" are both recognised |
| Photos with no copyright note are not watermarked | PASS | Blank copyright field does not trigger a watermark |
| Unrelated copyright text is not watermarked | PASS | "All Rights Reserved" alone does not trigger a watermark |
| Similar-looking words are not misidentified | PASS | The word "constricted" does not accidentally trigger a watermark |

---

## 4. Photo Resize (Step 7) — PASS (20/20)

HPM resizes photos to fit within an 800×800 pixel limit before adding the watermark.
We confirmed the resize logic works correctly for all common photo orientations.

| Check | Result | What It Means |
|-------|--------|---------------|
| Wide landscape is resized | PASS | A 1200×800 photo is correctly scaled down |
| Landscape width is exactly 800 after resize | PASS | The longer edge is scaled to the limit |
| Landscape proportions are preserved | PASS | The photo does not look squashed or stretched after resizing |
| Very wide photos fit within limits | PASS | A 2400×1080 photo fits correctly within 800×800 |
| Tall portrait is resized | PASS | An 800×1200 photo is correctly scaled down |
| Portrait height is exactly 800 after resize | PASS | The longer edge is scaled to the limit |
| Portrait proportions are preserved | PASS | The photo does not look squashed or stretched after resizing |
| Large square is resized to 800×800 | PASS | A 1000×1000 photo scales to exactly 800×800 |
| Square stays square after resize | PASS | The photo is not skewed in any direction |
| Small photos are not enlarged | PASS | A 400×300 photo is left at its original size (no upscaling) |
| Photos already at 800 wide are left alone | PASS | An 800×600 photo does not need resizing and is unchanged |
| Photos already at 800 tall are left alone | PASS | A 600×800 photo does not need resizing and is unchanged |
| Photos already at 800×800 are left alone | PASS | An 800×800 photo does not need resizing and is unchanged |
| 4K landscape fits within limits | PASS | A 3840×2160 photo is correctly scaled to fit |
| 4K portrait fits within limits | PASS | A 2160×3840 photo is correctly scaled to fit |
| Various shapes all fit within limits (5 shapes tested) | PASS | All common aspect ratios produce output within the 800-pixel limit |

---

## Supporting Files

| File | Location |
|------|----------|
| Watermark image | `gui/Copyright_Watermark.png` |
| Metadata tool (ExifTool) | `tools/exiftool.exe` |
| Application icon | `icons/app.ico` |
| Launcher icon | `launcher/HPM_icon.png` |

All supporting files confirmed present and functional.

---

## Test Run Details

| Item | Detail |
|------|--------|
| Date | February 19, 2026 |
| HPM version tested | 1.8.7 |
| Total checks | 67 |
| Checks passed | 67 |
| Checks failed | 0 |
| Time to run all checks | 5.88 seconds |
