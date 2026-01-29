# HPM 'Browse Files' Menu Implementation Plan

## Overview
Add a 'Browse Files' option to the Tools pull-down menu that opens a file browser to the Data Directory for the current batch as shown in the Batch Projects dialog. This feature should take the user to the top of the batch's directory tree.

## Target Directory Structure
```
{BatchName}/
├── input/
│   ├── tiff/              ← Selected TIFF images placed here
│   └── spreadsheet/       ← Selected Excel file placed here
├── output/
│   ├── csv/               → Exported CSV (Step 2)
│   ├── tiff_processed/    → Processed TIFFs (Step 4)
│   ├── jpeg/              → JPEG conversions (Step 6)
│   ├── jpeg_resized/      → Resized JPEGs (Step 7)
│   └── jpeg_watermarked/  → Watermarked JPEGs (Step 8)
├── reports/               → Validation and processing reports
├── logs/                  → Processing logs
└── config/
    └── project_config.yaml → Project configuration
```

## Requirements Analysis
- **Similar to Review feature**: Works similar to the 'Review' feature for Steps 4-8 in the Current Batch dialog
- **Root level access**: Takes user to root of tree where Review takes user to branches
- **Simple directory browser**: Use the same pattern as Review feature
- **Root directory**: Browser opens at the root of the batch's data directory tree
- **Show all files**: Display all files in each branch of the tree

## Implementation Plan

### Files to Modify
**Only one file needs modification:**
- `gui/main_window.py` - Add menu item and handler method

### Code Changes Required

#### 1. Add Menu Item (line 281)
Add this code after the existing Tools menu items:

```python
browse_files_action = QAction('&Browse Files...', self)
browse_files_action.setShortcut('Ctrl+B')
browse_files_action.triggered.connect(self._browse_files)
tools_menu.addAction(browse_files_action)
```

#### 2. Add Handler Method
Add this new method anywhere in the MainWindow class (recommended near other menu handlers):

```python
def _browse_files(self):
    '''Open file browser for current batch data directory.'''
    if not self.current_batch_id:
        QMessageBox.information(self, 'No Batch', 'Please select a batch first')
        return
    
    # Get current batch info
    batch_info = self.registry.get_batch(self.current_batch_id)
    data_directory = batch_info.get('data_directory', '')
    
    if not data_directory:
        QMessageBox.warning(
            self,
            'No Data Directory',
            'Data directory is not configured for this batch.',
        )
        return

    # Convert to Path object
    target_dir = Path(data_directory)
    
    # Check if directory exists
    if not target_dir.exists():
        QMessageBox.warning(
            self,
            'Directory Not Found',
            f'Data directory not found:\n\n{target_dir}\n\n'
            'Please check if the directory exists.',
        )
        return

    # Open directory in File Explorer using QDesktopServices
    try:
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        
        url = QUrl.fromLocalFile(str(target_dir))
        if QDesktopServices.openUrl(url):
            self.status_bar.showMessage(f'Opened data directory: {target_dir.name}', 3000)
        else:
            QMessageBox.warning(
                self, 'Failed to Open', f'Could not open directory:\n\n{target_dir}'
            )
    except Exception as e:
        QMessageBox.critical(
            self, 'Error', f'Failed to open directory:\n\n{str(e)}'
        )
```

## Technical Details

### Pattern Consistency
- **Same as Review feature**: Uses exact same pattern as Review feature in `step_widget.py`
- **Error handling**: Follows existing error handling and user feedback patterns
- **Local imports**: Uses local imports for `QDesktopServices` and `QUrl` (consistent with existing code)

### User Experience Features
- **Keyboard Shortcut**: `Ctrl+B` (consistent with other menu shortcuts)
- **Status Bar Feedback**: Shows success message for 3 seconds
- **Error Handling**: Clear, descriptive error messages
- **Validation**: Checks for selected batch and directory existence

### Integration Points
- **Existing code used**:
  - `self.current_batch_id` - Current selected batch
  - `self.registry.get_batch()` - Batch information retrieval
  - `QMessageBox` patterns - Error and info messages
  - `QDesktopServices.openUrl()` - System file browser integration
  - `self.status_bar.showMessage()` - User feedback

- **No new dependencies**:
  - Uses only existing imports and patterns
  - No additional dialogs or components needed
  - Leverages system file explorer (Windows Explorer, macOS Finder, etc.)

## Testing Scenarios

### Success Cases
1. **Normal operation**: Batch selected with valid data directory → Opens file explorer
2. **Keyboard shortcut**: `Ctrl+B` → Same as menu click

### Error Cases
1. **No batch selected**: Shows info message 'Please select a batch first'
2. **No data directory**: Batch selected but no data directory configured → Shows warning
3. **Missing directory**: Data directory path doesn't exist → Shows warning
4. **System failure**: System fails to open directory → Shows warning or error

## Code Placement Recommendation
Place the new method near other menu handlers, such as after the `_validate_project()` method or before the `_show_settings()` method, to maintain logical grouping of related functionality.

## Dependencies Analysis
### Current Imports Available
- `QMessageBox` - Already imported
- `Path` - Already imported  
- `self.current_batch_id` - Property exists
- `self.registry` - Property exists
- `QDesktopServices` and `QUrl` - Available as local imports (existing pattern)

### No New Requirements
- No additional package dependencies
- No new dialog components
- No configuration changes
- No database schema changes

## Implementation Validation
This plan is based on:
1. **Codebase analysis**: Examined existing Review feature implementation
2. **Pattern matching**: Uses established patterns from step_widget.py
3. **Import analysis**: Confirmed all required imports are available
4. **Error handling**: Follows existing error message patterns
5. **User experience**: Maintains consistency with existing menu behavior

## Estimated Implementation Time
- **Coding time**: 15-30 minutes
- **Testing time**: 10-15 minutes  
- **Total time**: 25-45 minutes

## Risk Assessment
- **Low risk**: Minimal code changes, follows established patterns
- **No breaking changes**: Only additive functionality
- **Rollback safe**: Easy to revert if issues arise
- **No dependencies**: No external dependencies or system changes

## Post-Implementation Verification
1. Verify menu item appears in Tools menu
2. Test keyboard shortcut `Ctrl+B`
3. Test with various batch states
4. Verify error handling for missing directories
5. Test on different operating systems (Windows, macOS, Linux)
6. Ensure status bar messages display correctly

---
**Document Created**: 2026-01-26  
**Author**: OpenCode AI Assistant  
**Status**: Ready for Implementation
