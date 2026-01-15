# HSTL Photo Metadata Framework - Testing Plan

## Document Info
- **Version:** 1.0
- **Created:** Wed 15 Jan 2026 11:55:00 PM CST
- **Project:** HSTL Photo Framework (HPM)
- **Location:** `C:\Users\jimur\Projects\HST-Metadata\Photos\Version-2\Framework`

---

## Current Status

| Metric | Value |
|--------|-------|
| Total Tests | 2 (ad-hoc) |
| Test Coverage | Unknown |
| pytest Integration | Not configured |
| CI/CD | None |

### Existing Test Files
- `test_menu_theme.py` - Manual theme testing
- `test_version_checker.py` - Version checker test

---

## Testing Goals

| Goal | Target |
|------|--------|
| Unit Test Coverage | 80% minimum |
| Integration Test Coverage | Key workflows |
| Total Test Count | ~200 tests |
| Test Execution Time | < 60 seconds (excluding slow/gui) |

---

## Phase 2.5.1: Test Infrastructure

### Directory Structure
```
Framework/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── test_config_manager.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── test_pipeline.py
│   │   ├── steps/
│   │   │   ├── __init__.py
│   │   │   └── test_base_step.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── test_batch_registry.py
│   │       ├── test_path_manager.py
│   │       ├── test_validator.py
│   │       ├── test_file_utils.py
│   │       └── test_logger.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_pipeline_workflow.py
│   │   ├── test_batch_lifecycle.py
│   │   └── test_cli_commands.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── test_dialogs.py
│   │   ├── test_widgets.py
│   │   └── test_theme_zoom.py
│   └── fixtures/
│       ├── sample_batch/         # Sample batch project
│       ├── sample_config.yaml    # Test configuration
│       └── sample_csv/           # Sample CSV data
```

### pytest Configuration (pyproject.toml additions)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (may use filesystem)",
    "gui: GUI tests (require PyQt6)",
    "slow: Slow tests (> 1 second)",
    "network: Tests requiring network access",
]
addopts = "-v --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["config", "core", "steps", "utils", "gui"]
omit = [
    "tests/*",
    "*/__init__.py",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
fail_under = 80
```

### Shared Fixtures (conftest.py)
```python
"""Shared test fixtures for HPM testing."""

import pytest
import tempfile
from pathlib import Path
import shutil

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)

@pytest.fixture
def sample_batch_dir(temp_dir):
    """Create a sample batch directory structure."""
    batch_dir = temp_dir / "test_batch"
    (batch_dir / "input").mkdir(parents=True)
    (batch_dir / "output").mkdir(parents=True)
    (batch_dir / "logs").mkdir(parents=True)
    return batch_dir

@pytest.fixture
def sample_config(temp_dir):
    """Create a sample configuration file."""
    config_path = temp_dir / "config.yaml"
    config_content = """
project:
  name: test_project
  data_directory: {temp_dir}

step_configurations:
  step1:
    enabled: true
  step2:
    enabled: true
"""
    config_path.write_text(config_content.format(temp_dir=temp_dir))
    return config_path

@pytest.fixture
def mock_batch_registry(temp_dir):
    """Create a mock batch registry."""
    registry_path = temp_dir / "batch_registry.yaml"
    registry_content = """
batches:
  test_batch_001:
    name: Test Batch 1
    status: active
    created: 2026-01-15
    steps_completed: [1, 2]
"""
    registry_path.write_text(registry_content)
    return registry_path
```

### Exit Criteria for Phase 2.5.1
- [ ] Test directory structure created
- [ ] pytest configuration added to pyproject.toml
- [ ] conftest.py with shared fixtures
- [ ] `pytest` runs without errors (even with 0 tests)
- [ ] Coverage reporting configured

---

## Phase 2.5.2: Unit Tests

### Priority 1: Configuration Management (25 tests)

#### `tests/unit/config/test_config_manager.py`

| Test | Description |
|------|-------------|
| `test_config_manager_init` | ConfigManager can be instantiated |
| `test_config_manager_init_no_file` | Handles missing config file gracefully |
| `test_load_config` | Load existing YAML config |
| `test_load_config_empty` | Handle empty config file |
| `test_load_config_invalid_yaml` | Handle malformed YAML |
| `test_save_config` | Save config to file |
| `test_save_config_creates_dirs` | Creates parent directories |
| `test_get_simple_key` | Get top-level key |
| `test_get_nested_key` | Get nested key with dot notation |
| `test_get_missing_key_default` | Return default for missing key |
| `test_get_missing_key_none` | Return None when no default |
| `test_set_simple_key` | Set top-level key |
| `test_set_nested_key` | Set nested key with dot notation |
| `test_set_creates_parents` | Creates parent keys if needed |
| `test_update_step_status_completed` | Mark step as completed |
| `test_update_step_status_pending` | Mark step as pending |
| `test_get_next_step_none_completed` | Returns step 1 when none completed |
| `test_get_next_step_some_completed` | Returns next uncompleted step |
| `test_get_next_step_all_completed` | Returns None when all complete |
| `test_validate_config_valid` | Valid config passes validation |
| `test_validate_config_missing_required` | Missing required fields fail |
| `test_validate_config_invalid_types` | Invalid types fail |
| `test_config_metadata_version` | Stores framework version |
| `test_config_metadata_timestamps` | Updates timestamps on save |
| `test_config_merge_with_defaults` | Merges user config with defaults |

### Priority 2: Batch Registry (20 tests)

#### `tests/unit/utils/test_batch_registry.py`

| Test | Description |
|------|-------------|
| `test_registry_init` | BatchRegistry can be instantiated |
| `test_registry_init_no_file` | Creates new registry if none exists |
| `test_register_batch` | Register new batch |
| `test_register_batch_duplicate` | Handle duplicate batch names |
| `test_get_batch` | Get batch by name |
| `test_get_batch_not_found` | Handle missing batch |
| `test_list_batches_all` | List all batches |
| `test_list_batches_active` | List only active batches |
| `test_list_batches_archived` | List only archived batches |
| `test_update_batch_status` | Update batch status |
| `test_update_step_completed` | Mark step as completed |
| `test_get_batch_progress` | Calculate completion percentage |
| `test_mark_batch_complete` | Mark batch as complete |
| `test_archive_batch` | Archive completed batch |
| `test_archive_batch_not_complete` | Prevent archiving incomplete |
| `test_reactivate_batch` | Reactivate archived batch |
| `test_remove_batch` | Remove batch from registry |
| `test_remove_batch_preserves_files` | Files not deleted on remove |
| `test_registry_persistence` | Changes persist to file |
| `test_registry_concurrent_access` | Handle concurrent access |

### Priority 3: Path Manager (15 tests)

#### `tests/unit/utils/test_path_manager.py`

| Test | Description |
|------|-------------|
| `test_path_manager_init` | PathManager can be instantiated |
| `test_get_framework_dir` | Returns framework directory |
| `test_get_data_dir` | Returns data directory |
| `test_get_batch_dir` | Returns batch directory |
| `test_get_input_dir` | Returns input directory for batch |
| `test_get_output_dir` | Returns output directory for batch |
| `test_get_logs_dir` | Returns logs directory |
| `test_get_config_path` | Returns config file path |
| `test_ensure_dir_creates` | Creates directory if not exists |
| `test_ensure_dir_exists` | No error if already exists |
| `test_resolve_relative_path` | Resolves relative to data dir |
| `test_resolve_absolute_path` | Absolute paths unchanged |
| `test_path_validation` | Validates path characters |
| `test_path_normalization` | Normalizes path separators |
| `test_get_step_output_dir` | Returns step-specific output dir |

### Priority 4: Pipeline (15 tests)

#### `tests/unit/core/test_pipeline.py`

| Test | Description |
|------|-------------|
| `test_pipeline_init` | Pipeline can be instantiated |
| `test_register_step` | Register step processor |
| `test_register_step_order` | Steps maintain order |
| `test_register_step_duplicate` | Handle duplicate step numbers |
| `test_run_single_step` | Execute single step |
| `test_run_step_range` | Execute range of steps |
| `test_run_all_steps` | Execute all steps in order |
| `test_run_dry_run` | Dry run validates without executing |
| `test_run_step_failure` | Handle step failure |
| `test_run_step_failure_stops` | Pipeline stops on failure |
| `test_pipeline_result_success` | Returns success result |
| `test_pipeline_result_failure` | Returns failure with errors |
| `test_pipeline_context_passing` | Context passed between steps |
| `test_pipeline_shared_data` | Steps can share data |
| `test_pipeline_logging` | Pipeline logs execution |

### Priority 5: Base Step Processor (15 tests)

#### `tests/unit/steps/test_base_step.py`

| Test | Description |
|------|-------------|
| `test_step_processor_abstract` | Cannot instantiate base class |
| `test_step_processor_subclass` | Can subclass with implementations |
| `test_step_lifecycle_order` | Lifecycle methods called in order |
| `test_step_setup` | Setup called before validate |
| `test_step_validate_inputs` | Input validation called |
| `test_step_execute` | Execute called after validation |
| `test_step_validate_outputs` | Output validation called |
| `test_step_cleanup` | Cleanup called after execute |
| `test_step_context_access` | Step can access context |
| `test_step_config_access` | Step can access config |
| `test_step_result_success` | Returns StepResult on success |
| `test_step_result_failure` | Returns StepResult on failure |
| `test_step_skip_on_input_fail` | Skips execute if input invalid |
| `test_step_processed_files` | Tracks processed files |
| `test_step_error_handling` | Handles exceptions gracefully |

### Priority 6: Validator (10 tests)

#### `tests/unit/utils/test_validator.py`

| Test | Description |
|------|-------------|
| `test_validator_init` | Validator can be instantiated |
| `test_validate_file_exists` | Check file exists |
| `test_validate_file_not_exists` | Fail on missing file |
| `test_validate_directory_exists` | Check directory exists |
| `test_validate_file_extension` | Check file extension |
| `test_validate_csv_format` | Validate CSV structure |
| `test_validate_image_format` | Validate image files |
| `test_validation_result_success` | Returns success result |
| `test_validation_result_errors` | Returns errors list |
| `test_validation_aggregate` | Aggregate multiple validations |

### Priority 7: File Utils (10 tests)

#### `tests/unit/utils/test_file_utils.py`

| Test | Description |
|------|-------------|
| `test_copy_file` | Copy file to destination |
| `test_copy_file_overwrite` | Overwrite existing file |
| `test_move_file` | Move file to destination |
| `test_delete_file` | Delete file |
| `test_delete_file_not_exists` | Handle missing file |
| `test_ensure_directory` | Create directory if needed |
| `test_list_files_pattern` | List files matching pattern |
| `test_list_files_recursive` | List files recursively |
| `test_get_file_hash` | Calculate file hash |
| `test_verify_file_integrity` | Verify file not corrupted |

### Priority 8: Logger (10 tests)

#### `tests/unit/utils/test_logger.py`

| Test | Description |
|------|-------------|
| `test_logger_init` | Logger can be instantiated |
| `test_logger_levels` | Log at different levels |
| `test_logger_file_output` | Log to file |
| `test_logger_console_output` | Log to console |
| `test_colored_formatter` | ColoredFormatter works |
| `test_step_logger_prefix` | StepLogger adds step prefix |
| `test_logger_rotation` | Log file rotation |
| `test_logger_format` | Log format correct |
| `test_logger_timestamp` | Timestamps in logs |
| `test_logger_exception` | Log exceptions with traceback |

### Unit Test Summary

| Module | Tests | Priority |
|--------|-------|----------|
| ConfigManager | 25 | High |
| BatchRegistry | 20 | High |
| PathManager | 15 | High |
| Pipeline | 15 | High |
| BaseStep | 15 | High |
| Validator | 10 | Medium |
| FileUtils | 10 | Medium |
| Logger | 10 | Low |
| **Total** | **120** | |

### Exit Criteria for Phase 2.5.2
- [ ] All 120 unit tests written and passing
- [ ] Unit test coverage >= 80%
- [ ] No test takes longer than 1 second
- [ ] All tests can run without external dependencies

---

## Phase 2.5.3: Integration Tests

### Pipeline Workflow Tests (15 tests)

#### `tests/integration/test_pipeline_workflow.py`

| Test | Description |
|------|-------------|
| `test_init_creates_structure` | `init` creates project structure |
| `test_init_creates_config` | `init` creates default config |
| `test_pipeline_step_sequence` | Steps execute in correct order |
| `test_pipeline_resume_after_failure` | Can resume after step failure |
| `test_pipeline_skip_completed` | Skips already completed steps |
| `test_pipeline_force_rerun` | Force flag reruns completed steps |
| `test_pipeline_dry_run_no_changes` | Dry run makes no file changes |
| `test_pipeline_rollback_on_error` | Rollback on critical error |
| `test_pipeline_output_validation` | Each step validates outputs |
| `test_pipeline_logging` | Pipeline creates log files |
| `test_pipeline_progress_tracking` | Progress updates during run |
| `test_pipeline_config_updates` | Config updated after each step |
| `test_pipeline_step_range` | Run specific step range (e.g., 3-5) |
| `test_pipeline_single_step` | Run single step by number |
| `test_pipeline_full_workflow` | Complete workflow end-to-end |

### Batch Lifecycle Tests (10 tests)

#### `tests/integration/test_batch_lifecycle.py`

| Test | Description |
|------|-------------|
| `test_create_new_batch` | Create new batch project |
| `test_batch_directory_structure` | Batch has correct structure |
| `test_batch_status_transitions` | Status: active → complete → archived |
| `test_batch_step_tracking` | Track completed steps per batch |
| `test_batch_archive_workflow` | Archive completed batch |
| `test_batch_reactivate_workflow` | Reactivate archived batch |
| `test_multi_batch_concurrent` | Multiple batches simultaneously |
| `test_batch_remove_preserves_data` | Remove from registry, keep files |
| `test_batch_info_display` | Batch info shows correct data |
| `test_batch_list_filtering` | Filter batches by status |

### CLI Command Tests (15 tests)

#### `tests/integration/test_cli_commands.py`

| Test | Description |
|------|-------------|
| `test_cli_help` | `--help` shows usage |
| `test_cli_version` | `--version` shows version |
| `test_cli_init` | `init` command works |
| `test_cli_status` | `status` command works |
| `test_cli_config_list` | `config --list` shows config |
| `test_cli_config_set` | `config --set` updates config |
| `test_cli_run_step` | `run 1` executes step 1 |
| `test_cli_run_range` | `run 1-3` executes steps 1-3 |
| `test_cli_run_list` | `run 2,4,6` executes specific steps |
| `test_cli_validate` | `validate` checks project |
| `test_cli_batches_list` | `batches` lists all batches |
| `test_cli_batch_info` | `batch info` shows batch details |
| `test_cli_batch_complete` | `batch complete` marks complete |
| `test_cli_batch_archive` | `batch archive` archives batch |
| `test_cli_error_handling` | Invalid commands show errors |

### Integration Test Summary

| Category | Tests |
|----------|-------|
| Pipeline Workflow | 15 |
| Batch Lifecycle | 10 |
| CLI Commands | 15 |
| **Total** | **40** |

### Exit Criteria for Phase 2.5.3
- [ ] All 40 integration tests written and passing
- [ ] Tests use temporary directories (no pollution)
- [ ] Tests are independent (can run in any order)
- [ ] Average test time < 2 seconds

---

## Phase 2.5.4: GUI Tests

### Dialog Tests (15 tests)

#### `tests/gui/test_dialogs.py`

| Test | Description |
|------|-------------|
| `test_new_batch_dialog_init` | NewBatchDialog initializes |
| `test_new_batch_dialog_validation` | Validates batch name input |
| `test_batch_info_dialog_display` | BatchInfoDialog shows data |
| `test_settings_dialog_init` | SettingsDialog initializes |
| `test_settings_dialog_save` | Settings save correctly |
| `test_set_data_location_dialog` | Data location dialog works |
| `test_step1_dialog_init` | Step1Dialog initializes |
| `test_step2_dialog_init` | Step2Dialog initializes |
| `test_step3_dialog_init` | Step3Dialog initializes |
| `test_step4_dialog_init` | Step4Dialog initializes |
| `test_step5_dialog_init` | Step5Dialog initializes |
| `test_step6_dialog_init` | Step6Dialog initializes |
| `test_step7_dialog_init` | Step7Dialog initializes |
| `test_step8_dialog_init` | Step8Dialog initializes |
| `test_theme_dialog_init` | ThemeDialog initializes |

### Widget Tests (10 tests)

#### `tests/gui/test_widgets.py`

| Test | Description |
|------|-------------|
| `test_batch_list_widget_init` | BatchListWidget initializes |
| `test_batch_list_widget_populate` | Shows batches correctly |
| `test_batch_list_widget_selection` | Selection works |
| `test_step_widget_init` | StepWidget initializes |
| `test_step_widget_progress` | Shows step progress |
| `test_step_widget_execution` | Step execution UI updates |
| `test_config_widget_init` | ConfigWidget initializes |
| `test_config_widget_edit` | Config editing works |
| `test_log_widget_init` | LogWidget initializes |
| `test_log_widget_display` | Shows log content |

### Theme and Zoom Tests (10 tests)

#### `tests/gui/test_theme_zoom.py`

| Test | Description |
|------|-------------|
| `test_theme_manager_init` | ThemeManager initializes |
| `test_theme_light` | Light theme applies |
| `test_theme_dark` | Dark theme applies |
| `test_theme_switch` | Theme switching works |
| `test_theme_persistence` | Theme persists across sessions |
| `test_zoom_manager_init` | ZoomManager initializes |
| `test_zoom_increase` | Zoom in works |
| `test_zoom_decrease` | Zoom out works |
| `test_zoom_reset` | Zoom reset works |
| `test_zoom_persistence` | Zoom level persists |

### GUI Test Summary

| Category | Tests |
|----------|-------|
| Dialogs | 15 |
| Widgets | 10 |
| Theme/Zoom | 10 |
| **Total** | **35** |

### Exit Criteria for Phase 2.5.4
- [ ] All 35 GUI tests written and passing
- [ ] Tests use `pytest-qt` or similar
- [ ] Tests run headless where possible
- [ ] No GUI tests in CI (marked with `@pytest.mark.gui`)

---

## Test Execution Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run unit tests only
pytest tests/unit -m unit

# Run integration tests only
pytest tests/integration -m integration

# Run excluding GUI and slow tests
pytest -m "not gui and not slow"

# Run specific test file
pytest tests/unit/config/test_config_manager.py

# Run with verbose output
pytest -v --tb=long

# Run parallel (if pytest-xdist installed)
pytest -n auto
```

---

## Test Summary

| Phase | Category | Tests | Priority |
|-------|----------|-------|----------|
| 2.5.1 | Infrastructure | - | High |
| 2.5.2 | Unit Tests | 120 | High |
| 2.5.3 | Integration Tests | 40 | High |
| 2.5.4 | GUI Tests | 35 | Medium |
| **Total** | | **195** | |

---

## Implementation Schedule

### Phase 2.5.1: Test Infrastructure
- Create directory structure
- Configure pytest in pyproject.toml
- Create conftest.py with fixtures
- Verify pytest runs

### Phase 2.5.2: Unit Tests (Priority Order)
1. ConfigManager (25 tests)
2. BatchRegistry (20 tests)
3. PathManager (15 tests)
4. Pipeline (15 tests)
5. BaseStep (15 tests)
6. Validator (10 tests)
7. FileUtils (10 tests)
8. Logger (10 tests)

### Phase 2.5.3: Integration Tests
1. CLI Commands (15 tests)
2. Pipeline Workflow (15 tests)
3. Batch Lifecycle (10 tests)

### Phase 2.5.4: GUI Tests
1. Theme/Zoom (10 tests) - simplest
2. Widgets (10 tests)
3. Dialogs (15 tests) - most complex

---

## Dependencies

### Required Packages
```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-qt>=4.2.0      # For GUI tests
hypothesis>=6.0.0     # For property-based tests (optional)
```

### External Dependencies
- ExifTool (for step 5 tests with real metadata)
- Sample image files (TIFF, JPEG)
- Sample CSV files

---

## Success Metrics

| Metric | Target | Stretch |
|--------|--------|---------|
| Total Tests | 195 | 250+ |
| Unit Coverage | 80% | 90% |
| Test Pass Rate | 100% | 100% |
| Execution Time | < 60s | < 30s |
| Flaky Tests | 0 | 0 |

---

## Notes

1. **GUI Tests**: Consider using `pytest-qt` for PyQt6 testing, or mark GUI tests to skip in CI environments.

2. **External Tools**: Tests requiring ExifTool should be marked `@pytest.mark.slow` or skipped if ExifTool not installed.

3. **Sample Data**: Create minimal sample files (small images, short CSVs) to keep tests fast.

4. **Isolation**: Each test should clean up after itself. Use `temp_dir` fixtures.

5. **Mocking**: Mock external services (Google API, GitHub API) in unit tests.

---

*Document created following PyGit Phase 2.5 testing methodology.*
