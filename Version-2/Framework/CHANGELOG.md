# Changelog - HSTL Photo Framework

All notable changes to the HSTL Photo Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-14 18:25

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
- **Step 2 Batch Title in CSV** - Automatically adds batch title to cell A1 (2025-12-16 20:03)
  - After CSV conversion completes, batch title is prepended to cell A1 in brackets
  - Format: "[BatchTitle] OriginalA1Content"
  - Example: "[Lindsay_Test5a] ObjectName"
  - Provides clear visual identifier of which batch the CSV belongs to
  - Prevents confusion when multiple batch CSV files are open simultaneously
  - Status message shows confirmation: "✓ Added batch title '[BatchTitle]' to cell A1"
  - Includes error handling if batch title not set or CSV is empty
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

## [0.0.10] - 2025-12-14 14:20

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
  - Redirects warnings to ~/.hstl_photo_framework/logs/warnings.log
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

## [0.0.9] - 2025-12-13 11:20

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

## [0.0.8] - 2025-12-13 00:25

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

## [0.0.7] - 2025-12-12 14:55

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

## [0.0.6] - 2025-12-12 11:30

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
  - Added shell=True parameter to subprocess.run() calls
  - Review buttons now properly open directories in Windows File Explorer
  - Fixed for Steps 2, 4, 5, 6, 7, and 8
  - Error handling for non-existent directories

### Changed
- **Step 5 Dialog Layout** - Added report button between search and embed buttons
- **Search Progress UI** - Two-phase search with directory counting and ETA display
- **Report Format** - 100-character width for better column alignment

## [0.0.5] - 2025-12-08 15:05

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

## [0.0.4] - 2025-12-08 13:15

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
