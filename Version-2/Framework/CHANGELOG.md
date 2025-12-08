# Changelog - HSTL Photo Framework

All notable changes to the HSTL Photo Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2025-12-08 10:10

### Fixed
- **Step 5 File Handling** - Fixed metadata embedding to preserve source files
  - Source TIFFs now copied from `input/tiff/` to `output/tiff_processed/`
  - Metadata written to copies in output directory, not to source files
  - Progress messages and reports updated to clarify source vs. output locations
  - Added full output directory path display after successful completion

## [0.0.2] - 2025-12-07 19:45

### Added
- **Quick Start Guide Menu** - Added "Quick Start Guide" (F1) to Help menu
  - Opens GUI_QUICKSTART.md in default application
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

## [0.0.1] - 2025-12-07 18:45

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
