# HSTL Photo Framework GUI - Version 0.1.3 Release Notes

**Release Date:** 2025-12-18 16:15  
**Status:** Feature Enhancement Release

## Overview

Version 0.1.3 adds valuable data insights to the Batch Projects dialog with new Records and Size columns, providing users with immediate visibility into batch data volume and storage requirements. The release also includes performance optimizations and enhanced file utility functions for robust batch management.

## What's New

### Batch Projects Records Column
- **CSV Record Counting** - New column displays count of Accession Numbers/ObjectNames from export.csv
- **Smart Field Detection** - Counts records by checking Accession Number, ObjectName, and AccessionNumber fields
- **Intelligent Display** - Shows integer count for valid data, "N/A" when export.csv doesn't exist
- **Optimal Positioning** - Placed immediately after Batch ID for logical information grouping
- **Visual Consistency** - Center-aligned with proper formatting for professional appearance

### Batch Projects Size Column
- **Directory Size Analysis** - New column shows total disk space used by each batch directory
- **Comprehensive Calculation** - Recursive scanning includes all files and subdirectories
- **Human-Readable Format** - Automatic unit scaling (B, KB, MB, GB, TB) for easy comprehension
- **Error Handling** - Shows "N/A" for inaccessible directories with graceful fallback
- **Visual Harmony** - Positioned after Records column to complete batch metrics grouping

### Performance Optimizations
- **Smart Caching System** - 30-second cache for expensive CSV and directory operations
- **Responsive Interface** - Prevents recalculation during rapid user interactions
- **Automatic Cache Management** - Cache cleared on refresh (F5 or Refresh button)
- **Fresh Data Guarantee** - Ensures current information while maintaining performance

### Enhanced File Utilities
- **`FileUtils.count_csv_records()`** - Robust CSV record counting with field validation
- **`FileUtils.get_directory_size()`** - Efficient recursive directory size calculation
- **`FileUtils.format_file_size()`** - Intelligent human-readable size formatting
- **Cross-Platform Compatibility** - Proper encoding support and error handling
- **Robust Error Recovery** - Graceful handling of missing files and permission issues

## Technical Improvements

### Batch List Widget Enhancements
- **Expanded Table Structure** - Updated from 8 to 10 columns with proper spacing
- **Efficient Data Loading** - Cached batch information for improved responsiveness
- **User Experience** - Center-aligned columns with consistent formatting
- **Error Resilience** - Comprehensive error handling for edge cases

### File System Operations
- **UTF-8 Encoding Support** - Proper text encoding handling across platforms
- **Permission Error Handling** - Graceful handling of inaccessible files/directories
- **Memory Efficiency** - Optimized directory traversal for large batches
- **Validation Logic** - Smart filtering of invalid CSV records

### Performance Architecture
- **30-Second Cache Timeout** - Balanced performance vs. data freshness
- **Cache Invalidation** - Automatic clearing on user refresh actions
- **Background Processing Ready** - Foundation for future threading improvements
- **Resource Management** - Efficient memory usage for large datasets

## Upgrade Notes

### From v0.1.2 to v0.1.3
- **No Migration Required** - All existing configurations remain compatible
- **Enhanced UI** - New columns provide additional insights without breaking existing workflow
- **Performance Gains** - Faster batch list loading and responsiveness
- **Backward Compatibility** - All existing features and functionality preserved

### New Dependencies
- **No New Requirements** - Uses existing framework dependencies
- **Enhanced Utils** - Improved file utility functions available for future development

## Known Issues

Same as v0.1.2:
- Step execution runs on main UI thread (may show busy cursor during processing)
- Configuration viewing is read-only (no inline editing)
- Settings dialog is placeholder with limited functionality
- No threading for long-running operations (foundation ready for future enhancement)

## What's Next

### Planned for v0.1.4
- Threading for long-running operations (batch analysis, directory scanning)
- Real-time progress indicators for Records and Size calculations
- Enhanced error reporting with detailed diagnostic information
- Configuration inline editing capabilities

### Planned for v0.2.0
- Advanced batch comparison and analysis tools
- Enhanced reporting with data visualization
- Batch archiving and compression features
- Integration with external storage solutions

## Files Changed

### Core Framework
- `utils/file_utils.py` - Added CSV counting, directory size, and formatting utilities
- `__init__.py` - Version bump to 0.1.3

### GUI Components
- `gui/widgets/batch_list_widget.py` - Records and Size columns, caching system
- `gui/widgets/step_widget.py` - Version label update
- `gui/main_window.py` - About dialog version update
- `gui/hstl_gui.py` - Module documentation and version constants
- `gui/__init__.py` - Version and commit date updates

### Documentation
- `CHANGELOG.md` - Added v0.1.3 section with comprehensive change details
- `docs/GUI_QUICKSTART.md` - Version information update
- `gui/README.md` - Version header update
- `docs/RELEASE_NOTES_v0.1.3.md` - This release notes document

### Configuration
- `WARP.ini` - Updated version tracking and timestamp

## Installation

Same as v0.1.2:
```bash
pip install -r requirements.txt
python gui/hstl_gui.py
```

## Feedback

### New Feature Questions
If you have questions about the new Records and Size columns:
1. Check that export.csv exists in `output/csv/` directory for record counting
2. Verify batch directory permissions for size calculation
3. Use Refresh button (F5) to update cached information

### Performance Optimization Tips
1. Large directories may take time to calculate initial size
2. Subsequent refreshes use cached data for faster response
3. Cache automatically refreshes after 30 seconds or manual refresh

### Reporting Issues
1. Check this document for known behaviors
2. Review CHANGELOG.md for recent changes
3. Provide batch size and file count details when reporting performance issues

---

**Upgrading from v0.1.2?** Simply pull the latest code and restart the application - no configuration changes needed!

## Impact Summary

### User Experience Improvements
- **Enhanced Visibility** - Immediate insight into batch data volume and storage usage
- **Better Decision Making** - Informed choices about batch management and resource allocation
- **Professional Interface** - Consistent, well-formatted data presentation
- **Responsive Performance** - Faster loading and smoother interactions

### Developer Benefits
- **Reusable Utilities** - New file utility functions available for framework development
- **Performance Patterns** - Caching architecture for future enhancements
- **Error Handling** - Robust patterns for file system operations
- **Documentation Standards** - Comprehensive change tracking and release notes

This release enhances the Batch Projects dialog with practical insights while maintaining the framework's stability and backward compatibility.