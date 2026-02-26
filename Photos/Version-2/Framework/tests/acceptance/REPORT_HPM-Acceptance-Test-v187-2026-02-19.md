# HPM Acceptance Test Report — v1.8.7

**Date:** 2026-02-19
**Version:** HPM 1.8.7
**Status:** PASS — All Tests Passing
**Total Tests:** 67 (64 fast + 3 slow)
**Execution Time:** 0.85s (fast) + 5.03s (launch) = 5.88s total

---

## Summary

| Metric | Result |
|--------|--------|
| Total tests | 67 |
| Passed | 67 |
| Failed | 0 |
| Skipped | 0 |
| Fast tests (non-slow) | 64 passed in 0.85s |
| Slow tests (launch) | 3 passed in 5.03s |
| HPM.exe size | 72 MB |
| Python | 3.12.10 |
| pytest | 9.0.2 |
| Platform | Windows 11 (win32) |

---

## Environment

```
Platform : Windows 11 (win32)
Python   : 3.12.10
pytest   : 9.0.2
Pillow   : (from .venv)
pytest   : 9.0.2, pluggy-1.6.0
HPM.exe  : dist/HPM.exe  (72 MB, built 2026-02-19)
```

---

## Test Results by Module

### test_asset_bundling.py — 10/10 PASSED

Verifies every source asset required by `HPM.spec` is present on disk and valid.

| Test | Result |
|------|--------|
| `TestWatermarkAsset::test_watermark_exists` | PASSED |
| `TestWatermarkAsset::test_watermark_is_valid_image` | PASSED |
| `TestWatermarkAsset::test_watermark_is_png` | PASSED |
| `TestExifToolAsset::test_exiftool_exists` | PASSED |
| `TestExifToolAsset::test_exiftool_is_file` | PASSED |
| `TestExifToolAsset::test_exiftool_runs_and_returns_version` | PASSED |
| `TestIconAssets::test_app_icon_exists` | PASSED |
| `TestIconAssets::test_app_icon_is_ico` | PASSED |
| `TestIconAssets::test_launcher_icon_exists` | PASSED |
| `TestSpecDatasConsistency::test_all_spec_data_sources_exist` | PASSED |

---

### test_exe_artifact.py — 11/11 PASSED

Validates the compiled artifact and release metadata without launching the EXE.

| Test | Result |
|------|--------|
| `TestExeFile::test_exe_exists` | PASSED |
| `TestExeFile::test_exe_is_file` | PASSED |
| `TestExeFile::test_exe_min_size_mb` | PASSED |
| `TestExeFile::test_exe_max_size_mb` | PASSED |
| `TestVersionConsistency::test_version_defined_in_init` | PASSED |
| `TestVersionConsistency::test_changelog_has_current_version` | PASSED |
| `TestVersionConsistency::test_changelog_entry_is_at_top` | PASSED |
| `TestSpecFile::test_spec_entry_point` | PASSED |
| `TestSpecFile::test_spec_bundles_watermark` | PASSED |
| `TestSpecFile::test_spec_bundles_exiftool` | PASSED |
| `TestSpecFile::test_spec_console_is_false` | PASSED |

---

### test_exe_launch.py — 3/3 PASSED  *(slow)*

Launches `HPM.exe` via subprocess and confirms it starts and terminates cleanly.

| Test | Result |
|------|--------|
| `TestExeLaunch::test_exe_launches_without_crash` | PASSED |
| `TestExeLaunch::test_exe_has_valid_pid` | PASSED |
| `TestExeLaunch::test_exe_terminates_cleanly` | PASSED |

EXE remained alive for the full 5-second startup window and terminated cleanly on request.

---

### test_jpeg_resize.py — 20/20 PASSED

Validates the Step 7 proportional JPEG resize algorithm across landscape, portrait,
square, and edge-case dimensions.

| Test | Result |
|------|--------|
| `TestResizeLandscape::test_landscape_wider_than_max_is_resized` | PASSED |
| `TestResizeLandscape::test_landscape_result_width_equals_max` | PASSED |
| `TestResizeLandscape::test_landscape_aspect_ratio_preserved` | PASSED |
| `TestResizeLandscape::test_wide_landscape_fits_in_max` | PASSED |
| `TestResizePortrait::test_portrait_taller_than_max_is_resized` | PASSED |
| `TestResizePortrait::test_portrait_result_height_equals_max` | PASSED |
| `TestResizePortrait::test_portrait_aspect_ratio_preserved` | PASSED |
| `TestResizeSquare::test_large_square_is_resized` | PASSED |
| `TestResizeSquare::test_large_square_stays_square` | PASSED |
| `TestResizeNoUpscaling::test_small_image_not_upscaled` | PASSED |
| `TestResizeNoUpscaling::test_exact_max_width_not_resized` | PASSED |
| `TestResizeNoUpscaling::test_exact_max_height_not_resized` | PASSED |
| `TestResizeNoUpscaling::test_exact_square_max_not_resized` | PASSED |
| `TestResizeOutputBounds::test_output_fits_within_max_dimension[1600-1067]` | PASSED |
| `TestResizeOutputBounds::test_output_fits_within_max_dimension[1067-1600]` | PASSED |
| `TestResizeOutputBounds::test_output_fits_within_max_dimension[1200-1200]` | PASSED |
| `TestResizeOutputBounds::test_output_fits_within_max_dimension[3840-2160]` | PASSED |
| `TestResizeOutputBounds::test_output_fits_within_max_dimension[2160-3840]` | PASSED |

---

### test_watermark_processing.py — 24/24 PASSED

Primary regression suite for issue #49 (copyright watermark aspect ratio distortion).
Covers the watermark source asset, output dimensions, proportional scale verification,
output format, opacity, and copyright-notice detection logic.

| Test | Result |
|------|--------|
| `TestWatermarkSourceAsset::test_watermark_png_exists` | PASSED |
| `TestWatermarkSourceAsset::test_watermark_png_has_alpha_channel` | PASSED |
| `TestWatermarkSourceAsset::test_watermark_png_is_square` | PASSED |
| `TestWatermarkSourceAsset::test_watermark_png_is_800px` | PASSED |
| `TestWatermarkSourceAsset::test_watermark_has_transparent_pixels` | PASSED |
| `TestWatermarkOutputDimensions::test_square_image_output_dimensions` | PASSED |
| `TestWatermarkOutputDimensions::test_landscape_image_output_dimensions` | PASSED |
| `TestWatermarkOutputDimensions::test_portrait_image_output_dimensions` | PASSED |
| `TestWatermarkOutputDimensions::test_wide_landscape_output_dimensions` | PASSED |
| `TestWatermarkOutputDimensions::test_tall_portrait_output_dimensions` | PASSED |
| `TestWatermarkAspectRatio::test_landscape_uses_proportional_scale` | PASSED |
| `TestWatermarkAspectRatio::test_portrait_uses_proportional_scale` | PASSED |
| `TestWatermarkAspectRatio::test_stretch_would_have_failed` | PASSED |
| `TestWatermarkOutputFormat::test_output_is_rgb` | PASSED |
| `TestWatermarkOutputFormat::test_output_differs_from_input` | PASSED |
| `TestWatermarkOpacity::test_high_opacity_more_visible_than_low` | PASSED |
| `TestWatermarkOpacity::test_zero_opacity_is_ignored` | PASSED |
| `TestCopyrightDetection::test_restricted_detected` | PASSED |
| `TestCopyrightDetection::test_restricted_case_insensitive` | PASSED |
| `TestCopyrightDetection::test_unrestricted_excluded` | PASSED |
| `TestCopyrightDetection::test_unrestricted_case_insensitive` | PASSED |
| `TestCopyrightDetection::test_empty_string_not_restricted` | PASSED |
| `TestCopyrightDetection::test_none_not_restricted` | PASSED |
| `TestCopyrightDetection::test_unrelated_text_not_restricted` | PASSED |
| `TestCopyrightDetection::test_partial_word_not_matched` | PASSED |

---

## Issue #49 Regression Confirmation

The three `TestWatermarkAspectRatio` tests specifically verify the fix committed in
v1.8.7 for [issue #49 — Copyright Watermark Aspect Ratio](https://github.com/juren53/HST-Metadata/issues/49).

**Root cause (confirmed by `test_stretch_would_have_failed`):**
The old algorithm called `watermark.resize((img_width, img_height))`, which used
independent x/y scale factors:
- For an 800×533 landscape image: `x_scale = 800/800 = 1.0`, `y_scale = 533/800 = 0.667`
- Different scale factors → "COPYRIGHT" text compressed vertically

**Fix (confirmed by `test_landscape_uses_proportional_scale` and
`test_portrait_uses_proportional_scale`):**
The new algorithm uses `scale = max(img_width, img_height) / max(wm_w, wm_h)` — a
single uniform scale factor — then crops to the image dimensions:
- For an 800×533 landscape: `scale = 800/800 = 1.0` → intermediate 800×800, crop to 800×533
- For a 533×800 portrait: `scale = 800/800 = 1.0` → intermediate 800×800, crop to 533×800
- Both axes use the same scale factor → text proportions preserved

---

## pytest Console Output

### Fast tests (64 tests)

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\juren\Projects\HST-Metadata\Photos\Version-2\Framework
configfile: pyproject.toml
plugins: mock-3.15.1
collected 67 items / 3 deselected / 64 selected

....................................................................[100%]

====================== 64 passed, 3 deselected in 0.85s =======================
```

### Launch tests (3 slow tests)

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\juren\Projects\HST-Metadata\Photos\Version-2\Framework
configfile: pyproject.toml
plugins: mock-3.15.1
collected 3 items

tests/acceptance/test_exe_launch.py::TestExeLaunch::test_exe_launches_without_crash PASSED [ 33%]
tests/acceptance/test_exe_launch.py::TestExeLaunch::test_exe_has_valid_pid          PASSED [ 66%]
tests/acceptance/test_exe_launch.py::TestExeLaunch::test_exe_terminates_cleanly     PASSED [100%]

============================== 3 passed in 5.03s ==============================
```

---

## Run Commands Used

```bash
# Fast tests
pytest tests/acceptance/ -m "acceptance and not slow" -v

# Launch smoke tests
pytest tests/acceptance/test_exe_launch.py -m "acceptance" -v
```
