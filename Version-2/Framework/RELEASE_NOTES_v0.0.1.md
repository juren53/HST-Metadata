# HSTL Photo Framework GUI - Version 0.0.1 Release Notes

**Release Date:** 2025-12-07 18:45  
**Status:** Initial GUI Release

## Overview

Version 0.0.1 marks the initial release of the PyQt6-based GUI for the HSTL Photo Framework. This release provides a complete graphical user interface for all batch management and workflow execution functionality previously only available through the command-line interface.

## What's New

### GUI Application
This is the first release of the graphical user interface, providing:
- Complete visual interface for all framework operations
- Multi-batch management with progress tracking
- Step-by-step workflow execution
- Configuration viewing and management
- Real-time operation feedback

### Key Features

#### 1. Batch Management
- **Visual Batch List** - See all your batches at a glance with progress bars
- **Easy Batch Creation** - Dialog-based batch setup with flexible location options
- **Status Tracking** - Color-coded status indicators (active/completed/archived)
- **Lifecycle Management** - Complete, archive, or reactivate batches with a click

#### 2. Workflow Execution
- **8-Step Visual Interface** - All processing steps displayed in intuitive grid layout
- **Individual Step Control** - Run any step independently
- **Batch Operations** - Run all steps or just the next pending step
- **Step Revert** - Mark completed steps as pending to re-run them
- **Real-time Feedback** - Output log shows progress and results

#### 3. User Experience
- **Tab-Based Interface** - Easy navigation between batches, execution, config, and logs
- **Keyboard Shortcuts** - Quick access with Ctrl+N, F5, Ctrl+V, etc.
- **Window Persistence** - Remembers your window size and last opened batch
- **Context Menus** - Right-click for quick batch actions

## Bug Fixes

### Batch List Refresh (Issue #1)
**Problem:** Newly created batches didn't appear in the batch list  
**Solution:** Added explicit registry reload from disk on refresh  
**Impact:** Batch list now updates correctly after creating new batches

### Status Column Contrast (Issue #2)
**Problem:** White text on pale green background was difficult to read  
**Solution:** Changed status text color to black  
**Impact:** Status column is now clearly readable

## Installation

### Requirements
- Python 3.8+
- PyQt6 >= 6.0.0
- All existing HSTL Framework dependencies

### Install
```bash
pip install -r requirements.txt
```

### Launch
```bash
python gui/hstl_gui.py
```

## Compatibility

- **Fully compatible** with existing CLI version
- **Shared registry** - Both CLI and GUI access the same batch registry
- **Configuration files** - All YAML configs work in both CLI and GUI
- **Directory structure** - No changes to file organization

## Known Limitations

1. **Main Thread Execution** - Step processing runs on UI thread (may show busy cursor)
2. **Read-Only Config** - Configuration viewing only; no inline editing yet
3. **No Threading** - Long operations may temporarily freeze the UI
4. **Basic Settings** - Settings dialog is placeholder for future enhancements

## Migration from CLI

If you're currently using the CLI version:

1. **No migration needed** - GUI uses the same configuration and registry
2. **Existing batches appear automatically** - All registered batches show in GUI
3. **Pick up where you left off** - Step progress preserved across CLI/GUI
4. **Use both** - CLI and GUI can be used interchangeably

## Usage Tips

### Getting Started
1. Launch the GUI: `python gui/hstl_gui.py`
2. Create a new batch: **File → New Batch** or press **Ctrl+N**
3. Double-click the batch to open it
4. Run steps individually or use **Run All Steps**

### Managing Multiple Batches
- Use the **Show All** checkbox to see archived batches
- Press **F5** to refresh the batch list
- Right-click any batch for quick actions

### Step Execution
- Click **Run** on any step to execute it
- Use **Run Next Step** for sequential workflow
- Click **Revert** to mark completed steps as pending
- Watch the Output panel for real-time feedback

## What's Next

### Planned for v0.0.2
- Threading for better UI responsiveness
- Real-time log streaming
- Configuration inline editing
- Enhanced progress indicators

### Planned for v0.1.0
- Complete step implementations
- Advanced validation reporting
- Batch comparison tools
- Configuration import/export

## Documentation

- **Quick Start Guide**: `GUI_QUICKSTART.md`
- **Full Documentation**: `gui/README.md`
- **Changelog**: `CHANGELOG.md`

## Feedback

This is an early release. If you encounter issues or have suggestions:
1. Check the troubleshooting section in `GUI_QUICKSTART.md`
2. Review known limitations above
3. Document steps to reproduce any issues

## Credits

Developed as part of the HSTL Photo Metadata Project  
GUI Framework: PyQt6  
Backend: HSTL Photo Framework (CLI)

---

**Thank you for using HSTL Photo Framework GUI v0.0.1!**
