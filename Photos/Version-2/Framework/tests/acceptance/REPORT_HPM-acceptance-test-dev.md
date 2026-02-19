# HPM EXE Acceptance Test Suite — Development Report

**Date:** 2026-02-19
**Status:** All Tests Passing
**Total Tests:** 64 (non-slow) + 3 (slow/launch)
**Execution Time:** < 1 second (non-slow), ~15 seconds (with launch tests)
**Related Issue:** [#49 — Copyright Watermark Aspect Ratio](https://github.com/juren53/HST-Metadata/issues/49)

---

## Background

The existing `tests/` suite (296 tests, phases 2.5.1–2.5.4) validates HPM's Python source
code.  It cannot be run against the compiled `HPM.exe` because:

- Unit tests `import` Python modules directly — PyInstaller freezes these as bytecode
  inside the EXE, making them unreachable from outside.
- Integration tests invoke `hstl_framework.py` via subprocess — the EXE is a windowed
  GUI application (`console=False`) with no CLI entry point.
- GUI tests instantiate PyQt6 classes via `pytest-qt` — impossible against a sealed binary.

The acceptance suite was created to fill this gap.  It treats `HPM.exe` as a **black box**
and answers a different question: *does the compiled artifact work correctly as a
deployable application?*

---

## Design Principles

1. **No pywinauto / GUI automation** — fragile, platform-dependent, high maintenance cost.
2. **Output-file verification** — test what the processing algorithms *produce*, not how
   the GUI looks.
3. **Algorithm mirrors** — `conftest.py` contains standalone Python functions that
   replicate the exact Pillow-based logic frozen inside the EXE (`apply_watermark`,
   `resize_jpeg`, `is_restricted`).  If source algorithms change, update the mirrors too.
4. **Fast by default** — the 64 non-slow tests complete in under 1 second.  Launch smoke
   tests are isolated behind `@pytest.mark.slow`.
5. **Follows existing project conventions** — pytest classes, markers, temp-dir fixtures,
   and file layout consistent with the rest of `tests/`.

---

## Test Results

| Metric | Value |
|--------|-------|
| Total tests (non-slow) | 64 |
| Total tests (including slow) | 67 |
| Pass rate | 100% |
| Execution time (non-slow) | < 1 second |
| Execution time (all) | ~15 seconds |

---

## Test Modules

### `test_exe_artifact.py` — 11 tests

Verifies the compiled artifact and release metadata without launching the EXE.

| Class | Tests | What is verified |
|-------|-------|-----------------|
| `TestExeFile` | 4 | `dist/HPM.exe` exists, is a file, is 50–300 MB |
| `TestVersionConsistency` | 3 | `__version__` in `__init__.py` is a valid semver; CHANGELOG has a matching entry; that entry is at the top |
| `TestSpecFile` | 4 | `HPM.spec` references `hstl_gui.py` as entry point; bundles `Copyright_Watermark.png` and `exiftool.exe`; sets `console=False` |

---

### `test_exe_launch.py` — 3 tests (slow)

Launches `HPM.exe` as a subprocess and confirms it starts without crashing.

| Test | What is verified |
|------|-----------------|
| `test_exe_launches_without_crash` | Process is still alive after 5-second startup wait |
| `test_exe_has_valid_pid` | Subprocess received a valid positive PID |
| `test_exe_terminates_cleanly` | `process.terminate()` stops the EXE within 10 seconds |

The module fixture launches the EXE once (`scope='module'`) and tears it down after all
three tests, keeping total wall-clock time to ~15 seconds.

---

### `test_watermark_processing.py` — 24 tests

Primary regression suite for **issue #49** (watermark aspect ratio distortion).

| Class | Tests | What is verified |
|-------|-------|-----------------|
| `TestWatermarkSourceAsset` | 5 | PNG exists; has alpha channel (LA or RGBA mode); is square 800×800; alpha channel is actually used |
| `TestWatermarkOutputDimensions` | 5 | Output image dimensions equal input dimensions for square, landscape, portrait, wide landscape, tall portrait |
| `TestWatermarkAspectRatio` | 3 | Landscape scale is uniform (800×800 intermediate, then crop); portrait scale is uniform; the *old* broken algorithm demonstrably used non-uniform scale factors |
| `TestWatermarkOutputFormat` | 2 | Output mode is RGB; watermarked image differs from original |
| `TestWatermarkOpacity` | 2 | High opacity produces more pixel change than low; zero opacity is a no-op |
| `TestCopyrightDetection` | 8 | `is_restricted()` logic: "Restricted" detected, "Unrestricted" excluded, empty/None not restricted, unrelated text not matched, partial-word false-positive check |

The `test_stretch_would_have_failed` test explicitly documents the bug:
the old `watermark.resize((img_width, img_height))` call used
`x_scale = 800/800 = 1.0` and `y_scale = 533/800 = 0.667` — different factors for
landscape images, stretching the "COPYRIGHT" text vertically.

---

### `test_jpeg_resize.py` — 20 tests

Validates the Step 7 proportional JPEG resize algorithm.

| Class | Tests | What is verified |
|-------|-------|-----------------|
| `TestResizeLandscape` | 4 | Wide images (1200×800) are downscaled; result width equals `max_dimension`; aspect ratio preserved; fits within bounds |
| `TestResizePortrait` | 3 | Tall images (800×1200) are downscaled; result height equals `max_dimension`; aspect ratio preserved |
| `TestResizeSquare` | 2 | Large squares (1000×1000) scale to `max_dimension × max_dimension`; result remains square |
| `TestResizeNoUpscaling` | 4 | Images already within 800×800 are returned unchanged (400×300, 800×600, 600×800, 800×800) |
| `TestResizeOutputBounds` | 5 (parametrized) | Various input shapes (3:2, 2:3, 1:1, 4K landscape, 4K portrait) all produce output ≤ 800 on both axes |

---

### `test_asset_bundling.py` — 10 tests

Verifies every source file that PyInstaller needs for bundling is present and valid.

| Class | Tests | What is verified |
|-------|-------|-----------------|
| `TestWatermarkAsset` | 3 | `gui/Copyright_Watermark.png` exists; PIL can open it without error; has `.png` extension |
| `TestExifToolAsset` | 3 | `tools/exiftool.exe` exists and is a file; `exiftool -ver` exits 0 and prints a version string |
| `TestIconAssets` | 3 | `icons/app.ico` and `launcher/HPM_icon.png` exist with correct extensions |
| `TestSpecDatasConsistency` | 1 | Every source path in `HPM.spec` datas exists on disk |

---

## How to Run

```bash
# Fast tests only — all 64, < 1 second (recommended for CI / pre-build checks)
pytest tests/acceptance/ -m "acceptance and not slow"

# All acceptance tests including EXE launch (~15 seconds, requires display)
pytest tests/acceptance/ -m "acceptance"

# Issue #49 regression tests only
pytest tests/acceptance/test_watermark_processing.py -k "aspect"

# Verbose output
pytest tests/acceptance/ -m "acceptance and not slow" -v

# As part of the full test suite
pytest -m "not slow"
```

---

## Files Created

```
tests/acceptance/
├── __init__.py
├── conftest.py                    # Fixtures, algorithm mirrors, shared paths
├── test_exe_artifact.py           # EXE file + version + spec validation
├── test_exe_launch.py             # Subprocess smoke tests (slow)
├── test_watermark_processing.py   # Watermark algorithm + issue #49 regression
├── test_jpeg_resize.py            # JPEG resize algorithm
├── test_asset_bundling.py         # Source assets ready for bundling
└── REPORT_HPM-acceptance-test-dev.md   # This document
```

`pyproject.toml` updated to register the `acceptance` pytest marker.

---

## Notes

- **pywinauto not required** — the suite is intentionally GUI-automation-free.
  Window-interaction testing would add significant maintenance burden for limited value.
- **Algorithm mirrors vs. imports** — `WatermarkThread` and `Step7Thread` extend `QThread`
  and cannot be instantiated without a `QApplication`.  The mirrors in `conftest.py`
  extract just the Pillow logic and are kept in sync with the source manually.
- **Relationship to existing suite** — the acceptance suite complements, not replaces,
  the 296-test source suite.  Run both before any release.
