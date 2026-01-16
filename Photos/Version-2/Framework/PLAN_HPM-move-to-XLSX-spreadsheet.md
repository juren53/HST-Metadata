# HPM Migration Plan: Google Worksheets to Excel Spreadsheets

## Executive Summary

This document outlines the migration strategy for moving the HST Photo Metadata (HPM) system from Google Worksheets to Excel spreadsheets. The migration will replace the Google Sheets API integration with local Excel file processing while preserving all existing data processing workflows.

## Current System Overview

### Current Architecture
- **Data Source**: Google Worksheets accessed via API
- **Key Component**: `g2c.py` - Google Sheets to CSV converter with IPTC mapping
- **Dependencies**: Google Auth, Google Sheets API, gspread
- **Workflow**: 8-step processing pipeline, Steps 1-2 handle data ingestion

### Current Data Flow
1. Step 1: User enters Google Worksheet URL
2. Step 2: `g2c.py` converts Google Sheet to `export.csv` with IPTC mapping
3. Steps 3-8: Process CSV through image processing pipeline

### New Data Flow (Post-Migration)
1. Step 1: User selects Excel spreadsheet, file is copied to `input/spreadsheet/` and validated
2. Step 2: `g2c.py` reads Excel file from `input/spreadsheet/` and converts to `export.csv` with IPTC mapping
3. Steps 3-8: Process CSV through image processing pipeline

## Migration Strategy

### Phase 1: Core Data Access Layer Replacement

#### 1.1 Replace `g2c.py` Google Sheets Integration
**File**: `g2c.py` (lines 28-458)

**Changes Required**:
- **Remove Google API imports** (lines 34-38):
  ```python
  # Remove: from google.auth.transport.requests import Request
  # Remove: from google_auth_oauthlib.flow import InstalledAppFlow
  # Remove: from googleapiclient.discovery import build
  # Remove: from googleapiclient.errors import HttpError
  ```

- **Replace `fetch_sheet_data()` function** (lines 150-300) with Excel reading from standardized location:
  ```python
  def read_excel_file(excel_path):
      """Read Excel file from input/spreadsheet/ and return pandas DataFrame with same structure as Google Sheets"""
      try:
          df = pd.read_excel(excel_path, engine='openpyxl')
          # Apply existing row3_mapping and validation logic
          return process_dataframe(df)
      except Exception as e:
          handle_excel_error(e)
  ```

- **Update default Excel file path** to look in `input/spreadsheet/` directory:
  ```python
  DEFAULT_EXCEL_PATH = "input/spreadsheet/metadata.xlsx"
  ```

- **Update command line interface** (lines 580-650):
  - Change `--sheet-url` parameter to `--excel-file`
  - Update help text and validation
  - Default to reading from `input/spreadsheet/` directory

- **Preserve existing logic**:
  - Row 3 header mapping (lines 464-472)
  - Date formatting functions
  - Data validation and error handling
  - IPTC field mapping

#### 1.2 Create File Management Module
**New File**: `file_manager.py`

**Purpose**: Handle Excel file copying and validation for Step 1

**Key Functions**:
```python
def copy_excel_to_input(source_path, project_data_dir):
    """Copy Excel spreadsheet to input/spreadsheet/ directory"""
    target_dir = os.path.join(project_data_dir, "input", "spreadsheet")
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    base_name = os.path.basename(source_path)
    target_path = os.path.join(target_dir, base_name)
    
    # Handle filename conflicts
    counter = 1
    while os.path.exists(target_path):
        name, ext = os.path.splitext(base_name)
        target_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
        counter += 1
    
    shutil.copy2(source_path, target_path)
    return target_path

def validate_hpm_excel_structure(excel_path):
    """Comprehensive validation of Excel file for HPM project requirements"""
    try:
        # Check file can be read
        df = pd.read_excel(excel_path, nrows=10)  # Read first 10 rows for structure
        
        # Validate Row 3 mapping headers
        required_mapping_headers = ['Title', 'Accession Number', 'Restrictions', 'Scopenote', 
                                   'Related Collection', 'Source Photographer', 'Institutional Creator']
        
        # Get Row 3 (index 2) headers
        if len(df) >= 3:
            row3_headers = df.iloc[2].fillna('').astype(str).tolist()
            missing_headers = [h for h in required_mapping_headers if h not in row3_headers]
            if missing_headers:
                return False, f"Missing required Row 3 headers: {', '.join(missing_headers)}"
        
        return True, "Excel file structure is valid for HPM processing"
        
    except Exception as e:
        return False, f"Excel validation error: {str(e)}"
```

#### 1.2 Create Excel Validation Module
**New File**: `excel_validator.py`

**Purpose**: Validate Excel file structure before processing

**Key Functions**:
```python
def validate_excel_file(excel_path):
    """Validate Excel file meets HPM requirements"""
    # Check file extension (.xlsx, .xls)
    # Verify required worksheets exist
    # Validate data structure matches expected format
    
def check_required_columns(df):
    """Ensure required metadata columns are present"""
    # Use existing required_fields from settings.py
```

### Phase 2: User Interface Updates

#### 2.1 Update Step 1 Dialog
**File**: `gui/dialogs/step1_dialog.py`

**Changes**:
- Replace Google Worksheet URL input with Excel file browser
- Update dialog title: "Step 1: Excel Spreadsheet Preparation"
- Update description text and requirements to include file copying and validation
- Add file validation for Excel formats
- Implement file copying to `input/spreadsheet/` directory
- Add comprehensive HPM project validation

**New UI Elements**:
```python
# Replace QLineEdit with file browser
from PyQt6.QtWidgets import QFileDialog, QLabel, QProgressBar
from file_manager import copy_excel_to_input, validate_hpm_excel_structure

def browse_excel_file(self):
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Select Excel Spreadsheet", "", 
        "Excel Files (*.xlsx *.xls);;All Files (*)"
    )
    if file_path:
        self.excel_path_edit.setText(file_path)
        self.validate_and_copy_excel(file_path)

def validate_and_copy_excel(self, source_path):
    """Validate Excel file and copy to input/spreadsheet/ directory"""
    # Show progress
    self.status_label.setText("Validating Excel file...")
    self.progress_bar.setVisible(True)
    
    # Validate file structure
    is_valid, message = validate_hpm_excel_structure(source_path)
    if not is_valid:
        QMessageBox.critical(self, "Validation Error", 
                           f"The selected Excel file is not valid for HPM processing:\n\n{message}")
        return
    
    # Copy to input directory
    try:
        self.status_label.setText("Copying Excel file to project...")
        target_path = copy_excel_to_input(source_path, self.config_manager.get_data_directory())
        
        # Update display with target location
        self.copied_to_label.setText(f"Copied to: {target_path}")
        self.status_label.setText("Excel file successfully validated and copied!")
        self.progress_bar.setVisible(False)
        
        # Store target path for later use
        self.excel_target_path = target_path
        
    except Exception as e:
        QMessageBox.critical(self, "File Copy Error", 
                           f"Failed to copy Excel file:\n\n{str(e)}")
```

#### 2.2 Update Step 2 Dialog
**File**: `gui/dialogs/step2_dialog.py`

**Changes**:
- Update `CSVConversionThread` to call Excel conversion instead of Google Sheets
- Remove Google authentication dependencies
- Update progress messages from "Converting Google Sheet" to "Processing Excel file"

#### 2.3 Update UI Text References
**Files**: 
- `gui/widgets/step_widget.py`
- Any other files referencing "Google Worksheet"

**Changes**: Update all user-facing text from "Google Worksheet" to "Excel Spreadsheet"

### Phase 3: Configuration and Dependencies

#### 3.1 Update Requirements
**File**: `requirements.txt`

**Remove** (lines 43-52):
```
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
gspread>=5.0.0
```

**Add** (if not already present):
```
openpyxl>=3.0.0    # For .xlsx files
xlrd>=2.0.0        # For legacy .xls files
```

#### 3.2 Update Default Settings
**File**: `config/settings.py`

**Changes**:
- Update step descriptions (line 19): 'Google Spreadsheet Preparation' → 'Excel Spreadsheet Preparation'
- Update step1 validation rules to check for Excel files instead of URLs
- Update step1 required fields description

### Phase 4: Cleanup and Documentation

#### 4.1 Remove Deprecated Components
**Files to Remove/Archive**:
- `client_secret_*.json` - Google OAuth credentials
- `token_sheets.pickle` - Google authentication tokens
- `Google_form/` directory - Google Forms integration (no longer needed)

#### 4.2 Update Documentation
**Files to Update**:
- README.md - Update installation and usage instructions
- User manual - Update screenshots and instructions
- Technical documentation - Update architecture diagrams

## Implementation Details

### Data Mapping Preservation

**Critical**: The existing Row 3 header mapping must be preserved exactly:

```python
# From g2c.py lines 464-472 - DO NOT MODIFY
row3_mapping = {
    'Title': 'Headline',
    'Accession Number': 'ObjectName', 
    'Restrictions': 'CopyrightNotice',
    'Scopenote': 'Caption-Abstract',
    'Related Collection': 'Source',
    'Source Photographer': 'By-line',
    'Institutional Creator': 'By-lineTitle'
}
```

### Excel File Specifications

**Supported Formats**:
- `.xlsx` (Excel 2007+) - Primary format using openpyxl
- `.xls` (Excel 97-2003) - Legacy support using xlrd

**Required Structure**:
- Row 1: Data headers
- Row 2: Blank separator row  
- Row 3: Field mapping headers (critical for IPTC processing)
  - **Required Row 3 Headers**: Title, Accession Number, Restrictions, Scopenote, Related Collection, Source Photographer, Institutional Creator
- Row 4+: Metadata data

**File Management Requirements**:
- Source file is copied to `input/spreadsheet/` directory in project
- Filename conflicts are handled by appending counter (e.g., `metadata_1.xlsx`)
- Original file remains untouched - copy is used for processing

**Validation Requirements**:
- File format validation (.xlsx/.xls only)
- File readability and structure validation
- Row 3 mapping must contain all required HPM field headers
- Data type validation for critical columns
- Date fields must be in expected format for ISO conversion

**Step 1 Validation Workflow**:
1. User selects Excel file via file browser
2. File format validation (extension check)
3. Excel file structure validation (Row 3 headers check)
4. File copying to standardized location (`input/spreadsheet/`)
5. Confirmation of successful copy with target path display

### Directory Structure Changes

**Current Structure:**
```
data_directory/
├── input/
│   ├── tiff/              # Source TIFF files
│   └── spreadsheet/        # Not used (Google Sheets accessed via URL)
├── output/
│   ├── csv/               # export.csv
│   ├── tiff_processed/    # TIFFs with embedded metadata
│   ├── jpeg/             # Converted JPEGs
│   ├── jpeg_resized/     # Resized JPEGs
│   └── jpeg_watermarked/ # Final watermarked JPEGs
├── reports/              # Processing reports
├── logs/                 # Framework logs
└── config/               # project_config.yaml
```

**Updated Structure (Post-Migration):**
```
data_directory/
├── input/
│   ├── tiff/              # Source TIFF files
│   └── spreadsheet/        # Excel spreadsheets (copied from user selection)
├── output/
│   ├── csv/               # export.csv
│   ├── tiff_processed/    # TIFFs with embedded metadata
│   ├── jpeg/             # Converted JPEGs
│   ├── jpeg_resized/     # Resized JPEGs
│   └── jpeg_watermarked/ # Final watermarked JPEGs
├── reports/              # Processing reports
├── logs/                 # Framework logs
└── config/               # project_config.yaml
```

**Key Changes:**
- `input/spreadsheet/` directory becomes active (previously unused)
- Step 1 copies user-selected Excel files to this standardized location
- Step 2 reads from this location for consistent processing
- Original files remain untouched - ensuring data integrity

### Error Handling Strategy

**Excel-Specific Errors**:
- File not found or inaccessible
- Corrupted Excel file format
- Missing required worksheets or columns
- Invalid data types or formats

**Graceful Degradation**:
- Provide specific error messages with suggested solutions
- Maintain existing error reporting structure
- Preserve backup functionality

## Benefits of Migration

### Operational Benefits
1. **Offline Processing** - No internet dependency
2. **Faster Processing** - Direct file access vs API calls
3. **Better Security** - No OAuth tokens or API keys
4. **Simplified Deployment** - No Google API setup required

### Maintenance Benefits
1. **Reduced Dependencies** - Fewer external services
2. **Simpler Codebase** - Remove authentication complexity
3. **Easier Testing** - No mock API calls needed
4. **Lower Overhead** - No API rate limits or quotas

## Risk Assessment and Mitigation

### High Risk Items
1. **Data Format Changes** - Excel files might have different structure
   - **Mitigation**: Implement comprehensive validation before processing

2. **User Workflow Disruption** - Users accustomed to Google Sheets
   - **Mitigation**: Provide migration guide and training materials

### Medium Risk Items
1. **File Compatibility** - Different Excel versions and formats
   - **Mitigation**: Support both .xlsx and .xls formats with fallbacks

2. **Performance Impact** - Large Excel files might be slow to process
   - **Mitigation**: Implement chunked reading for very large files

### Low Risk Items
1. **UI Changes** - User interface modifications
   - **Mitigation**: Maintain similar workflow and button placement

## Testing Strategy

### Unit Tests
- Test Excel file reading with various formats
- Test data validation functions
- Test error handling scenarios

### Integration Tests
- End-to-end workflow with sample Excel files
- Test all 8 processing steps with Excel-derived data
- Test IPTC metadata embedding accuracy

### User Acceptance Testing
- Test with real HST metadata spreadsheets
- Validate user interface and workflow
- Performance testing with large datasets

## Timeline and Resource Allocation

### Estimated Development Time
- **Phase 1**: 4-5 days (Core data access replacement + file management module)
- **Phase 2**: 2-3 days (UI updates with file copying/validation)
- **Phase 3**: 1 day (Dependencies and configuration)
- **Phase 4**: 1-2 days (Cleanup and documentation)
- **Testing**: 2-3 days (Comprehensive testing including file management)

**Total Estimated Time**: 10-14 days (2-3 weeks)

### Resource Requirements
- **Developer**: 1 full-time developer
- **Tester**: 0.5 FTE for testing phase
- **Subject Matter Expert**: Available for validation and user acceptance testing

## Rollout Strategy

### Parallel Deployment (Recommended)
1. **Phase 1**: Deploy Excel support alongside Google Sheets (dual-mode)
2. **Phase 2**: Migrate existing projects to Excel format
3. **Phase 3**: Decommission Google Sheets integration

### Big Bang Deployment (Alternative)
1. Complete migration in single release
2. Convert all existing Google Sheets to Excel format
3. Update all user documentation simultaneously

## Success Criteria

### Technical Success
- [ ] All existing functionality works with Excel files
- [ ] Processing time improves or stays the same
- [ ] No data loss or corruption during migration
- [ ] All automated tests pass

### User Success  
- [ ] Users can successfully process Excel spreadsheets
- [ ] Workflow complexity remains the same or improves
- [ ] Error messages are clear and actionable
- [ ] Performance meets or exceeds current system

## Future Considerations

### Potential Enhancements
1. **Template Generation** - Create Excel templates with proper structure
2. **Data Validation Rules** - Built-in Excel validation for required fields
3. **Batch Processing** - Support multiple Excel files in single batch
4. **Cloud Storage Integration** - Support Excel files from SharePoint, OneDrive, etc.

### Scalability Considerations
- Monitor memory usage with large Excel files
- Consider database integration for very large datasets
- Evaluate performance improvements and optimizations

---

**Document Version**: 1.0  
**Created**: January 16, 2026  
**Author**: HPM Development Team  
**Review Date**: January 30, 2026