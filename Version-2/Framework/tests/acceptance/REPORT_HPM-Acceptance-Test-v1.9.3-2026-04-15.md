# HPM Acceptance Test Report — v1.9.3

**Date:** 2026-04-15  
**Time:** 03:34:25  
**Status:** ALL PASSING  
**Total Tests:** 66 (66 passed, 0 failed, 0 skipped)  
**Execution Time:** 2.0s  

---

## Results by Module

### `test_asset_bundling.py` — 10 tests  (10 passed, 0 failed, 0 skipped)

| Result | Test | Duration |
|--------|------|----------|
| PASS | `TestWatermarkAsset::test_watermark_exists` | 0.00s |
| PASS | `TestWatermarkAsset::test_watermark_is_valid_image` | 0.01s |
| PASS | `TestWatermarkAsset::test_watermark_is_png` | 0.00s |
| PASS | `TestExifToolAsset::test_exiftool_exists` | 0.00s |
| PASS | `TestExifToolAsset::test_exiftool_is_file` | 0.00s |
| PASS | `TestExifToolAsset::test_exiftool_runs_and_returns_version` | 1.30s |
| PASS | `TestIconAssets::test_app_icon_exists` | 0.00s |
| PASS | `TestIconAssets::test_app_icon_is_ico` | 0.00s |
| PASS | `TestIconAssets::test_launcher_icon_exists` | 0.00s |
| PASS | `TestSpecDatasConsistency::test_all_spec_data_sources_exist` | 0.00s |

### `test_exe_artifact.py` — 13 tests  (13 passed, 0 failed, 0 skipped)

| Result | Test | Duration |
|--------|------|----------|
| PASS | `TestExeFile::test_exe_exists` | 0.00s |
| PASS | `TestExeFile::test_exe_is_file` | 0.00s |
| PASS | `TestExeFile::test_exe_min_size_mb` | 0.00s |
| PASS | `TestExeFile::test_exe_max_size_mb` | 0.00s |
| PASS | `TestVersionConsistency::test_version_defined_in_init` | 0.00s |
| PASS | `TestVersionConsistency::test_changelog_has_current_version` | 0.00s |
| PASS | `TestVersionConsistency::test_changelog_entry_is_at_top` | 0.00s |
| PASS | `TestExeBundledModules::test_ftfy_bundled` | 0.03s |
| PASS | `TestExeBundledModules::test_ftfy_submodules_bundled` | 0.08s |
| PASS | `TestSpecFile::test_spec_entry_point` | 0.00s |
| PASS | `TestSpecFile::test_spec_bundles_watermark` | 0.00s |
| PASS | `TestSpecFile::test_spec_bundles_exiftool` | 0.00s |
| PASS | `TestSpecFile::test_spec_console_is_false` | 0.00s |

### `test_jpeg_resize.py` — 18 tests  (18 passed, 0 failed, 0 skipped)

| Result | Test | Duration |
|--------|------|----------|
| PASS | `TestResizeLandscape::test_landscape_wider_than_max_is_resized` | 0.02s |
| PASS | `TestResizeLandscape::test_landscape_result_width_equals_max` | 0.02s |
| PASS | `TestResizeLandscape::test_landscape_aspect_ratio_preserved` | 0.01s |
| PASS | `TestResizeLandscape::test_wide_landscape_fits_in_max` | 0.02s |
| PASS | `TestResizePortrait::test_portrait_taller_than_max_is_resized` | 0.01s |
| PASS | `TestResizePortrait::test_portrait_result_height_equals_max` | 0.02s |
| PASS | `TestResizePortrait::test_portrait_aspect_ratio_preserved` | 0.02s |
| PASS | `TestResizeSquare::test_large_square_is_resized` | 0.00s |
| PASS | `TestResizeSquare::test_large_square_stays_square` | 0.02s |
| PASS | `TestResizeNoUpscaling::test_small_image_not_upscaled` | 0.00s |
| PASS | `TestResizeNoUpscaling::test_exact_max_width_not_resized` | 0.00s |
| PASS | `TestResizeNoUpscaling::test_exact_max_height_not_resized` | 0.00s |
| PASS | `TestResizeNoUpscaling::test_exact_square_max_not_resized` | 0.00s |
| PASS | `TestResizeOutputBounds::test_output_fits_within_max_dimension[1600-1067]` | 0.02s |
| PASS | `TestResizeOutputBounds::test_output_fits_within_max_dimension[1067-1600]` | 0.01s |
| PASS | `TestResizeOutputBounds::test_output_fits_within_max_dimension[1200-1200]` | 0.02s |
| PASS | `TestResizeOutputBounds::test_output_fits_within_max_dimension[3840-2160]` | 0.06s |
| PASS | `TestResizeOutputBounds::test_output_fits_within_max_dimension[2160-3840]` | 0.06s |

### `test_watermark_processing.py` — 25 tests  (25 passed, 0 failed, 0 skipped)

| Result | Test | Duration |
|--------|------|----------|
| PASS | `TestWatermarkSourceAsset::test_watermark_png_exists` | 0.00s |
| PASS | `TestWatermarkSourceAsset::test_watermark_png_has_alpha_channel` | 0.00s |
| PASS | `TestWatermarkSourceAsset::test_watermark_png_is_square` | 0.00s |
| PASS | `TestWatermarkSourceAsset::test_watermark_png_is_800px` | 0.00s |
| PASS | `TestWatermarkSourceAsset::test_watermark_has_transparent_pixels` | 0.02s |
| PASS | `TestWatermarkOutputDimensions::test_square_image_output_dimensions` | 0.00s |
| PASS | `TestWatermarkOutputDimensions::test_landscape_image_output_dimensions` | 0.02s |
| PASS | `TestWatermarkOutputDimensions::test_portrait_image_output_dimensions` | 0.02s |
| PASS | `TestWatermarkOutputDimensions::test_wide_landscape_output_dimensions` | 0.00s |
| PASS | `TestWatermarkOutputDimensions::test_tall_portrait_output_dimensions` | 0.02s |
| PASS | `TestWatermarkAspectRatio::test_landscape_uses_proportional_scale` | 0.00s |
| PASS | `TestWatermarkAspectRatio::test_portrait_uses_proportional_scale` | 0.00s |
| PASS | `TestWatermarkAspectRatio::test_stretch_would_have_failed` | 0.00s |
| PASS | `TestWatermarkOutputFormat::test_output_is_rgb` | 0.00s |
| PASS | `TestWatermarkOutputFormat::test_output_differs_from_input` | 0.05s |
| PASS | `TestWatermarkOpacity::test_high_opacity_more_visible_than_low` | 0.11s |
| PASS | `TestWatermarkOpacity::test_zero_opacity_is_ignored` | 0.03s |
| PASS | `TestCopyrightDetection::test_restricted_detected` | 0.00s |
| PASS | `TestCopyrightDetection::test_restricted_case_insensitive` | 0.00s |
| PASS | `TestCopyrightDetection::test_unrestricted_excluded` | 0.00s |
| PASS | `TestCopyrightDetection::test_unrestricted_case_insensitive` | 0.02s |
| PASS | `TestCopyrightDetection::test_empty_string_not_restricted` | 0.00s |
| PASS | `TestCopyrightDetection::test_none_not_restricted` | 0.00s |
| PASS | `TestCopyrightDetection::test_unrelated_text_not_restricted` | 0.00s |
| PASS | `TestCopyrightDetection::test_partial_word_not_matched` | 0.00s |

---

*Generated automatically by `tests/acceptance/conftest.py` on 2026-04-15 at 03:34:25.*
