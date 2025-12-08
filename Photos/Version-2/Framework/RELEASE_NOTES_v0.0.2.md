# HSTL Photo Framework GUI - Version 0.0.2 Release Notes

**Release Date:** 2025-12-07 19:45  
**Status:** Bug Fix and Enhancement Release

## Overview

Version 0.0.2 addresses several usability issues found in v0.0.1 and adds quality-of-life improvements including better documentation access, enhanced visual hierarchy, and improved window resizing behavior.

## What's New

### Quick Start Guide Access (F1)
- **Help Menu Integration** - Quick Start Guide now accessible from Help → Quick Start Guide
- **Keyboard Shortcut** - Press F1 to instantly open the guide
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **Smart Error Handling** - Shows file path if default app can't open the file

### Enhanced Visual Design
- **Bolder Step Labels** - Step names now 2 points larger and bold for better visibility
- **Improved Layout** - Steps arranged vertically in columns for natural workflow progression
  - Column 1: Steps 1-4 (Data preparation)
  - Column 2: Steps 5-8 (Image processing)
- **Better Status Contrast** - Black text on colored backgrounds for readability

### Improved Window Behavior
- **Flexible Sizing** - Minimum window size reduced to 800x600 (was 1200x800)
- **Smooth Resizing** - Window can be resized to any size without issues
- **Smart Scrolling** - Scroll bars appear automatically when content doesn't fit
- **No More Clipping** - Text remains readable at all window sizes, including maximized

## Bug Fixes

### Critical Fixes
1. **Batch List Not Refreshing**
   - **Issue**: Newly created batches didn't appear in the list
   - **Fix**: Registry now reloads from disk on every refresh
   - **Impact**: Batch list always shows current state

2. **UI Clipping on Maximize**
   - **Issue**: Text was cut off when window was maximized
   - **Fix**: Proper size policies and scroll areas added
   - **Impact**: Content always visible and readable

### UI/UX Fixes
3. **Low Contrast Status Column**
   - **Issue**: White text on pale green was hard to read
   - **Fix**: Changed to black text
   - **Impact**: Status column clearly readable

4. **Syntax Errors**
   - **Issue**: Application wouldn't start due to indentation errors
   - **Fix**: Corrected method indentation and removed duplicates
   - **Impact**: Application launches successfully

## Technical Changes

### Layout Improvements
- Added `QSizePolicy.Expanding` to step widgets
- Set equal column stretch (1:1) for grid layout
- Wrapped all tab content in `QScrollArea` widgets
- Set `widgetResizable=True` on scroll areas

### Window Management
- Removed explicit window flags that prevented resizing
- Changed from `setMinimumSize()` to `resize()` for default size
- Added scroll support for small window sizes

## Upgrade Notes

### From v0.0.1 to v0.0.2
- **No migration needed** - All configurations and data remain compatible
- **Window size** - Application may open smaller than before (800x600 min vs 1200x800 fixed)
- **Functionality** - All features from v0.0.1 remain unchanged
- **New shortcuts** - F1 now opens Quick Start Guide

## Known Issues

Same as v0.0.1:
- Step execution runs on main UI thread (may show busy cursor)
- Configuration viewing is read-only (no inline editing)
- Settings dialog is placeholder
- No threading for long operations

## What's Next

### Planned for v0.0.3
- Threading for step execution
- Real-time progress indicators
- Enhanced error reporting
- Configuration inline editing

### Planned for v0.1.0
- Complete step implementations
- Advanced validation features
- Batch comparison tools
- Report generation

## Files Changed

- `gui/hstl_gui.py` - Version updates
- `gui/main_window.py` - Window resizing, scroll areas, Quick Start menu
- `gui/widgets/step_widget.py` - Layout changes, visual enhancements
- `gui/widgets/batch_list_widget.py` - Registry reload fix, contrast fix
- `gui/__init__.py` - Version constants
- Documentation files - Version updates

## Installation

Same as v0.0.1:
```bash
pip install -r requirements.txt
python gui/hstl_gui.py
```

## Feedback

If you encounter issues:
1. Check minimum window size (800x600)
2. Verify PyQt6 is installed
3. Review CHANGELOG.md for known issues

---

**Upgrading from v0.0.1?** Simply pull the latest code - no configuration changes needed!
