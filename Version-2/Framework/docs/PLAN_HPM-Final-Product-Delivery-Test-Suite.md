# HPM Final Product Delivery — Test Suite

**HSTL Photo Metadata (HPM) Project**
**Version:** 1.1
**Date:** 2026-03-22
**Related Plan:** `PLAN_HPM-Final-Product-Delivery-oc.md`
**Status:** Implemented — 63 tests, all passing (1.42s)

---

## 1. Overview

This document describes the test suite for the HPM Delivery feature (v1.9.1). Tests are organised across three layers of the existing suite — unit, integration, and GUI — matching conventions already established in the framework.

### Result summary

| Layer | File | Tests | Status |
|-------|------|-------|--------|
| Shared fixture | `tests/conftest.py` | `completed_batch` fixture | ✅ |
| Unit | `tests/unit/utils/test_path_manager.py` | 7 | ✅ All pass |
| Unit | `tests/unit/core/test_delivery_service.py` | 28 | ✅ All pass |
| Integration | `tests/integration/test_delivery_workflow.py` | 17 | ✅ All pass |
| GUI | `tests/gui/test_dialogs.py` | 6 | ✅ All pass |
| **Total** | | **63** | **✅ 63/63** |

---

## 2. Shared Fixture — `tests/conftest.py`

A `completed_batch` fixture was added to the root `conftest.py`. It creates a full HPM batch directory tree populated with dummy files and a `project_config.yaml` with all 8 steps marked complete — the minimum state required by `DeliveryService`.

**Directories created:**

```
completed_batch_data/
├── input/tiff/
├── input/spreadsheet/source.xlsx       ← retained artifact
├── output/csv/export.csv               ← retained artifact
├── output/tiff_processed/IMG_001.tif   ← delivery source (2 files)
├── output/tiff_processed/IMG_002.tif
├── output/jpeg_watermarked/IMG_001.jpg ← delivery source
├── output/jpeg/IMG_001.jpg             ← trash source
├── output/jpeg_resized/IMG_001.jpg     ← trash source
├── config/project_config.yaml          ← steps 1–8 all True
├── logs/
└── reports/
```

**Availability:** All test layers — unit, integration, GUI.

---

## 3. Unit Tests

### 3.1 Path Manager — `tests/unit/utils/test_path_manager.py`

Class `TestPathManagerDeliveryPaths` added at the bottom of the existing file.

**Tests (7):**

| Test | Asserts |
|------|---------|
| `test_get_delivery_tiff_dir` | Returns `data_dir/delivery/tiff_delivery` |
| `test_get_delivery_jpeg_dir` | Returns `data_dir/delivery/jpeg_delivery` |
| `test_get_trash_jpeg_converted_dir` | Returns `data_dir/trash/jpeg_converted` |
| `test_get_trash_jpeg_resized_dir` | Returns `data_dir/trash/jpeg_resized` |
| `test_delivery_paths_return_none_without_data_dir` | All four return `None` when no data dir set |
| `test_delivery_paths_are_path_objects` | All four return `Path` instances |
| `test_delivery_paths_nested_under_data_dir` | All four are children of data directory |

### 3.2 Delivery Service — `tests/unit/core/test_delivery_service.py`

New file. Four test classes covering the full `DeliveryService` API.

#### `TestDeliveryServiceValidation` (6 tests)

| Test | Asserts |
|------|---------|
| `test_rejects_incomplete_batch` | `validate()` returns `(False, reason)` when steps incomplete |
| `test_rejects_missing_tiff_processed_dir` | Fails when `output/tiff_processed` is absent |
| `test_rejects_missing_jpeg_watermarked_dir` | Fails when `output/jpeg_watermarked` is absent |
| `test_rejects_empty_tiff_processed_dir` | Fails when dir exists but contains no files |
| `test_rejects_empty_jpeg_watermarked_dir` | Fails when dir exists but contains no files |
| `test_accepts_valid_completed_batch` | Returns `(True, "ok")` for fully ready batch |

#### `TestDeliveryServiceExecution` (9 tests)

| Test | Asserts |
|------|---------|
| `test_returns_success` | `create_package()` returns `(True, message)` |
| `test_creates_delivery_tiff_directory` | `delivery/tiff_delivery/` exists after run |
| `test_creates_delivery_jpeg_directory` | `delivery/jpeg_delivery/` exists after run |
| `test_copies_tiffs_to_delivery` | Filenames in tiff_delivery match tiff_processed |
| `test_copies_jpegs_to_delivery` | Filenames in jpeg_delivery match jpeg_watermarked |
| `test_source_tiffs_remain_after_copy` | `tiff_processed` file count unchanged (copy not move) |
| `test_moves_intermediate_jpegs_to_trash` | `output/jpeg` empty; files in `trash/jpeg_converted` |
| `test_moves_resized_jpegs_to_trash` | `output/jpeg_resized` empty; files in `trash/jpeg_resized` |
| `test_progress_callback_receives_messages` | Callback called with log messages |
| `test_progress_callback_is_optional` | `create_package()` succeeds with no callback |

#### `TestDeliveryServiceStateQueries` (8 tests)

| Test | Asserts |
|------|---------|
| `test_delivery_exists_false_before_package_created` | `delivery_exists()` is `False` initially |
| `test_delivery_exists_true_after_package_created` | `delivery_exists()` is `True` after run |
| `test_trash_has_files_false_before_delivery` | `trash_has_files()` is `False` initially |
| `test_trash_has_files_true_after_delivery` | `trash_has_files()` is `True` after run |
| `test_get_file_counts_returns_correct_tiff_count` | Count matches `tiff_processed` file count |
| `test_get_file_counts_returns_correct_jpeg_count` | Count matches `jpeg_watermarked` file count |
| `test_all_steps_complete_true_for_completed_batch` | Returns `True` for complete batch |
| `test_all_steps_complete_false_when_config_missing` | Returns `False` when config absent |

#### `TestDeliveryServiceEdgeCases` (7 tests)

| Test | Asserts |
|------|---------|
| `test_second_run_succeeds` | Calling `create_package()` twice returns success |
| `test_create_package_skips_absent_jpeg_dir` | Succeeds when `output/jpeg` does not exist |
| `test_create_package_skips_absent_jpeg_resized_dir` | Succeeds when `output/jpeg_resized` does not exist |
| `test_empty_trash_removes_all_files` | `trash_has_files()` is `False` after `empty_trash()` |
| `test_empty_trash_noop_when_trash_dir_absent` | Returns success even if `trash/` never created |
| `test_empty_trash_leaves_delivery_intact` | `delivery/` file counts unchanged after empty trash |
| `test_partial_failure_returns_false` | `shutil.copy2` patched to raise; returns `(False, error)` |

---

## 4. Integration Tests — `tests/integration/test_delivery_workflow.py`

New file. Real filesystem, no mocking. Three test classes.

> Integration tests are the highest-value layer for the delivery feature because the work is fundamentally file I/O. Real filesystem tests catch failures that mocked tests miss.

#### `TestDeliveryPackageCreation` (12 tests)

| Test | Asserts |
|------|---------|
| `test_full_delivery_creates_expected_directory_structure` | All four delivery/trash dirs exist after run |
| `test_delivery_blocked_on_incomplete_batch` | `validate()` fails; `delivery/` not created |
| `test_delivery_tiff_count_matches_source` | File count in tiff_delivery equals tiff_processed |
| `test_delivery_jpeg_count_matches_source` | File count in jpeg_delivery equals jpeg_watermarked |
| `test_delivered_tiff_filenames_match_source` | Exact filename set match |
| `test_delivered_jpeg_filenames_match_source` | Exact filename set match |
| `test_intermediate_jpegs_absent_from_output_after_delivery` | `output/jpeg` and `output/jpeg_resized` empty |
| `test_intermediate_jpegs_present_in_trash_after_delivery` | Files in `trash/jpeg_converted` match original `output/jpeg` |
| `test_retained_artifacts_untouched` | Excel, CSV, config unchanged |
| `test_source_tiffs_retained_after_delivery` | `output/tiff_processed` unchanged after delivery |
| `test_idempotent_with_second_run` | Second `create_package()` call returns success |
| `test_delivery_with_multiple_tiff_files` | Correctly handles 10-file batch |

#### `TestEmptyTrash` (5 tests)

| Test | Asserts |
|------|---------|
| `test_empty_trash_removes_all_trash_contents` | `trash_has_files()` is `False` after empty |
| `test_empty_trash_removes_trash_directory_itself` | `trash/` directory itself is deleted |
| `test_empty_trash_leaves_delivery_directory_intact` | `delivery/` file counts unchanged |
| `test_empty_trash_noop_before_delivery` | Returns success when `trash/` never existed |
| `test_empty_trash_noop_when_trash_already_empty` | Second `empty_trash()` call returns success |

#### `TestDeliveryServiceStateIntegration` (2 tests)

| Test | Asserts |
|------|---------|
| `test_delivery_exists_reflects_filesystem` | `delivery_exists()` tracks real filesystem state |
| `test_trash_has_files_reflects_filesystem` | `trash_has_files()` tracks real filesystem state through full lifecycle |

---

## 5. GUI Tests — `tests/gui/test_dialogs.py`

Class `TestDeliveryDialogImport` added before the existing `TestDialogAcceptReject` class.

**Dependency:** `pytest-qt` — installed to venv during test suite implementation.

**Tests (6):**

| Test | Asserts |
|------|---------|
| `test_import_delivery_dialog` | `DeliveryDialog` can be imported |
| `test_delivery_dialog_init_complete_batch` | Dialog instantiates with a completed batch |
| `test_delivery_dialog_deliver_btn_enabled_for_complete_batch` | `deliver_btn` is enabled when all 8 steps done |
| `test_delivery_dialog_deliver_btn_disabled_for_incomplete_batch` | `deliver_btn` is disabled when steps incomplete |
| `test_delivery_dialog_button_text_changes_when_delivery_exists` | Button text includes "Overwrite" when delivery exists |
| `test_delivery_dialog_has_output_text_widget` | `output_text` widget exists and is read-only |

---

## 6. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 9.0.2 | Test runner (pre-existing) |
| `pytest-qt` | 4.5.0 | `qtbot` fixture for GUI tests — **added during v1.9.1** |

`pytest-qt` is installed in `.venv`. It requires PyQt6, which was already present.

---

## 7. Running the delivery tests

Run all delivery tests:

```
pytest tests/unit/utils/test_path_manager.py::TestPathManagerDeliveryPaths tests/unit/core/test_delivery_service.py tests/integration/test_delivery_workflow.py tests/gui/test_dialogs.py::TestDeliveryDialogImport -v
```

Run by layer:

```
pytest tests/unit/core/test_delivery_service.py -v           # unit — service
pytest tests/integration/test_delivery_workflow.py -v        # integration
pytest tests/gui/test_dialogs.py::TestDeliveryDialogImport   # GUI
```

---

*Implemented 2026-03-22 — all 63 tests passing*
