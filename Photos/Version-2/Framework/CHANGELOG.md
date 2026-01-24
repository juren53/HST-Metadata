# Changelog - HSTL Photo Framework

All notable changes to the HSTL Photo Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## HPM [1.8.0] - 2026-01-24 17:30 CST

### Changed

- **Major Version Bump** - First stable release candidate
  - Version numbering changed from 0.1.x to 1.8.0 to reflect production readiness
  - All 8 processing steps fully functional with GUI support

### Updated

- **requirements.txt Modernized** - Cleaned up and documented actual dependencies
  - Core dependencies: PyYAML, pandas, openpyxl, ftfy, PyQt6, Pillow, PyExifTool
  - Removed unused packages: tqdm, structlog, colorama, pydantic, xlrd
  - Added documentation mapping packages to steps (ftfy→Step 3, Pillow/PyExifTool→Step 8)
  - Added ExifTool command-line installation note
  - Updated Python requirement to 3.9+
  - **Files Modified**: `requirements.txt`

### Fixed

- **Step 1 Revert Now Deletes Spreadsheet Files** - Revert Step 1 now properly cleans up `input/spreadsheet` directory
  - Previously, reverting Step 1 would mark the step as pending but leave downloaded Excel files in place
  - Multiple Excel files could stack up in the directory across re-runs
  - Now deletes all files from `input/spreadsheet` when reverting Step 1
  - Confirmation dialog warns user that files will be deleted
  - **Files Modified**: `gui/widgets/step_widget.py`

- **Step 2 Revert Now Deletes All CSV Files** - Revert Step 2 now deletes all files in `output/csv` directory
  - Previously only deleted `export.csv`, leaving other files that may have accumulated
  - Now deletes all files in the directory for consistent cleanup
  - **Files Modified**: `gui/widgets/step_widget.py`

---

## HPM [0.1.7p] - 2026-01-24 15:30 CST

### Fixed

- **Step 1 Revert Now Deletes Spreadsheet Files** - Revert Step 1 now properly cleans up `input/spreadsheet` directory
  - Previously, reverting Step 1 would mark the step as pending but leave downloaded Excel files in place
  - Multiple Excel files could stack up in the directory across re-runs
  - Now deletes all files from `input/spreadsheet` when reverting Step 1
  - Confirmation dialog warns user that files will be deleted
  - **Files Modified**: `gui/widgets/step_widget.py`

- **Step 2 Revert Now Deletes All CSV Files** - Revert Step 2 now deletes all files in `output/csv` directory
  - Previously only deleted `export.csv`, leaving other files that may have accumulated
  - Now deletes all files in the directory for consistent cleanup
  - **Files Modified**: `gui/widgets/step_widget.py`

---

## HPM [0.1.7o] - 2026-01-24 12:48 CST

### Improved

- **Get Latest Updates Feature Overhaul** - Smooth, hassle-free updates like modern software
  - No longer warns about uncommitted changes (local artifacts safely discarded)
  - Shows clear version comparison: "Current: v0.1.7n → New: v0.1.8a"
  - Uses `git reset --hard` for reliable updates without merge conflicts
  - Displays target version in progress dialog and success message
  - Uses semantic version comparison instead of commit counting
  - **Files Modified**: `utils/git_updater.py`, `gui/main_window.py`

### Added

- **New git_updater methods**:
  - `force_update()` - Force update discarding local changes
  - `get_update_info()` - Get comprehensive version comparison
  - `_compare_versions()` - Semantic version comparison for HPM format (e.g., "0.1.7n")
  - `_get_local_version()` - Read version from local `__init__.py`

---

## HPM [0.1.7n] - 2026-01-24 05:05 CST

### Added

- **DateCreated Fallback Logic** - g2c.py now uses coverageStartDate as fallback when productionDate is empty
  - Primary source: `productionDateMonth`, `productionDateDay`, `productionDateYear`
  - Fallback source: `coverageStartDateMonth`, `coverageStartDateDay`, `coverageStartDateYear`
  - Reports how many dates came from each source in output
  - Refactored date extraction into reusable helper function
  - **Files Modified**: `g2c.py`

---

## HPM [0.1.7m] - 2026-01-24 04:54 CST

### Fixed

- **Revert Step System Logging** - Step revert operations now properly log to the system log
  - Previously, revert operations only displayed messages in the UI but were not recorded in the system log
  - Added `log_manager` import and logging calls throughout `_revert_step()` method
  - Now logs: revert initiation, file deletions (with counts), errors, and completion status
  - Applies to all steps with file deletion (Steps 2, 4, 5, 6, 7, 8)
  - **Files Modified**: `gui/widgets/step_widget.py`

- **Step 5 Review Button** - Now opens File Explorer directly instead of searching for TagWriter
  - Previously showed "TagWriter Not Found" dialog before offering to open File Explorer
  - Now behaves consistently with Steps 6-8: opens `output/tiff_processed` directory directly
  - Removed TagWriter detection and launch logic (~50 lines of unused code)
  - **Files Modified**: `gui/widgets/step_widget.py`

- **g2c.py Technical Debt Cleanup** - Removed dead code and duplicates identified by consensus code review
  - Removed ~82 lines (13% reduction) of unreachable/duplicate code
  - Deleted dead code after `return df` in `read_excel_file()` (~59 lines of legacy Google Sheets artifacts)
  - Removed duplicate argparse argument definitions (`--excel-file`, `--export-csv` defined twice)
  - Removed duplicate exception handling block (unreachable code after `sys.exit(1)`)
  - Eliminated references to undefined variables (`headers`, `data_rows`, `HttpError`)
  - Core IPTC mapping and encoding cleanup logic unchanged
  - **Files Modified**: `g2c.py`

---

## HPM [0.1.7k] - 2026-01-23 02:07 CST

### Fixed

- **Get Latest Updates Git Error** - Fixed recurring "Need to specify how to reconcile divergent branches" error
  - Added `--rebase` flag to git pull command in `utils/git_updater.py` (line 231)
  - Prevents fatal error when using HPM's "Get Latest Updates" feature
  - Git now uses rebase strategy to reconcile divergent branches automatically
  - **Files Modified**: `utils/git_updater.py`

---

## HPM [0.1.7j] - 2026-01-22 17:57 CST

### Improved

- **Step 4 TIFF Copy Feedback** - Added real-time UI feedback during TIFF file copy operation
  - Users now see each filename with sequence number displayed as files are copied (e.g., "Copied (1/10): filename.tif")
  - Added `QApplication.processEvents()` calls to force UI updates during the blocking copy loop
  - Improves user experience for large TIFF transfers that take significant time

---

## HPM [0.1.7h] - 2026-01-21 21:30 CST

### Added

- **Complete Test Suite Implementation** - HPM Testing Plan (Phases 2.5.2-2.5.4) fully implemented (2026-01-21)

  - **Test Results**: 296 tests passing in 5.66 seconds (44% above 206 target)
  - **Test Distribution**:
    - Unit Tests: 189 tests (64%)
    - Integration Tests: 50 tests (17%)
    - GUI Tests: 57 tests (19%)

  - **Phase 2.5.2 - Unit Tests** (178 tests, +48% above 120 target):
    - `tests/unit/config/test_config_manager.py` - 34 tests for configuration management
    - `tests/unit/utils/test_batch_registry.py` - 27 tests for batch registration
    - `tests/unit/utils/test_path_manager.py` - 20 tests for path management
    - `tests/unit/core/test_pipeline.py` - 19 tests for pipeline orchestration
    - `tests/unit/steps/test_base_step.py` - 21 tests for step processor base class
    - `tests/unit/utils/test_validator.py` - 15 tests for validation utilities
    - `tests/unit/utils/test_file_utils.py` - 21 tests for file utilities
    - `tests/unit/utils/test_logger.py` - 21 tests for logging

  - **Phase 2.5.3 - Integration Tests** (50 tests, +25% above 40 target):
    - `tests/integration/test_pipeline_workflow.py` - 12 tests for pipeline workflows
    - `tests/integration/test_batch_lifecycle.py` - 12 tests for batch lifecycle
    - `tests/integration/test_cli_commands.py` - 26 tests for CLI commands

  - **Phase 2.5.4 - GUI Tests** (57 tests, +63% above 35 target):
    - `tests/gui/test_theme_zoom.py` - 24 tests for theme/zoom managers
    - `tests/gui/test_widgets.py` - 11 tests for GUI widgets
    - `tests/gui/test_dialogs.py` - 22 tests for GUI dialogs

  - **Coverage Areas**:
    - Configuration loading, saving, and manipulation
    - Batch registration, status tracking, and lifecycle
    - Path management and validation
    - Pipeline orchestration and step execution
    - Step processor lifecycle and validation
    - File and directory validation utilities
    - File operations (backup, search, size calculation)
    - Logging setup, formatters, and context adapters
    - Theme switching (light/dark/system)
    - Zoom functionality (75%-200%)
    - Widget initialization and functionality
    - Dialog initialization and accept/reject behavior

  - **Testing Infrastructure**:
    - pytest with markers (@pytest.mark.unit, @pytest.mark.integration, @pytest.mark.gui)
    - pytest-qt for PyQt6 GUI testing
    - Mock objects and fixtures in `tests/conftest.py`
    - Singleton reset fixtures for ThemeManager and ZoomManager

  - **Files Created**:
    - `tests/unit/config/test_config_manager.py`
    - `tests/unit/utils/test_batch_registry.py`
    - `tests/unit/utils/test_path_manager.py`
    - `tests/unit/core/test_pipeline.py`
    - `tests/unit/steps/test_base_step.py`
    - `tests/unit/utils/test_validator.py`
    - `tests/unit/utils/test_file_utils.py`
    - `tests/unit/utils/test_logger.py`
    - `tests/integration/test_pipeline_workflow.py`
    - `tests/integration/test_batch_lifecycle.py`
    - `tests/integration/test_cli_commands.py`
    - `tests/gui/test_theme_zoom.py`
    - `tests/gui/test_widgets.py`
    - `tests/gui/test_dialogs.py`
    - `tests/REPORT_HPM-Test-Plan-Complete-and-Passing-2026-01-21.md`

---

## HPM [0.1.7g] - 2026-01-21 18:32 CST

### Added

- **ExifTool Info in Help/About Dialog** - Added ExifTool version and path to About dialog
  - New `get_exiftool_info()` utility function in `utils/file_utils.py`
  - Detects ExifTool executable via PATH or common Windows location (%LOCALAPPDATA%\exiftool\)
  - Displays ExifTool version number and executable path
  - Shows "Not found in PATH" if ExifTool is not installed
  - Follows same pattern as existing Python, HPM, and OS information display
  - **Files Modified**: `utils/file_utils.py`, `gui/main_window.py`

- **ExifTool Portable Version Planning** - Comprehensive planning documents for ExifTool distribution strategy
  - **PLAN_ExifTool-creating-a-portable-version.md** - Original plan with three approaches:
    1. Option 1: Use older standalone version (v12.60)
    2. Option 2: Create custom PAR::Packer build
    3. Option 3: Enhanced smart installer bundle
  - Includes review and critique section analyzing each approach
  - Documents root causes: MOTW issues, dependency shift, path dependencies
  - **PLAN_ExifTool-creating-a-portable-version-v2.md** - Revised plan tailored for HPM use case
    - Recommends ExifTool v12.60 standalone as primary solution
    - HPM-specific analysis: IPTC metadata on historical TIFFs/JPEGs only
    - Confirms v12.60 has full IPTC encoding support (stable since v6.86)
    - Character encoding and mojibake handling section with detection scripts
    - Expanded test plan (9 tests including encoding validation)
    - Fallback options documented with activation triggers
    - Annual review checklist for maintenance
  - **Key Finding**: For HPM's use case, newer ExifTool features (camera RAW, video metadata) are not needed
  - **Encoding Support**: `-charset iptc=CHARSET` commands fully supported in v12.60 for mojibake fixes
  - **Files Created**: `notes/PLAN_ExifTool-creating-a-portable-version.md`, `notes/PLAN_ExifTool-creating-a-portable-version-v2.md`

---

## HPM [0.1.7f] - 2026-01-19

### Fixed

- **Step Dialog Output Display** - Restored missing progress messages in Steps 2-8 dialogs.
  - Fixed `_on_progress()` methods in all step dialogs to display messages in the dialog's output_text widget.
  - Previously, messages were only being sent to the log manager, making dialogs appear blank during operations.
  - Steps 2-4: Now display conversion/processing progress in real-time.
  - Step 5: Now displays metadata embedding progress and file processing status.
  - Steps 6-8: Now display JPEG conversion, resizing, and watermarking progress.
  - Users can now see operation status directly in the dialog without having to check the log viewer.
  - **Files Modified**: `gui/dialogs/step2_dialog.py`, `gui/dialogs/step3_dialog.py`, `gui/dialogs/step4_dialog.py`, `gui/dialogs/step5_dialog.py`, `gui/dialogs/step6_dialog.py`, `gui/dialogs/step7_dialog.py`, `gui/dialogs/step8_dialog.py`

- **Step 4 Dialog** - Fixed corrupted file that was missing large portions of code.
  - Restored complete `_generate_report()` method with proper exception handling.
  - Restored entire `Step4Dialog` class definition and all its methods.
  - File had been truncated at line 211, causing "expected 'except' or 'finally' block" syntax error.
  - Recovered missing code from git history.
  - **Files Modified**: `gui/dialogs/step4_dialog.py`

- **Step 2 Dialog** - Fixed step status not updating in UI after completion.
  - Added `self.accept()` call to close dialog and trigger UI refresh.
  - Shows completion message before closing so users can review the results.
  - Step now properly shows as "Complete" instead of "Pending" in main window.
  - **Files Modified**: `gui/dialogs/step2_dialog.py`

### Changed

- **Get Latest Updates Dialog** - Simplified language to be more user-friendly.
  - Removed git-specific terminology ("pull", "commit(s)", "branch") throughout all update dialogs.
  - Main dialog now shows "An update is available" instead of "Updates are available: X commit(s) available".
  - Displays both current version and available update version (e.g., "Update available: v0.1.7g").
  - Changed "pull the latest updates" to "download the latest update".
  - Progress dialog now says "Downloading latest update" instead of "Pulling latest updates".
  - Success message changed to "Successfully downloaded and installed" instead of "Successfully pulled".
  - Simplified statistics display to show only "X file(s) updated" instead of detailed insertions/deletions.
  - Uncommitted changes warning now says "unsaved changes" instead of "uncommitted changes".
  - Already up-to-date message no longer mentions branch or repository details.
  - Added `get_remote_version()` method to fetch version from remote repository.
  - **Files Modified**: `gui/main_window.py`, `utils/git_updater.py`

### Added

- **Step 4 Directory Memory** - File dialog now remembers the last selected directory.
  - When copying raw TIFF files, dialog opens in the last directory used.
  - Directory path is saved in batch configuration at `step_configurations.step4.last_copy_directory`.
  - Includes validation to ensure saved directory exists before using it.
  - Falls back to `C:\` if saved directory no longer exists.
  - Improves workflow for users repeatedly copying from the same source location.
  - **Files Modified**: `gui/dialogs/step4_dialog.py`

- **Update Dialog Test Script** - Created test utility for previewing update dialogs.
  - New `test_update_dialog.py` script allows testing all update dialog scenarios without git operations.
  - Test buttons for: Update Available, Already Up-to-Date, Uncommitted Changes, Update Complete, Update Failed.
  - No version modifications or git operations required for testing.
  - **Files Created**: `test_update_dialog.py`

- **Update Testing Documentation** - Comprehensive guide for testing update features.
  - Documents 4 different methods for testing update dialogs and flows.
  - Includes best practices, testing checklist, and troubleshooting tips.
  - Explains how to test without continuous version releases.
  - **Files Created**: `notes/TESTING_HPM-update-route.md`

---

## HPM [0.1.7e] - 2026-01-19

### Changed

- **Centralized Logging - Phase 2** - Enhanced logging across core components and all step dialogs.
  - Replaced direct `print()` statements and `QMessageBox` calls with new centralized `log_manager` methods in `hstl_framework.py` and all `gui/dialogs/step*.py` files.
  - Updated `core/pipeline.py` and `steps/base_step.py` to use the new `success` logging level for completion messages.
  - The new `ColoredFormatter` now handles emojis, colors, and component names, ensuring consistent log output.
- **Improved Error Handling** - Added specific `try...except` block for `FileNotFoundError` during project initialization in `hstl_framework.py` to provide a more user-friendly error message.

### Added

- **SUCCESS Logging Level** - Added a custom `SUCCESS` logging level for more semantic logging of successful operations.

---

## HPM [0.1.7d] - 2026-01-18 20:15 CST

### Changed

- **Centralized Version Management** - Version info now maintained in single location (2026-01-18 20:15 CST)
  - `__init__.py` is now the single source of truth for `__version__` and `__commit_date__`
  - All UI components import version at runtime instead of hardcoding
  - Reduces manual version updates from 11 files to just 4 files
  - **Files Modified**:
    - `__init__.py` - Added `__commit_date__` variable
    - `gui/__init__.py` - Now imports from parent
    - `gui/hstl_gui.py` - Imports version instead of hardcoding
    - `gui/main_window.py` - Uses imported variables for title bar and About dialog
    - `gui/widgets/step_widget.py` - Uses imported variables
    - `gui/widgets/batch_list_widget.py` - Uses imported variables
    - `Project_Rules.md` - Updated version checklist

---

## HPM [0.1.7c] - 2026-01-18 10:30 CST

### Changed

- **Step 2 Dialog** - Dialog no longer auto-closes after successful CSV completion (2026-01-18 10:30 CST)
  - Removed automatic `self.accept()` call after CSV conversion completes
  - User can now review the completion status and close the dialog manually
  - Allows users to see all status messages before dismissing the dialog
  - **Files Modified**: `gui/dialogs/step2_dialog.py`

- **Step 3 Label** - Changed from "Test for Unicode scrabbling" to "Test for Mojibake" (2026-01-18 10:30 CST)
  - "Mojibake" is the standard technical term for garbled text from encoding issues
  - More concise and recognizable terminology
  - **Files Modified**: `gui/widgets/step_widget.py`

---

## HPM [0.1.7b] - 2026-01-17 16:05 CST

### Added

- **Logging Toggle Feature** - Master on/off switch for logging in Settings dialog (2026-01-17 11:41 CST)
  - New "Enable logging" checkbox at top of Logging settings group
  - When disabled, all log messages are suppressed (logger level set above CRITICAL)
  - Other logging controls (verbosity, per-batch, buffer) are grayed out when disabled
  - Setting persists across app restarts via QSettings
  - Respects disabled state when `setup_logger()` is called from framework initialization
  - **Files Modified**: `utils/log_manager.py`, `utils/logger.py`, `gui/dialogs/settings_dialog.py`, `gui/main_window.py`

- **Console Capture Feature** - Route print() statements to logging system (2026-01-17 11:41 CST)
  - New "Capture console output" checkbox in Settings dialog
  - Captures all print() statements and stdout/stderr writes from worker threads
  - Messages appear in Log dialog with `[console]` prefix
  - Useful for capturing output from external tools (e.g., g2c.py during Step 2)
  - Uses thread-local flag to prevent infinite loops when log messages write to console
  - Pattern matching skips already-formatted log messages to prevent duplication
  - RLock prevents deadlocks when logging from captured output
  - Debug mode available (`_debug = True`) for troubleshooting capture issues
  - **Files Created**: `utils/console_capture.py`
  - **Files Modified**: `utils/log_manager.py`, `gui/dialogs/settings_dialog.py`, `gui/main_window.py`

- **Batch Name in Log Viewer** - Display current batch name in log viewer header (2026-01-17 15:54 CST)
  - Shows "Logs - {batch_name}" in the header above filter bar
  - Pop-out Log Viewer dialog also shows batch name in title bar
  - Helps users confirm which batch's logs they are viewing
  - Updates automatically when switching batches
  - **Files Modified**: `gui/widgets/enhanced_log_widget.py`, `gui/dialogs/log_viewer_dialog.py`, `gui/main_window.py`

### Changed

- **Step 1 Dialog** - File browser now opens in user's Downloads folder by default (2026-01-17)
  - Excel spreadsheets are typically downloaded, so Downloads is the most logical starting location
  - Uses `os.path.expanduser("~/Downloads")` for cross-platform compatibility
  - **Files Modified**: `gui/dialogs/step1_dialog.py`

- **Step 1 Label** - Changed from "Excel Spreadsheet Completed" to "Excel Spreadsheet Download" (2026-01-17)
  - Better reflects the action of downloading/obtaining the spreadsheet
  - **Files Modified**: `gui/widgets/step_widget.py`

- **Help/About Dialog** - Updated title and content (2026-01-17)
  - Title changed to "HSTL Photo Metadata Framework [ HPM ]"
  - Header changed to match new title
  - Description changed from "comprehensive" to "end-to-end" framework
  - Added OS platform information (shows full Windows version info like "Windows-10-10.0.19045-SP0")
  - **Files Modified**: `gui/main_window.py`

---

## HPM [0.1.7] - 2026-01-16

### Changed

- **Excel Migration** - Migrated from Google Sheets to local Excel spreadsheet workflow (2026-01-16)
  - Step 1 now handles Excel (.xlsx/.xls) files instead of Google Sheets
  - Removed Google API dependencies for metadata input
  - Excel files are validated and copied to batch input directory
  - Row 2 validation updated to expect batch title instead of blank row
  - CSV export now uses correct batch output directory path

### Fixed

- **Step 1 Dialog** - Fixed `AttributeError` for missing `get_data_directory` method
  - Changed to use `config_manager.get('project.data_directory')` pattern
- **Step 2 Dialog** - Fixed CSV export to use absolute path instead of relative `output/export.csv`
- **Step 2 Dialog** - Fixed step completion not updating in UI after successful conversion
  - Added missing `update_step_status()`, `save_config()`, and `accept()` calls
  - Step 2 now properly shows as complete in Current Batch and Batches dialogs
- **Step 4 Dialog** - Fixed `IndentationError` on `_on_error` method (missing indentation)
- **Step 4 Dialog** - Fixed `AttributeError` for missing `data_directory` attribute
  - Changed to use `config_manager.get('project.data_directory')` pattern
- **Batch Info Dialog** - Fixed `IndentationError` in `step_names` dictionary
- **CSV Export** - Removed blocking `input()` call that prevented GUI operation
  - Now auto-continues with available mappings when some row 3 values are missing

### Removed

- Google Sheets integration (moved to Excel-based workflow)
- Row 2 blank validation requirement
- **Step 5 Dialog** - Removed "Search for Missing TIFFs" button and feature
  - Feature was too slow for practical use (recursive filesystem search)
  - Users can search for missing files offline if needed
  - Missing TIFF list still displayed in output for reference

---

## HPM [0.1.5e] - 2026-01-15

### Added

- **Comprehensive Logging System** - Enhanced logging infrastructure for documentation and troubleshooting (2026-01-15)

  - **New Module**: `utils/log_manager.py` - Centralized logging manager singleton
    - Session-level logging with rotating file handlers (10MB max, 5 backups)
    - Per-batch log files in each batch's data directory
    - Configurable verbosity levels: Minimal, Normal, Detailed
    - Thread-safe GUI integration via Qt signals
    - `LogRecord` dataclass with batch_id, step number, and timestamp metadata
    - Convenience methods: `step_start()`, `step_complete()`, `step_error()`
  - **Enhanced Log Viewer**: `gui/widgets/enhanced_log_widget.py`
    - Filter bar with Level, Batch, Step, and Search filters
    - Color-coded log entries by severity level
    - Auto-scroll with pause option
    - Export logs to file with filter information
    - Pop-out button for separate window
  - **Pop-out Log Window**: `gui/dialogs/log_viewer_dialog.py`
    - Independent window for multi-monitor workflows
    - Same filtering and search capabilities as embedded viewer
    - Accessible via View menu (Ctrl+L) or Pop Out button
  - **Settings Integration**: Added Logging section to Settings dialog
    - Verbosity Level dropdown (Minimal/Normal/Detailed)
    - Per-batch logging checkbox
    - GUI log buffer size spinbox (100-10000 lines)
  - **Framework Integration**:
    - `BatchContextAdapter` in `utils/logger.py` for batch-aware logging
    - `batch_id` parameter added to `ProcessingContext` in `steps/base_step.py`
    - LogManager integrated into `hstl_framework.py` for CLI logging
    - Step 5 dialog updated as example pattern for step logging
  - **Configuration Updates**: New settings in `config/settings.py`
    - `verbosity`: 'minimal', 'normal', or 'detailed'
    - `per_batch_logging`: Enable/disable per-batch log files
    - `gui_log_buffer`: Maximum lines in GUI log viewer
  - **Log File Organization**:
    - Session logs: `~/.hstl_photo_framework/logs/session_YYYYMMDD_HHMMSS.log`
    - Per-batch logs: `{batch_data_directory}/logs/batch_{id}.log`
  - **Features**:
    - Real-time log display with color-coded severity levels
    - Filter by log level (DEBUG, INFO, WARNING, ERROR)
    - Filter by specific batch or step
    - Full-text search across log messages
    - Export filtered logs with metadata
    - Persistent verbosity settings via QSettings
  - **Files Created**:
    - `utils/log_manager.py` - Centralized logging manager (300+ lines)
    - `gui/widgets/enhanced_log_widget.py` - Advanced log viewer widget (350+ lines)
    - `gui/dialogs/log_viewer_dialog.py` - Pop-out log window dialog (80 lines)
  - **Files Modified**:
    - `utils/logger.py` - Added BatchContextAdapter and get_batch_logger()
    - `config/settings.py` - Added verbosity, per_batch_logging, gui_log_buffer settings
    - `gui/main_window.py` - Integrated EnhancedLogWidget, pop-out, View menu item
    - `gui/dialogs/settings_dialog.py` - Added Logging settings section
    - `steps/base_step.py` - Added batch_id to ProcessingContext
    - `hstl_framework.py` - Added LogManager integration
    - `gui/dialogs/step5_dialog.py` - Added logging as example pattern

### Fixed

- **Logging System Bug** - Fixed log messages not appearing in GUI after batch selection (2026-01-15)
  - **Root Cause**: `setup_logger()` in `utils/logger.py` was clearing all handlers including the GUI log handler when `framework.initialize()` was called during batch selection
  - **Solution**: Modified `setup_logger()` to preserve LogManager-owned handlers (GUILogHandler, BatchFileHandler, and session handler)
  - Added `_log_manager_owned` marker to session handler for preservation
  - Added logging for batch actions (complete, archive, reactivate, remove)
  - Batch creation and deletion now properly logged in GUI viewer

- **Added logging to all step dialogs** (2026-01-15)
  - Steps 2, 3, 4, 6, 7, 8 now log start/complete/error events with batch context
  - Each step logs with `batch_id` and `step` number for filtering in log viewer
  - Updated `step_widget.py` to pass `batch_id` to all step dialogs
  - Files modified: `step2_dialog.py`, `step3_dialog.py`, `step4_dialog.py`, `step6_dialog.py`, `step7_dialog.py`, `step8_dialog.py`, `step_widget.py`

## HPM [0.1.5d] - 2026-01-15 05:52

### Added

- **Comprehensive Test Infrastructure** - Complete testing framework for HPM system (2026-01-15 05:52 CST)
  
  - **Test Framework Structure**: Complete pytest-based testing infrastructure
    - `tests/unit/` - Unit tests for individual components and modules
    - `tests/integration/` - Integration tests for workflow testing
    - `tests/gui/` - GUI testing framework for PyQt6 interface
    - `tests/fixtures/` - Test data and mock objects
    - `conftest.py` - Global pytest configuration and fixtures
  - **Smoke Tests**: Basic functionality validation
    - `tests/unit/test_smoke.py` - Initial smoke test for system validation
    - Validates core module imports and basic functionality
    - Provides foundation for comprehensive test suite development
  - **PyProject Configuration**: Modern Python project configuration
    - `pyproject.toml` - Project metadata and pytest configuration
    - Configured for pytest with coverage reporting
    - Python 3.12+ compatibility specified
    - Author and repository information included
  - **Test Planning Documentation**:
    - `tests/PLAN_HPM-Testing.md` - Comprehensive testing strategy and roadmap
    - Documents test phases, priorities, and implementation approach
    - Outlines unit, integration, and GUI testing methodologies
    - Provides timeline and resource allocation for testing efforts
  - **Test Completion Report**:
    - `tests/REPORT_Phase 2.5.1 Complete - Test Infrastructure.md` - Phase completion documentation
    - Documents implementation of Phase 2.5.1 test infrastructure
    - Details all components created and their purposes
    - Provides status report and next phase recommendations
  - **PyGit Cloning Tool**: Python-based Git repository management
    - `portable/PyGitClone.py` - Standalone Git cloning utility
    - Facilitates automated repository setup for testing environments
    - Cross-platform compatibility for development and deployment
  - **Coverage Integration**: Test coverage measurement and reporting
    - `.coverage` file generated during test execution
    - Provides insights into test coverage across codebase
    - Helps identify areas needing additional test coverage
  - **Development Benefits**:
    - Enables comprehensive regression testing for future changes
    - Supports continuous integration and automated testing workflows
    - Improves code quality and reliability through systematic testing
    - Foundation for test-driven development practices
  - **Files Created**:
    - `tests/` directory structure with 7 subdirectories
    - `tests/conftest.py` - Pytest configuration (48 lines)
    - `tests/unit/test_smoke.py` - Basic smoke tests (25 lines)
    - `tests/PLAN_HPM-Testing.md` - Testing strategy document (21,953 bytes)
    - `tests/REPORT_Phase 2.5.1 Complete - Test Infrastructure.md` - Completion report (3,549 bytes)
    - `pyproject.toml` - Project configuration (3,313 bytes)
    - `portable/PyGitClone.py` - Git cloning utility (15,206 bytes)

## HPM [0.1.5c] - 2026-01-13 10:30

### Added

- **About Dialog Enhancement** - Added Python executable and HPM code location information (2026-01-13 10:30 CST)
  - Shows which Python executable is being used for quick verification
  - Displays HPM code location (full path to hstl_gui.py)
  - Information displayed in small, subdued font at bottom of About dialog
  - Text is selectable for easy copying
  - Helps developers and users quickly identify which Python instance is running
  - **Files Modified**:
    - `gui/main_window.py` - Enhanced About dialog with system information

### Changed

- **Help Menu Cleanup** - Removed redundant "Check for Updates" menu item (2026-01-13 10:30 CST)
  - "Get Latest Updates" menu item covers both checking and updating
  - Simplified Help menu structure
  - Reduces user confusion with duplicate functionality
  - **Files Modified**:
    - `gui/main_window.py` - Removed "Check for Updates" menu item

## HPM [0.1.5b] - 2026-01-12 22:18

### Changed

- **Help Menu Streamlining** - Removed antiquated Quick Start Guide (2026-01-12 22:14 CST)
  - Removed Quick Start Guide menu item from Help menu
  - User Guide is sufficient for documentation
  - Reassigned F1 keyboard shortcut to User Guide
  - Removed unused `_show_quickstart()` method (36 lines)
  - Cleaner, more focused Help menu structure
  - **Files Modified**:
    - `gui/main_window.py` - Removed Quick Start Guide menu item and method

- **UI Consistency Improvement** - Added version label to Batches tab (2026-01-12 22:18 CST)
  - Added version and date/time stamp to Batches tab header
  - Matches styling from Current Batch tab (10pt font, right-aligned)
  - Format: v0.1.5b | 2026-01-12 22:18 CST
  - Added spacing for better visual separation
  - Consistent version display across all major tabs
  - **Files Modified**:
    - `gui/widgets/batch_list_widget.py` - Added version label to header

## HPM [0.1.5a] - 2026-01-12 20:03

### Added

- **Get Latest Updates Feature** - Integrated git pull functionality for automatic updates (2026-01-12 20:03 CST)
  
  - **New Module**: `utils/git_updater.py` - Git operations for safe repository updates
    - Automatic git repository detection from module location
    - Uncommitted changes detection with detailed file status
    - Current branch identification
    - Remote URL retrieval
    - Safe git pull with comprehensive error handling
    - Parse git output for update statistics (files changed, insertions, deletions)
    - 30-second timeout protection
  - **GUI Integration**: `gui/main_window.py`
    - New menu item: Help → Get Latest Updates
    - Background thread implementation using `GitUpdateThread` for non-blocking UI
    - Progress dialog during git pull operation
    - Multiple safety checks before updating
    - Confirmation dialogs at each step
    - Detailed success/error reporting
  - **Safety Features**:
    - Detects if installation is in a git repository
    - Warns about uncommitted changes before pulling
    - Checks if updates are available before pulling
    - Requires user confirmation before executing git pull
    - Cannot cancel git pull mid-operation (prevents corruption)
    - Timeout protection prevents hanging operations
  - **User Experience**:
    - "Already up-to-date" message when no updates available
    - Shows number of commits available when updates exist
    - Displays current branch and remote URL
    - Shows update statistics after successful pull
    - Reminds user to restart HPM for changes to take effect
    - Handles non-git installations gracefully
  - **Error Handling**:
    - Not in git repository detection
    - Uncommitted changes warning with option to continue
    - Network errors and timeouts
    - Git command failures with detailed messages
    - Merge conflict detection and reporting
  - **Testing**:
    - Built-in test function in `git_updater.py`
    - Validates repository detection
    - Tests branch and remote identification
    - Checks uncommitted changes detection
    - Verifies update availability checking
  - **Benefits**:
    - Users can update HPM with one click
    - No need to manually run git pull commands
    - Safe updates with multiple confirmation steps
    - Clear feedback on what changed
    - Works seamlessly with existing git workflow
  - **Files Added**:
    - `utils/git_updater.py` - Git updater module (301 lines)
  - **Files Modified**:
    - `gui/main_window.py` - Added git update integration (152 new lines)

## HPM [0.1.5] - 2026-01-12 10:15

### Added

- **Check for Updates Feature** - Integrated GitHub release version checking (2026-01-12 10:15 CST)
  
  - **New Module**: `utils/github_version_checker.py` - Standalone GitHub version checker
    - Semantic version comparison (handles major.minor.patch format)
    - Asynchronous version checking with background threads
    - Robust error handling for network issues and API failures
    - Reusable across PyQt6 applications
  - **GUI Integration**: `gui/main_window.py`
    - New menu item: Help → Check for Updates
    - Background thread implementation for non-blocking UI
    - Update available dialog with release notes display
    - Direct download link to GitHub releases page
    - Friendly error messages for common scenarios (404, network errors)
  - **Repository Configuration**:
    - Monitors juren53/HST-Metadata GitHub repository
    - Checks for latest release tags
    - Compares current version (0.1.5) with published releases
  - **User Experience**:
    - Manual check via Help menu
    - Non-intrusive status bar updates
    - Clear messaging when up-to-date or updates available
    - One-click access to download page
  - **Testing**:
    - Added `test_version_checker.py` - Standalone test script
    - Validates version checking functionality
    - Tests API connectivity and error handling
  - **Benefits**:
    - Users can easily check for new HPM releases
    - Automatic version comparison prevents manual checking
    - Seamless integration with GitHub release workflow
    - Consistent with TagWriter implementation
  - **Files Added**:
    - `utils/github_version_checker.py` - Version checker module (280 lines)
    - `test_version_checker.py` - Test script (61 lines)
  - **Files Modified**:
    - `gui/main_window.py` - Added version checking integration (113 new lines)

  
  - **New Module**: `utils/git_updater.py` - Git operations for safe repository updates
    - Automatic git repository detection from module location
    - Uncommitted changes detection with detailed file status
    - Current branch identification
    - Remote URL retrieval
    - Safe git pull with comprehensive error handling
    - Parse git output for update statistics (files changed, insertions, deletions)
    - 30-second timeout protection
  - **GUI Integration**: `gui/main_window.py`
    - New menu item: Help → Get Latest Updates
    - Background thread implementation using `GitUpdateThread` for non-blocking UI
    - Progress dialog during git pull operation
    - Multiple safety checks before updating
    - Confirmation dialogs at each step
    - Detailed success/error reporting
  - **Safety Features**:
    - Detects if installation is in a git repository
    - Warns about uncommitted changes before pulling
    - Checks if updates are available before pulling
    - Requires user confirmation before executing git pull
    - Cannot cancel git pull mid-operation (prevents corruption)
    - Timeout protection prevents hanging operations
  - **User Experience**:
    - "Already up-to-date" message when no updates available
    - Shows number of commits available when updates exist
    - Displays current branch and remote URL
    - Shows update statistics after successful pull
    - Reminds user to restart HPM for changes to take effect
    - Handles non-git installations gracefully
  - **Error Handling**:
    - Not in git repository detection
    - Uncommitted changes warning with option to continue
    - Network errors and timeouts
    - Git command failures with detailed messages
    - Merge conflict detection and reporting
  - **Testing**:
    - Built-in test function in `git_updater.py`
    - Validates repository detection
    - Tests branch and remote identification
    - Checks uncommitted changes detection
    - Verifies update availability checking
  - **Benefits**:
    - Users can update HPM with one click
    - No need to manually run git pull commands
    - Safe updates with multiple confirmation steps
    - Clear feedback on what changed
    - Works seamlessly with existing git workflow
  - **Files Added**:
    - `utils/git_updater.py` - Git updater module (301 lines)
  - **Files Modified**:
    - `gui/main_window.py` - Added git update integration (152 new lines)

## HPM [0.1.4] - 2026-01-07

### Added

- **USB Portable Setup System** - Complete portable WinPython solution for USB drives (Wed 07 Jan 2026)
  
  - **New Directory**: `portable/` - Comprehensive portable USB deployment system
  - **Portable Launcher**: `LAUNCH_HPM_PORTABLE.bat` - Drive-letter-agnostic batch launcher
    - Uses `%~d0` magic variable to detect current USB drive letter automatically
    - Works regardless of which drive letter (D:, E:, F:, etc.) Windows assigns
    - Activates WinPython environment and launches HPM GUI from USB
    - Solves the problem of hardcoded paths breaking when USB drive letter changes
  - **Cross-Platform Development Support**:
    - `launch_hpm_portable.sh` - Linux equivalent for testing application logic
    - `validate_windows_scripts.sh` - Validates Windows batch files for common issues
    - `fix_line_endings.sh` - Converts line endings to Windows format (CRLF)
  - **Comprehensive Documentation**:
    - `portable/README.md` - Overview and quick navigation guide
    - `portable/QUICK_START.md` - Simple 3-step guide for USB portable setup
    - `portable/USB_PORTABLE_SETUP.md` - Detailed portable WinPython guide with examples
    - `portable/CROSS_PLATFORM_STRATEGY.md` - How to develop Windows scripts on Linux
    - `portable/LINUX_WORKFLOW_CHEATSHEET.md` - Quick reference for Linux development
  - **Line Ending Management**:
    - `.gitattributes` - Ensures proper CRLF line endings for Windows batch files
    - Git configuration prevents "mixed line endings" warnings
    - Cross-platform compatibility maintained between Linux development and Windows deployment
  - **Features**:
    - Automatic drive letter detection using Windows batch variables
    - No manual path editing required after initial setup
    - Works on any Windows computer regardless of USB drive letter assignment
    - Complete directory structure validation before execution
    - Enables true portable Python development environment
  - **Use Cases**:
    - Run HPM system from USB drive on different computers
    - No local installation required on target computers
    - Ideal for fieldwork, demonstrations, or shared workstations
    - WinPython and HPM Framework travel together on USB

- **WinPython Activation Documentation** - Detailed explanation of WinPython environment activation (Tue 06 Jan 2026)
  
  - **New File**: `launcher/WinPythons_activate-bat_explained.md`
  - Explains what `activate.bat` does and how it works
  - Documents WinPython path structure and versioning
  - Describes environment variable modification during activation
  - Clarifies difference between WinPython activation and Python venv
  - Provides context for understanding portable launcher operations

- **Copyright Watermark Image** - Branding asset for GUI and watermarking (Tue 06 Jan 2026)
  
  - **New File**: `gui/Copyright_Watermark.png` (33.5 KB)
  - Used for GUI branding and restricted image watermarking
  - Professional institutional branding for HSTL Photo Framework
  - Applied during Step 8 watermark processing for restricted images

### Changed

- **HPM Installation Documentation** - Added alternate manual startup instructions (Tue 06 Jan 2026)
  - New section in `HPM_Installation.md` documenting manual application launch
  - Step-by-step instructions for launching from user home directory
  - Alternative to using HPM Launcher for users preferring manual control
  - Documents three-step process: activate WinPython, navigate to Framework, launch GUI
  - Single-line command alternative provided for advanced users

## HPM [0.1.3i] - 2026-01-06

### Changed

- **WinPython Upgrade** - Updated to latest Python 3.13.11 release (Tue 06 Jan 2026)
  
  - **Previous Version**: WinPython 3.12.0.1b5 (Python 3.12.0, November 2023)
  - **New Version**: WinPython 3.13.11.0slim_post1 (Python 3.13.11, December 2025)
  - **Installation Process**:
    - Downloaded WinPython64-3.13.11.0slim_post1.exe (623 MB) from GitHub releases
    - Removed old installation: `%USERPROFILE%\winpython\WPy64-31201b5\`
    - Extracted new version to: `%USERPROFILE%\winpython\WPy64-313110\`
    - Verified Python 3.13.11 installation and activation
  - **Dependency Reinstallation**:
    - All HPM dependencies reinstalled from `requirements.txt`
    - Core packages verified: PyYAML, pandas, pydantic, Pillow
    - GUI frameworks: PyQt6 6.10.1, wxPython 4.2.4
    - Google services: google-auth 2.41.1, gspread 6.2.1, google-api-python-client 2.187.0
    - New packages: ftfy 6.3.1, structlog 25.5.0, PyExifTool 0.5.6, pytest-cov 7.0.0
  - **Configuration Updates**:
    - Updated `launcher\launcher_config.json` with new WinPython path
    - Changed: `WPy64-31201b5` → `WPy64-313110`
    - HPM Launcher tested and verified working with Python 3.13.11
  - **Benefits**:
    - Latest Python 3.13 features and performance improvements
    - Updated package versions with security patches and bug fixes
    - 2+ year version jump ensures long-term support
  - **Files Modified**:
    - `launcher\launcher_config.json` - Updated winpython_activate path (line 3)

- **Launcher Documentation Update** - Added direct execution instructions (Tue 06 Jan 2026)
  
  - **New Section**: "Option 1: Run Directly from Launcher Directory" in LAUNCHER_README.md
  - **Execution Commands**:
    - Using WinPython: `%USERPROFILE%\winpython\WPy64-313110\python\python.exe launcher.py`
    - If Python in PATH: `python launcher.py`
    - One-liner from anywhere: Full path to python.exe and launcher.py
  - **Automatic Behaviors Documented**:
    - Reads `launcher_config.json` from same directory
    - Activates WinPython environment automatically
    - Launches HPM GUI application
    - Creates logs at `%USERPROFILE%\hpm_launcher.log`
  - **Configuration Example Updated**:
    - Updated WinPython version in config example: `WPy64-31201b5` → `WPy64-313110`
    - Reflects current Python 3.13.11 installation
  - **Documentation Reorganization**:
    - Renumbered existing options to Option 2 and Option 3
    - Made direct execution the primary recommended method
  - **Benefits**:
    - Users can run launcher without building executable
    - No desktop shortcut creation required
    - Simpler workflow for development and testing
    - Clear commands for all user scenarios
  - **Files Modified**:
    - `launcher\LAUNCHER_README.md` - Added direct execution section and updated config example

### Added

- **HPM Installation Checklist Table of Contents** - Enhanced documentation navigation (Tue 06 Jan 2026)
  - **New Feature**: Comprehensive hyperlinked table of contents at top of HPM_Installation.md
  - **Navigation Links**:
    - All 8 main installation sections (Prerequisites through Installation Complete)
    - 40+ subsection links for quick access to specific installation steps
    - Hierarchical indentation showing document structure
  - **Link Structure**:
    - Main sections: Prerequisites, WinPython installation, GitHub download, Dependencies, etc.
    - Subsections: Installation methods, verification steps, configuration details
    - Deep links to specific procedures (Google Cloud setup, launcher configuration, testing)
  - **Benefits**:
    - Faster navigation to specific installation steps
    - Clear overview of entire installation process
    - Improved user experience for long documentation
    - Works in all Markdown viewers (GitHub, VS Code, etc.)
  - **Files Modified**:
    - `HPM_Installation.md` - Added table of contents section (lines 7-45)

## HPM [0.1.3h] - 2026-01-06

### Changed

- **WinPython Installation Method** - Added winget as recommended installation approach (Tue 06 Jan 2026)
  - **New Primary Method**: `winget install winpython` - simplified installation using Windows Package Manager
  - **Installation Process**:
    - Navigate to user root directory (`%USERPROFILE%`)
    - Run `winget install winpython` command
    - Follow on-screen prompts for automatic installation
  - **Alternative Method**: Manual download and installation retained as fallback option
    - Manual method still available for users without winget
    - Download from WinPython official site (https://winpython.github.io/)
    - Extract and verify installation structure
  - **Documentation Updates**:
    - Reorganized installation section with clear method prioritization
    - Added winget availability note (Microsoft Store - "App Installer")
    - Separated "Verify Installation Structure" as standalone subsection
    - Improved readability with clearer section headers
  - **Benefits**:
    - Faster installation process
    - Automatic dependency handling
    - Simplified user experience for Windows users
    - Maintains compatibility with existing installation workflows
  - **Files Modified**:
    - `HPM_Installation.md` - Updated WinPython installation section (lines 15-58)

## HPM [0.1.3g] - 2026-01-05

### Added

- **HPM Installation Checklist** - Comprehensive installation guide with step-by-step verification (Mon 05 Jan 2026)
  - **New Documentation**: `HPM_Installation.md` - Complete installation checklist for HPM system
  - **Installation Sections**:
    1. Prerequisites verification (Windows 10+, admin access, disk space)
    2. WinPython installation and configuration
    3. GitHub repository cloning (`git clone https://github.com/juren53/HST-Metadata.git`)
    4. Python dependencies installation (`pip install -r requirements.txt`)
    5. Helper tools setup (ExifTool with PATH configuration)
    6. Google credentials configuration (OAuth 2.0 setup)
    7. HPM Launcher configuration and desktop shortcut creation
    8. Complete installation verification (CLI and GUI testing)
  - **Features**:
    - Checkbox format for progress tracking through installation
    - Detailed verification steps for each component
    - Quick Reference Card for daily startup commands
    - Installation Summary table with component locations
    - Troubleshooting references and documentation links
    - Optional helper tools section (CSV Record Viewer, image viewers)
  - **Comprehensive Coverage**:
    - WinPython download, installation, and verification
    - Git clone command with repository structure validation
    - Complete dependency installation with import testing
    - ExifTool installation with system PATH configuration
    - Google Cloud Project setup with API enablement
    - OAuth 2.0 credential creation and first-time authentication
    - Launcher configuration file verification and testing
    - Test batch creation and cleanup procedures
  - **Installation Path Documentation**:
    - Framework: `%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework`
    - WinPython: `%USERPROFILE%\winpython\WPy64-31201b5\`
    - ExifTool: `C:\Program Files\ExifTool\` (in system PATH)
    - Credentials: `client_secret.json` in Framework directory
  - **Files Created**:
    - `HPM_Installation.md` - Master installation checklist document

## HPM [0.1.3f] - 2026-01-05

### Changed

- **Quickstart Guide Update** - Enhanced documentation for HPM Launcher and manual startup (Mon 05 Jan 2026)
  - **New Section**: "Starting the HPM Application" added after Prerequisites
  - **HPM Launcher Documentation**:
    - Recommended method using HPM Launcher executable or Python script
    - Lists automatic features (WinPython activation, directory navigation, GUI launch)
    - Benefits highlighted: one-click startup, path validation, error logging
    - Reference to detailed launcher documentation
  - **Manual HPM Startup Section**:
    - Step-by-step instructions for manual application launch
    - Three embedded commands from HPM Launcher documented:
      1. Activate WinPython environment via activate.bat
      2. Navigate to Framework directory using cd
      3. Launch GUI application using python gui\hstl_gui.py
    - Environment variable usage explained (`%USERPROFILE%`)
    - Single-line command alternative provided for advanced users
  - **Updated References**:
    - Added launcher documentation link to "Need Help?" section
    - Updated "Last updated" date to 2026-01-05
  - **Files Modified**:
    - `docs/QUICKSTART.md` - Added startup sections and updated references

## HPM [0.1.3e] - 2026-01-03 20:46 CST

### Added

- **Zoom/Font Scaling Feature** - Font-based zoom functionality for improved accessibility (Sat 03 Jan 2026 08:46:00 PM CST)
  - **Zoom Range**: 75% to 200% in discrete steps (75%, 85%, 100%, 115%, 130%, 150%, 175%, 200%)
  - **Multiple Control Methods**:
    - View menu with Zoom In/Out/Reset actions
    - Keyboard shortcuts: `Ctrl++` or `Ctrl+=` (zoom in), `Ctrl+-` (zoom out), `Ctrl+0` (reset to 100%)
    - Mouse wheel: Hold `Ctrl` and scroll to zoom in/out
  - **Features**:
    - Global zoom applied consistently across all windows and tabs
    - Persistent zoom level - saves to settings and restores on app restart
    - Status bar feedback - shows "Zoom: X%" for 2 seconds when changed
    - Font scaling approach - Qt layouts automatically adjust widget sizes
  - **MVP Implementation** - Font-only scaling without widget-specific dimension code
    - Simple ~200 line implementation vs. complex 1000+ line alternative
    - Leverages Qt's built-in layout system for automatic size adjustments
    - All text elements scale: buttons, labels, tables, trees, menus, logs
    - Layout elements auto-adjust: button sizes, table row heights, tree item heights
  - **Architecture**:
    - ZoomManager singleton class following ThemeManager pattern
    - Signal/slot architecture for responsive UI updates
    - QSettings persistence using "ui/zoom_level" key
    - Base font size capture for accurate scaling calculations
    - Font size clamped to 8pt-24pt range for usability
  - **Files Created**:
    - `gui/zoom_manager.py` - ZoomManager singleton class with font scaling logic
  - **Files Modified**:
    - `gui/main_window.py` - Added View menu, keyboard shortcuts, mouse wheel support, zoom methods, persistence
    - `gui/hstl_gui.py` - Initialize ZoomManager with base font on startup
  - **Testing**:
    - Verified zoom works across all tabs (Batches, Current Batch, Configuration, Logs)
    - Confirmed theme integration - zoom persists when switching between Light/Dark themes
    - Tested persistence - zoom level restores correctly after app restart
    - All control methods working: menu, keyboard, mouse wheel

### Technical

- **Qt Font Scaling** - Application-wide font scaling with automatic widget updates
  - Uses `QApplication.setFont()` for global font changes
  - Iterates all widgets to force immediate font update on zoom change
  - Qt layouts automatically handle size adjustments for scaled fonts
  - No custom per-widget scaling code required
- **Zoom Manager Architecture** - Singleton pattern with settings persistence
  - Discrete zoom levels prevent fractional font sizes
  - Nearest zoom level detection for smooth increment/decrement
  - Signal emission for UI updates (status bar feedback)
  - Robust validation and clamping for corrupted settings

## HPM [0.1.3d] - 2026-01-03 19:10 CST

### Fixed

- **Menu Readability Issue** - Fixed dropdown menu text visibility in Light and Dark themes (Sat 03 Jan 2026 07:15:00 PM CST)
  - **Root Cause**: QMenu and QMenuBar widgets weren't properly styled by existing theme system
  - **Problem**:
    - Light Theme caused white text on white background (unreadable)
    - Dark Theme caused black text on dark background (unreadable)
    - Menus inherited system colors that conflicted with custom theme palettes
  - **Solution Implemented**:
    - Added comprehensive `get_menu_stylesheet()` method to ThemeManager
    - Generates CSS stylesheets for QMenu, QMenuBar, and all menu states
    - Integrated stylesheet application in `apply_theme()` method
    - Proper color contrast for all theme modes (Light, Dark, System Default)
  - **Menu Styling Features**:
    - Background and text colors match current theme
    - Hover effects with theme-appropriate highlight colors
    - Disabled item styling with proper contrast
    - Separator styling for visual menu organization
    - Consistent padding and spacing across all menus
    - Cross-platform compatibility (Windows, macOS, Linux)
  - **Files Modified**:
    - `gui/theme_manager.py` - Added menu stylesheet generation and integration
    - `gui/dialogs/theme_dialog.py` - Updated theme preview to include menu styling
    - Created `test_menu_theme.py` for testing menu theme functionality
  - **Verification**:
    - Successfully tested with all three theme modes
    - Menu readability maintained across File, Edit, Batch, Tools, and Help menus
    - Theme switching instantly updates menu appearance without restart
    - Professional appearance with WCAG AA contrast compliance

### Technical

- **Theme Architecture Enhancement** - Extended theme system to handle complex widget styling
- **CSS Integration** - Added PyQt6 stylesheet support alongside existing QPalette system
- **Cross-Platform Menu Rendering** - Ensured consistent menu appearance across operating systems
- **Theme Testing Framework** - Created dedicated test script for menu theme validation

## HPM [0.1.3c] - 2026-01-02 21:30

### Added

- **Requirements.txt Complete Review** - Comprehensive dependency analysis and updates (Fri 02 Jan 2026 09:30:00 PM CST)
  - **Critical Missing Dependencies Added**:
    - `PyExifTool>=0.5.0` - Essential for metadata operations in Steps 4-8
    - `gspread>=5.0.0` - Required for Google Sheets API integration
    - `wxPython>=4.1.0` - Needed for csv_record_viewer utility
  - **Requirements.txt Organization**:
    - Categorized dependencies by functional groups (Core, Image Processing, GUI, Google Services, Development)
    - Added comprehensive comments explaining each dependency's purpose
    - Updated version constraints for compatibility
    - Added external tool documentation (ExifTool command-line + Python wrapper)
  - **External Tool Requirements Clarified**:
    - Documented ExifTool requires BOTH command-line tool AND PyExifTool wrapper
    - Added installation instructions for Windows, macOS, and Linux
    - Included troubleshooting guidance for common issues
  - **Documentation Created**:
    - `INSTALLATION.md` - Complete installation guide with step-by-step instructions
    - `notes/REPORT_requirements-txt_review.md` - Comprehensive analysis report
    - Updated `README.md` with installation prerequisites
    - Updated `docs/QUICKSTART.md` to reference installation guide
  - **Verification Completed**:
    - All 17 dependencies tested and verified working
    - Installation procedures validated across different Python environments
    - External tool integration tested successfully
  - **Quality Improvements**:
    - Dependency coverage: 82% → 100%
    - Documentation quality: Minimal → Comprehensive
    - Installation clarity: Poor → Excellent
    - Risk mitigation: High → Low

### Technical

- **Dependency Testing Framework** - Created comprehensive test script to verify all imports
- **Version Constraint Validation** - Ensured compatibility across dependency stack
- **Platform-Specific Documentation** - Added Windows, macOS, and Linux installation notes
- **External Tool Integration** - Clarified relationship between ExifTool and PyExifTool

## HPM [0.1.3c] - 2026-01-03 10:00

### Changed

- **Version Label Updates** - Updated all version references from 0.1.3b to 0.1.3c

## HPM [0.1.3b] - 2026-01-02 20:05

### Changed

- **HPM Launcher Reconfiguration** - Launcher system updated for local execution (Fri 02 Jan 2026 08:05:00 PM CST)
  - Reconfigured launcher to run HPM system from local Framework directory instead of USB thumbdrive
  - Updated to execute from `C:\Users\<username>\Projects\HST-Metadata\Photos\Version-2\Framework`
  - Integrated WinPython environment activation (`activate.bat`) into launch sequence
  - Launcher now creates temporary batch file to: activate WinPython, change to Framework directory, run `python gui\hstl_gui.py`
  - Replaced PowerShell script execution with Python GUI application launch
  - Updated configuration to use environment variables (`%USERPROFILE%`) for multi-user portability
  - Changed hardcoded username "jimur" to `%USERPROFILE%` in all paths for easy deployment to other users
  - Renamed `thumbdrive_launcher.py` to `launcher.py` to reflect local execution purpose
  - Renamed executable output from `ThumbdriveLauncher.exe` to `HPMLauncher.exe`
  - Updated log filename from `thumbdrive_launcher.log` to `hpm_launcher.log`
  - Desktop shortcut label changed from "Thumbdrive Launcher" to "HPM Launcher"
  - Desktop shortcut description updated to "Launch HSTL Photo Metadata System"
  - All launcher scripts updated: `create_shortcut.ps1`, `create_desktop_shortcut.py`, `build_launcher.bat`, `INSTALL.ps1`
  - Updated `LAUNCHER_README.md` with new configuration examples and environment variable documentation
  - Added environment variable expansion support in launcher configuration (automatically expands `%USERPROFILE%`, `%HOMEDRIVE%`, etc.)
  - Path validation updated to check: base directory, WinPython activate script, and GUI script
  - Fixed USB drive health issues (D: drive had filesystem corruption, repaired with CHKDSK)
  - Successfully tested local execution - HPM GUI launches correctly from Framework directory

## HPM [0.1.3a] - 2025-12-31 13:45

### Added

- **Theme Selection Feature** - Comprehensive Light/Dark theme support with system default option (Wed 31 Dec 2025 01:45:00 PM CST)
  - New "Theme Selection..." menu item under Edit menu for easy access
  - Three theme modes: Light, Dark, and System Default (auto-detects OS theme)
  - Theme selection dialog with live preview showing colors before applying
  - Instant theme switching without application restart
  - Persistent theme preference saved to Windows Registry via QSettings
  - Custom color palettes designed for both Light and Dark themes
  - Light Theme: White background (#FFFFFF) with dark text, optimized for bright environments
  - Dark Theme: Dark background (#1E1E1E) with light text, optimized for low-light environments
  - System Default: Automatically detects and matches operating system theme preference
  - Theme-aware status colors that adapt to current theme (success green, warning orange)
  - Theme-aware batch status backgrounds (active aqua/cyan, completed light/steel blue, archived gray)
  - All existing UI elements automatically adapt to selected theme
  - Enhanced Settings dialog with "Appearance" section containing theme button
  - Professional color contrast ratios for accessibility (WCAG AA compliance)

### Changed

- **Theme-Aware Colors** - Updated hardcoded colors throughout UI to use theme manager
  - Step 1 hint text now uses theme-aware disabled text color
  - Step 2 URL display uses theme-aware link color and background
  - Step 5 status indicators (success/warning) use theme-aware semantic colors
  - Batch list widget status backgrounds use theme-aware status colors
  - All color changes apply instantly when theme is switched

### Technical

- **Theme Manager Architecture** - Singleton pattern with QPalette-based theme application
  - `gui/theme_manager.py` - Core theme management with ThemeManager singleton class
  - `gui/dialogs/theme_dialog.py` - Theme selection UI with radio buttons and preview widget
  - PyQt6 QPalette for native widget theming with supplementary stylesheets for custom elements
  - Signal/slot architecture for real-time theme updates across all widgets
  - Automatic theme initialization on application startup in `gui/hstl_gui.py`
  - Batch list widget automatically refreshes when theme changes
  - Theme colors stored in dataclass for type safety and easy access

## HPM [0.1.3] - 2025-12-18 16:15

### Added

- **Batch Projects Records Column** - Added CSV record count display to Batch Projects dialog (Thu 18 Dec 2025 04:30:00 PM CST)
  
  - New Records column shows count of Accession Numbers/ObjectNames from export.csv file
  - Counts records by checking Accession Number, ObjectName, and AccessionNumber fields
  - Display format: Integer count or "N/A" if export.csv doesn't exist
  - Positioned immediately after Batch ID column for logical grouping
  - Center-aligned for clean presentation alongside existing metrics

- **Batch Projects Size Column** - Added directory size display to Batch Projects dialog (2025-12-18 16:30 CST)
  
  - New Size column shows total disk space used by each batch directory
  - Recursive calculation includes all files and subdirectories in batch folder
  - Human-readable format with automatic unit scaling (B, KB, MB, GB, TB)
  - Display format: Formatted size (e.g., "1.5 MB", "500 KB") or "N/A" if inaccessible
  - Positioned after Records column to complete batch information grouping
  - Center-aligned for visual consistency with Records column

- **Performance Caching** - Added 30-second cache for expensive batch information calculations
  
  - CSV record counting and directory size calculations cached to improve responsiveness
  - Cache automatically cleared when refresh button is pressed or F5 key used
  - Prevents recalculation during rapid user interactions or batch switching
  - Ensures fresh data while maintaining performance for large directories

- **File Utility Enhancements** - Added utility functions for CSV and directory operations
  
  - Added `FileUtils.count_csv_records()` - counts records by Accession Numbers/ObjectNames
  - Added `FileUtils.get_directory_size()` - recursive directory size calculation with error handling
  - Added `FileUtils.format_file_size()` - human-readable size formatting with unit scaling
  - Robust error handling for missing files, permission issues, and malformed data
  - Cross-platform compatibility with proper encoding support

- **ftfy Dependency** - Added ftfy library for text encoding fixes (2025-12-17 01:49 CST)
  
  - Added ftfy>=6.0.0 to requirements.txt
  - Required for mojibake detection and text encoding repair
  - Supports Step 3 mojibake scan functionality in metadata processing

### Build

- **Enforced Line Endings** - Added `.gitattributes` to standardize line endings (LF for text files).
  - Ensures consistent line endings across different operating systems (Windows, Linux, macOS).
  - Prevents "mixed line endings" warnings and improves cross-platform compatibility.
  - Configures Git to normalize text files to LF on commit and convert to CRLF on Windows checkout.

## [Unreleased]

### Added

- **Thumbdrive Launcher Utility** - Complete Python-based launcher for running PowerShell scripts from thumbdrive (2025-12-29)
  
  - Robust launcher (`thumbdrive_launcher.py`) with comprehensive error handling
  - Smart drive detection with automatic wait for thumbdrive insertion (configurable timeout)
  - Required file validation ensures all dependencies exist before execution
  - Detailed logging to `%USERPROFILE%\thumbdrive_launcher.log` for troubleshooting
  - User-friendly GUI notifications for all error scenarios
  - JSON configuration file (`launcher_config.json`) for easy customization
  - Desktop icon creation with custom thumbdrive icon (blue USB design with "D:" label)
  - Build script (`build_launcher.bat`) for creating standalone .exe with PyInstaller
  - PowerShell shortcut creator (`create_shortcut.ps1`) for automated desktop setup
  - Icon generator (`create_icon.py`) creates multi-resolution .ico file with PIL/Pillow
  - Complete documentation in `LAUNCHER_README.md` with setup and troubleshooting guides
  - Handles edge cases: thumbdrive not inserted, missing files, script timeouts, PowerShell errors
  - Configurable script timeout protection (default 300 seconds)
  - Optional success notifications and auto-retry behavior

- **Batch Projects Records Column** - Added CSV record count display to Batch Projects dialog (2025-12-18 16:30 CST)
  
  - New Records column shows count of Accession Numbers/ObjectNames from export.csv file
  - Counts records by checking Accession Number, ObjectName, and AccessionNumber fields
  - Display format: Integer count or "N/A" if export.csv doesn't exist
  - Positioned immediately after Batch ID column for logical grouping
  - Center-aligned for clean presentation alongside existing metrics

- **Batch Projects Size Column** - Added directory size display to Batch Projects dialog (2025-12-18 16:30 CST)
  
  - New Size column shows total disk space used by each batch directory
  - Recursive calculation includes all files and subdirectories in batch folder
  - Human-readable format with automatic unit scaling (B, KB, MB, GB, TB)
  - Display format: Formatted size (e.g., "1.5 MB", "500 KB") or "N/A" if inaccessible
  - Positioned after Records column to complete batch information grouping
  - Center-aligned for visual consistency with Records column

- **Performance Caching** - Added 30-second cache for expensive batch information calculations
  
  - CSV record counting and directory size calculations cached to improve responsiveness
  - Cache automatically cleared when refresh button is pressed or F5 key used
  - Prevents recalculation during rapid user interactions or batch switching
  - Ensures fresh data while maintaining performance for large directories

- **File Utility Enhancements** - Added utility functions for CSV and directory operations
  
  - Added `FileUtils.count_csv_records()` - counts records by Accession Numbers/ObjectNames
  - Added `FileUtils.get_directory_size()` - recursive directory size calculation with error handling
  - Added `FileUtils.format_file_size()` - human-readable size formatting with unit scaling
  - Robust error handling for missing files, permission issues, and malformed data
  - Cross-platform compatibility with proper encoding support

- **ftfy Dependency** - Added ftfy library for text encoding fixes (2025-12-17 01:49 CST)
  
  - Added ftfy>=6.0.0 to requirements.txt
  - Required for mojibake detection and text encoding repair
  - Supports Step 3 mojibake scan functionality in metadata processing

## HPM [0.1.2] - 2025-12-16 20:30

### Changed

- **Step 2 Batch Title in CSV** - Automatically adds batch title to cell A2
  
  - After CSV conversion completes, batch title is appended to cell A2 in brackets
  - Format: "OriginalA2Content [BatchTitle]"
  - Example: "record.title [Lindsay_Test5a]"
  - Provides clear visual identifier of which batch the CSV belongs to
  - Prevents confusion when multiple batch CSV files are open simultaneously
  - Status message shows confirmation: "✓ Appended batch title '[BatchTitle]' to cell A2"
  - Includes error handling if batch title not set or CSV has less than 2 rows

- **Step 5 Credit Field** - Hardcoded to "Harry S. Truman Library"
  
  - Credit metadata tag now always set to "Harry S. Truman Library"
  - No longer reads Credit value from export.csv file
  - Ensures consistent institutional attribution across all TIFF files
  - Applied to all images processed through Step 5 metadata embedding

### Improved

- **Step 5 Verso File Handling** - Automatic copying of verso TIFF files
  - After metadata embedding completes, automatically searches for verso files
  - Identifies files containing '_verso' or '_Verso' in filename (case-insensitive)
  - Copies all verso TIFFs from input/tiff to output/tiff_processed directory
  - Ensures verso images are available for Step 6 processing alongside tagged siblings
  - Addresses issue where verso TIFFs appear in "TIFF FILES WITHOUT MATCHING CSV RECORDS" report
  - Verso files don't have metadata records but need to be processed with their non-verso counterparts
  - Provides detailed feedback showing which files were copied
  - Example output: "✓ Copied 15 verso file(s) to tiff_processed directory"
  - Graceful error handling if copying fails for individual files

## HPM [0.1.1] - 2025-12-14 18:25

### Improved

- **Real-Time Processing Feedback** - Enhanced user feedback across all processing steps
  
  - **Step 5 (Metadata Embedding)**: Added per-file progress messages
    - Shows file being processed with headline preview
    - Displays completion checkmark after metadata embedded
    - Enhanced progress checkpoints every 10 files
  - **Step 6 (JPEG Conversion)**: Added detailed conversion feedback
    - Shows TIFF → JPEG conversion progress for each file
    - Displays image dimensions and output file size
    - Shows quality setting in completion message
  - **Step 7 (JPEG Resizing)**: Already had real-time feedback (reference implementation)
  - **Step 8 (Watermarking)**: Added comprehensive status messages
    - Shows RESTRICTED/UNRESTRICTED status for each file
    - Displays dimensions and file size for all files
    - Shows opacity setting for watermarked files
    - Separate feedback for watermarked vs copied files
  - All steps now show progress checkpoints with file count tracker (e.g., "45/100 files completed")
  - Consistent feedback pattern across all processing steps

- **Step 5 Verso File Handling** - Automatic copying of verso TIFF files
  
  - After metadata embedding completes, automatically searches for verso files
  - Identifies files containing '_verso' or '_Verso' in filename (case-insensitive)
  - Copies all verso TIFFs from input/tiff to output/tiff_processed directory
  - Ensures verso images are available for Step 6 processing alongside tagged siblings
  - Addresses issue where verso TIFFs appear in "TIFF FILES WITHOUT MATCHING CSV RECORDS" report
  - Verso files don't have metadata records but need to be processed with their non-verso counterparts
  - Provides detailed feedback showing which files were copied
  - Example output: "✓ Copied 15 verso file(s) to tiff_processed directory"
  - Graceful error handling if copying fails for individual files

### Changed

- **Step 2 Batch Title in CSV** - Automatically adds batch title to cell A2 (2025-12-16 20:03)
  
  - After CSV conversion completes, batch title is appended to cell A2 in brackets
  - Format: "OriginalA2Content [BatchTitle]"
  - Example: "record.title [Lindsay_Test5a]"
  - Provides clear visual identifier of which batch the CSV belongs to
  - Prevents confusion when multiple batch CSV files are open simultaneously
  - Status message shows confirmation: "✓ Appended batch title '[BatchTitle]' to cell A2"
  - Includes error handling if batch title not set or CSV has less than 2 rows
  - Modified gui/dialogs/step2_dialog.py lines 231-269

- **Step 5 Credit Field** - Hardcoded to "Harry S. Truman Library" (2025-12-16 19:48)
  
  - Credit metadata tag now always set to "Harry S. Truman Library"
  - No longer reads Credit value from export.csv file
  - Ensures consistent institutional attribution across all TIFF files
  - Applied to all images processed through Step 5 metadata embedding
  - Modified gui/dialogs/step5_dialog.py line 289

### Fixed

- **Step 5 UTF-8 Mojibake** - Fixed corrupted special characters in TIFF metadata
  - Root cause: pyexiftool library defaulted to cp1252 encoding on Windows
  - Special characters were being corrupted (e.g., "Niños" → "NiÃ±os", "Héroes" → "HÃ©roes")
  - CSV file contained correct UTF-8 text, but encoding mismatch during metadata embedding
  - Solution: Set ExifTool instance to use UTF-8 encoding with `encoding='utf-8'` parameter
  - Now properly handles Spanish and other non-ASCII characters in Headline and Caption-Abstract fields
  - Tested and verified with example: "President Truman Visits Niños Héroes Monument in Mexico"

## HPM [0.0.10] - 2025-12-14 14:20

### Added

- **UTF-8 Encoding Documentation** - Created comprehensive documentation about mojibake
  
  - New document: Encodings_UTF-8_and_Mojibake.md
  - Explains cross-platform encoding issues between Windows and Linux
  - Documents the mojibake problem and how it occurs
  - Includes examples of common mojibake transformations
  - Structured with clear sections and visual examples

- **Change Log Menu Item** - Added to Help menu for easy version history access
  
  - Opens CHANGELOG.md in default markdown viewer/text editor
  - Cross-platform support (Windows, macOS, Linux)
  - Positioned between Quick Start Guide and About
  - Error handling with fallback path display

- **Single Instance Protection** - Prevents multiple app instances from running
  
  - Uses QLockFile to ensure only one instance at a time
  - Shows critical message box if another instance is already running
  - Prevents data corruption from concurrent file access
  - Lock file in system temp directory
  - Automatic cleanup when application closes
    
    ### Fixed

- **CSV Record Viewer Encoding** - Added explicit UTF-8 encoding to prevent mojibake
  
  - Added `encoding='utf-8'` to all file operations in csv_record_viewer.py
  - Fixed JSON config file operations (lines 201, 219)
  - Fixed CSV file loading operation (line 374)
  - Ensures consistent cross-platform handling of special characters (é, ñ, ™, etc.)
  - Prevents mojibake when viewing photo metadata records
  - Eliminates silent encoding switches between Windows (cp1252) and Linux (UTF-8)

- **Step 5 CSV Record Counting** - Fixed to only count records with valid Accession Numbers
  
  - Changed counting logic to filter out rows without ObjectName
  - Uses same artifact_patterns filtering as file analysis
  - Skips empty, whitespace-only, and header artifact values
  - Processing loop also skips invalid records during embedding
  - Prevents false "missing images" counts
  - Now displays "CSV records with Accession Numbers" in progress
  - Adheres to rule: records without Accession Numbers are not records

- **Warning Messages** - Captured Python warnings to system log file
  
  - Redirects warnings to `~/.hstl_photo_framework/logs/warnings.log`
  - Keeps console output clean
  - Preserves warnings for debugging
  - UTF-8 encoding with timestamps
  - Appends to log file (doesn't overwrite)

### Changed

- **g2c Module Location** - Moved g2c.py into Framework directory
  - Copied from ../dev/g2c.py to Framework root
  - Updated PyInstaller spec to reference local g2c.py
  - Simplified step2_dialog.py import logic
  - Removed dependency on external ../dev directory
  - Framework directory now fully self-contained

### Build

- **GUI Executable v0.0.10** - Compiled standalone Windows application
  - PyInstaller 6.17.0 build on Python 3.12.10
  - Executable size: 24 MB (25,151,324 bytes)
  - Includes all dependencies (110 supporting files)
  - Location: `dist/HSTL_Photo_Framework_GUI/`
  - No Python installation required to run
- **Git Tag**: v0.0.10 created and pushed to remote repository

## HPM [0.0.9] - 2025-12-13 11:20

### Added

- **Batch Projects Date Created Column** - Added creation date display
  
  - New column shows when each batch was created
  - Formatted as YYYY-MM-DD HH:MM for easy reading
  - Separate from Last Accessed to show true creation time

- **Current Batch Reports Button** - Added quick access to reports directory
  
  - New Reports button in Current Batch action button bar
  - Opens batch reports directory in file manager
  - Positioned alongside Run All Steps, Run Next Step, and Validate All buttons
  - All four action buttons now centered at bottom of window
  - Shows warning if reports directory doesn't exist yet
  - Provides feedback in output log when directory is opened

### Fixed

- **Batch Projects Last Accessed** - Now properly updates when batch is opened
  - Fixed issue where Last Accessed showed creation date
  - Added call to update_last_accessed() when batch is selected
  - Timestamp now accurately reflects most recent access
  - Batch ID and Data Directory column headers now left-aligned

## HPM [0.0.8] - 2025-12-13 00:25

### Added

- **Batch Projects Date Created Column** - Added creation date display
  
  - New column shows when each batch was created
  - Formatted as YYYY-MM-DD HH:MM for easy reading
  - Separate from Last Accessed to show true creation time

- **Batch Projects Data Directory Column** - Added data directory path display
  
  - New column shows full path to each batch's data directory
  - Positioned as rightmost column in the table
  - Helps identify batch locations at a glance

- **Batch Projects Column Width Persistence** - User column adjustments now saved
  
  - All columns are user-adjustable by dragging column borders
  - Column widths saved automatically using QSettings
  - Preferences restored between sessions
  - Reasonable default widths set for all columns

### Fixed

- **Batch Projects Last Accessed** - Now properly updates when batch is opened
  - Fixed issue where Last Accessed showed creation date
  - Added call to update_last_accessed() when batch is selected
  - Timestamp now accurately reflects most recent access
  - Batch ID and Data Directory column headers now left-aligned

### Changed

- **Step Labels** - Updated step names for improved clarity
  
  - Step 1: "Google Worksheet Preparation" → "Google Worksheet Completed"
  - Step 2: "CSV Conversion" → "Create export.csv file"
  - Step 3: "Unicode Filtering" → "Test for Unicode scrabbling"
  - Step 4: "TIFF Bit Depth Conversion" → "Test/Convert 16 Bit TIFFs"
  - Step 5: "Metadata Embedding" → "Metadata Embedding of TIFF images"
  - Step 8: "Watermark Addition" → "Watermark Restricted JPEGs"

- **Revert Button Functionality** - Enhanced to delete working files when reverting steps
  
  - Step 2: Deletes export.csv file from output/csv directory
  - Step 4: Deletes all files from input/tiff directory with warning about overwritten 16-bit files
  - Step 5: Deletes all files from output/tiff_processed directory
  - Step 6: Deletes all files from output/jpeg directory
  - Step 7: Deletes all files from output/jpeg_resized directory
  - Step 8: Deletes all files from output/jpeg_watermarked directory
  - Custom confirmation dialogs for each step with clear file deletion warnings
  - File count feedback after deletion

- **Step 1 Dialog** - URL field now starts blank instead of pre-filled
  
  - Removed auto-loading of previously saved URL to prevent confusion
  - URL still saved to configuration but won't appear on next dialog open

## HPM [0.0.7] - 2025-12-12 14:55

### Added

- **Edit Menu** - Added Edit menu with "Set Location of Data Files" option
  
  - Allows users to set custom default batch location
  - Validates and creates directories as needed
  - Stores preference in QSettings (Windows Registry/AppData)
  - New batches created in custom location
  - Falls back to C:\Data\HSTL_Batches if not set
  - Existing batches remain in original locations

- **Step 5 Artifact Filtering** - CSV records without accession numbers now excluded
  
  - Filters out artifact records (header names appearing as data)
  - Excludes empty, whitespace-only, and known artifact patterns
  - Affects all Step 5 analysis, reports, and search functionality
  - Note added to comparison report explaining exclusions

### Fixed

- **Step 5 Bit Depth Preservation** - Metadata embedding now preserves original bit depth
  
  - Changed from multiple ExifTool calls to single batched command
  - Added `-overwrite_original_in_place` flag
  - Prevents unwanted conversion from 8-bit to 16-bit
  - Preserves original compression and image format
  - Only updates metadata sections, not image data

- **Review Button Directory Opening** - Replaced subprocess with QDesktopServices
  
  - Changed from subprocess.run(['explorer'...]) to QDesktopServices.openUrl()
  - More reliable and cross-platform compatible
  - Fixed for Steps 2, 4, 5, 6, 7, and 8
  - No longer shows "Command returned non-zero exit status 1" errors

- **Step 8 Watermark Coverage** - Watermark now covers entire image
  
  - Changed from 50% width centered to full image dimensions
  - Watermark resized to match full image width and height
  - Position set to (0, 0) for complete coverage

- **Step 8 Dialog Sizing** - Dialog no longer runs off screen
  
  - Added QScrollArea for content scrolling
  - Buttons placed outside scroll area for accessibility
  - Reduced minimum height from 600px to 500px
  - Reduced output text minimum height from 250px to 200px
  - Default window size reduced to 810x585 (10% smaller)
  - Disabled horizontal scrollbar, enabled vertical scrolling

## HPM [0.0.6] - 2025-12-12 11:30

### Added

- **Step 5 Missing TIFF Search** - Added search functionality for missing TIFF files
  
  - Search button appears when missing files are detected
  - Recursive filesystem search with progress feedback
  - Real-time progress bar and ETA estimation
  - Two-pass directory counting for accurate progress
  - Results display showing found file locations
  - User selects search directory via folder picker

- **Step 5 Comparison Report** - Generate detailed CSV vs TIFF comparison reports
  
  - Generate Comparison Report button in Step 5 dialog
  - Side-by-side listing of CSV records with matching status
  - MATCH/MISS indicators for each record
  - Shows matching TIFF filename next to each CSV record
  - Lists TIFF files without matching CSV records
  - Timestamped reports saved to batch reports directory
  - Report displayed in popup dialog with monospace font
  - Sorted alphabetically by accession number

- **Step 5 Enhanced File Analysis** - Improved file matching display
  
  - Shows count of matched files (CSV records with TIFF files)
  - Shows count of missing files (CSV records without TIFF files)
  - Lists first 10 missing filenames in output
  - Color-coded status labels (green/orange) for visual feedback

### Fixed

- **Review Button Windows Integration** - Fixed explorer command execution
  - Added `shell=True` parameter to `subprocess.run()` calls
  - Review buttons now properly open directories in Windows File Explorer
  - Fixed for Steps 2, 4, 5, 6, 7, and 8
  - Error handling for non-existent directories

### Changed

- **Step 5 Dialog Layout** - Added report button between search and embed buttons
- **Search Progress UI** - Two-phase search with directory counting and ETA display
- **Report Format** - 100-character width for better column alignment

## HPM [0.0.5] - 2025-12-08 15:05

### Added

- **Step 4 Dialog** - TIFF Bit Depth Test & Conversion
  - Detects 16-bit TIFF images using ExifTool metadata (BitsPerSample tag)
  - Handles "EXIF 16" format returned by ExifTool
  - Pre-analysis shows count and complete list of 16-bit TIFFs before conversion
  - Converts 16-bit TIFFs to 8-bit using proper scaling (divide by 256)
  - Overwrites original files in input/tiff directory (unlike Step 5 which copies)
  - Generates timestamped conversion reports
  - Review button opens input/tiff directory in File Explorer
  - Warning dialog before overwriting original files
  - Detailed progress tracking and error handling

### Fixed

- **Step 4 File Locking** - Fixed Windows file locking issue during conversion
  - Explicitly close source image before saving converted version
  - Prevents "file in use" errors when overwriting TIFF files
- **Step 4 Detection Logic** - Improved 16-bit detection
  - Checks for '16' presence AND absence of '8' in metadata value
  - Correctly handles various formats: "16", "16 16 16", "EXIF 16", "IFD0 16"
  - Avoids false positives on 8-bit images with "8" in metadata

## HPM [0.0.4] - 2025-12-08 13:15

### Added

- **Step 6 Dialog** - JPEG Conversion with metadata preservation
  
  - Converts processed TIFFs from output/tiff_processed to output/jpeg
  - Preserves all metadata (EXIF, IPTC, XMP) using ExifTool
  - Adjustable JPEG quality setting (1-100%, default 85%)
  - Real-time progress updates and error tracking
  - Generates timestamped conversion report
  - Review button opens output/jpeg directory

- **Step 7 Dialog** - JPEG Resizing with aspect ratio preservation
  
  - Resizes JPEGs from output/jpeg to output/jpeg_resized
  - Fits images within configurable box (default 800x800 px)
  - Maintains original aspect ratio during resize
  - Uses high-quality Lanczos resampling
  - Smart skipping of images already within size constraints
  - Detailed resize information (original → resized dimensions)
  - Review button opens output/jpeg_resized directory

- **Step 8 Dialog** - Selective watermarking for restricted images
  
  - Reads IPTC:CopyrightNotice field to identify restricted images
  - Only watermarks images containing 'Restricted' in copyright field
  - Copies unrestricted images without watermarks
  - Adjustable watermark opacity slider (10-100%, default 30%)
  - Uses gui/Copyright_Watermark.png as overlay
  - Scales watermark to 50% of image width, centers on image
  - Pre-analysis counts and lists restricted images before processing
  - Review button opens output/jpeg_watermarked directory

### Changed

- **Status Column Color** - Changed active batch background from light green to aqua
- **TagWriter Integration** - Step 5 Review button launches TagWriter in tiff_processed directory

### Fixed

- **Step 6 Import** - Removed unnecessary piexif import (using ExifTool instead)
- **Step 8 Detection** - Fixed ExifTool result handling (returns string not bytes)
- **Copyright Field** - Case-insensitive 'Restricted' detection

## HPM [0.0.3] - 2025-12-08 10:10

### Fixed

- **Step 5 File Handling** - Fixed metadata embedding to preserve source files
  - Source TIFFs now copied from `input/tiff/` to `output/tiff_processed/`
  - Metadata written to copies in output directory, not to source files
  - Progress messages and reports updated to clarify source vs. output locations
  - Added full output directory path display after successful completion

## HPM [0.0.2] - 2025-12-07 19:45

### Added

- **Quick Start Guide Menu** - Added "Quick Start Guide" (F1) to Help menu
  - Opens docs/GUI_QUICKSTART.md in default application
  - Cross-platform support (Windows, macOS, Linux)
  - Error handling with fallback path display

### Changed

- **Step Name Visibility** - Enhanced step labels for better readability
  - Increased font size by 2 points
  - Made step names bold
  - Improved visual hierarchy
- **Step Layout** - Changed step arrangement to vertical columns
  - Column 1: Steps 1-4 (Google Spreadsheet → TIFF Conversion)
  - Column 2: Steps 5-8 (Metadata → Watermark)
  - More natural workflow progression
- **Window Sizing** - Improved window resizing behavior
  - Reduced minimum size from 1200x800 to 800x600
  - Added scroll areas to all tabs for better content handling
  - Window now resizes smoothly without content clipping

### Fixed

- **Batch List Refresh** - Fixed newly created batches not appearing
  - Added explicit registry reload from disk on refresh
- **Status Column Contrast** - Fixed low contrast in batch status column
  - Changed text color to black for better readability
- **Syntax Errors** - Fixed indentation and duplicate method issues
  - Corrected _show_settings method indentation
  - Removed duplicate _show_about method
- **UI Clipping** - Fixed text clipping when window is maximized
  - Added proper size policies to step widgets
  - Set column stretch for grid layout
  - Removed problematic window flags
  - Content now adapts to all window sizes

## HPM [0.0.1] - 2025-12-07 18:45

### Added - GUI Application (Initial Release)

#### Core Application

- **PyQt6 GUI Application** - Complete graphical user interface for HSTL Photo Framework
- **Main Window** - Tab-based interface with menu bar, status bar, and keyboard shortcuts
- **Application Entry Point** - `gui/hstl_gui.py` with proper initialization

#### Batch Management

- **Batch List Widget** - Display all registered batches with sortable columns
- **Visual Progress Indicators** - Progress bars showing completion percentage (0-100%)
- **Status Color Coding** - Visual status indicators (active/completed/archived)
  - Active: Light green background
  - Completed: Light blue background
  - Archived: Light gray background
- **Context Menu Actions** - Right-click menu for batch operations
  - Open Batch
  - Show Info
  - Mark as Complete
  - Archive
  - Reactivate
  - Remove from Registry
- **Show All Toggle** - Checkbox to display archived/completed batches
- **Batch Creation Dialog** - Flexible location options:
  - Default location (`C:\Data\HSTL_Batches`)
  - Custom base directory
  - Full custom path
- **Batch Info Dialog** - Detailed view of batch information and step status

#### Step Execution Interface

- **Visual Step Layout** - 8 processing steps in 2x4 grid
- **Step Status Indicators**:
  - ⭕ Pending - Not yet completed
  - 🔄 Running - Currently processing
  - ✅ Completed - Successfully finished
  - ❌ Failed - Error occurred
- **Individual Step Execution** - Run button for each step
- **Step Revert Capability** - Revert completed steps back to pending
  - Confirmation dialog before reverting
  - Preserves output files
  - Updates configuration automatically
- **Batch Operations**:
  - Run All Steps - Execute all 8 steps in sequence
  - Run Next Step - Automatically run next pending step
  - Validate All - Run validation checks
- **Output/Log Viewer** - Real-time display of step execution output
- **Step Names** - Descriptive labels for all 8 processing steps

#### Configuration Management

- **Configuration Tree View** - Hierarchical display of YAML configuration
- **Automatic Refresh** - Reload configuration from disk
- **Read-Only Display** - View all project settings

#### User Interface Features

- **Menu Bar** with organized commands:
  - File: New Batch (Ctrl+N), Open Config (Ctrl+O), Exit (Ctrl+Q)
  - Batch: Refresh (F5), Complete, Archive, Reactivate
  - Tools: Validate Project (Ctrl+V), Settings
  - Help: About
- **Keyboard Shortcuts** - Quick access to common operations
- **Status Bar** - Current batch indicator and operation status
- **Window State Persistence** - Remembers size, position, and last opened batch
- **Log Viewer Tab** - Dedicated tab for viewing application logs

#### Integration & Architecture

- **Framework Integration** - Uses existing `HSLTFramework` class
- **Registry Support** - Full integration with `BatchRegistry` for multi-batch tracking
- **Configuration Backend** - Leverages `ConfigManager` for YAML operations
- **Path Management** - Uses `PathManager` for directory operations
- **Signal/Slot Architecture** - PyQt6 best practices for event handling

#### Documentation

- **GUI README** - Comprehensive documentation of GUI features
- **Quick Start Guide** - Step-by-step guide for first-time users
- **Installation Instructions** - PyQt6 setup and requirements
- **Troubleshooting Guide** - Common issues and solutions

### Fixed

#### Batch List Refresh Issue

- **Registry Reload** - Fixed batch list not showing newly created batches
  - Added explicit registry reload from disk on refresh
  - Both main window and batch list widget now reload registry data
  - Press F5 or click Refresh to see latest batches

#### UI Contrast Issue

- **Status Column Readability** - Fixed low contrast in status column
  - Changed text color to black for better visibility
  - Improved readability against light green/blue/gray backgrounds

### Technical Details

#### File Structure

```
gui/
├── hstl_gui.py              # Main entry point
├── main_window.py           # Main window class
├── widgets/
│   ├── batch_list_widget.py # Batch list display
│   ├── step_widget.py       # Step execution interface
│   ├── config_widget.py     # Configuration viewer
│   └── log_widget.py        # Log viewer
├── dialogs/
│   ├── new_batch_dialog.py  # New batch creation
│   ├── batch_info_dialog.py # Batch details
│   └── settings_dialog.py   # Application settings
└── README.md                # GUI documentation
```

#### Dependencies

- PyQt6 >= 6.0.0 (added to requirements.txt)
- All existing framework dependencies

#### Known Limitations

- Step execution runs on main UI thread (may show busy cursor)
- Configuration editing is read-only
- Settings dialog is placeholder
- No threading for long-running operations

### Notes

- GUI is fully functional and ready for use
- All CLI functionality accessible through GUI
- Batch registry shared between CLI and GUI
- Configuration files compatible with CLI version
- Output files and directory structure unchanged

---

## Future Versions

### Planned for 0.0.2

- Threading for long-running operations
- Real-time log streaming
- Configuration inline editing
- Step-specific progress indicators
- Settings persistence and customization

### Planned for 0.1.0

- Step implementation completion
- Advanced validation reporting
- Batch comparison tools
- Export/import configurations
- Enhanced error handling and recovery