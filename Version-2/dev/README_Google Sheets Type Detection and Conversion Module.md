# Google Sheets Type Detection and Conversion Module

A Python module that detects whether a Google Sheets URL points to a native Google Sheet or an Excel file being viewed in Google Sheets, and provides automatic conversion capabilities using the Google Drive API.

## Problem Solved

The existing `google-to-csv.py` script requires native Google Sheets URLs and breaks when given Excel files that are being viewed through Google Sheets. This module solves that problem by:

1. **Detecting file types** - Identifies whether a file is a native Google Sheet or Excel file
2. **Automatic conversion** - Converts Excel files to native Google Sheets when needed
3. **Seamless integration** - Works as a drop-in replacement for existing URL handling
4. **Preserves originals** - Creates new converted files without modifying originals

## Key Features

- **🔍 Type Detection**: Automatically detect file types based on MIME types
- **🔄 Auto-Conversion**: Convert Excel files to native Google Sheets
- **🔐 Access Validation**: Verify permissions before processing
- **📦 Batch Processing**: Convert multiple files at once
- **🖥️ CLI Interface**: Command-line tools for easy usage
- **📚 Easy Integration**: Drop-in replacement for existing scripts

## MIME Types Detected

| File Type | MIME Type | Can Convert |
|-----------|-----------|-------------|
| Native Google Sheet | `application/vnd.google-apps.spreadsheet` | ✅ Ready to use |
| Excel (.xlsx) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | ✅ Yes |
| Excel (.xls) | `application/vnd.ms-excel` | ✅ Yes |

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Google API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API and Google Sheets API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials file and save it as `credentials.json`

### 3. Required Scopes

The module requires these Google API scopes:
- `https://www.googleapis.com/auth/drive` - For file metadata and conversion
- `https://www.googleapis.com/auth/spreadsheets` - For reading sheet content

## Quick Start

### Basic Usage

```python
from sheets_type_detector import detect_sheet_type, convert_spreadsheet_to_sheet

# Detect file type
result = detect_sheet_type('https://docs.google.com/spreadsheets/d/1BxC.../edit')
print(f"Is native sheet: {result['is_native_sheet']}")
print(f"Is Excel file: {result['is_excel']}")

# Convert Excel to Google Sheets if needed
if result['is_excel']:
    conversion = convert_spreadsheet_to_sheet(result['file_id'])
    if conversion['success']:
        print(f"Converted to: {conversion['new_file_url']}")
```

### Integration with Existing Scripts

Replace your existing URL handling:

```python
# Before (breaks with Excel files)
spreadsheet_id = extract_spreadsheet_id_from_url(url)

# After (handles both native sheets and Excel files)
from example_usage import enhanced_extract_spreadsheet_id
result = enhanced_extract_spreadsheet_id(url, auto_convert=True)
spreadsheet_id = result['spreadsheet_id']
```

## Command Line Interface

### Detect File Type

```bash
python cli.py detect "https://docs.google.com/spreadsheets/d/1BxC.../edit"
```

### Convert Excel to Google Sheets

```bash
python cli.py convert "1BxC..." --auto-convert
```

### Validate Access Permissions

```bash
python cli.py validate "1BxC..."
```

### Batch Convert Multiple Files

```bash
# Create a text file with URLs (one per line)
echo "https://drive.google.com/file/d/1BxC.../view" > urls.txt
echo "https://drive.google.com/file/d/2DxE.../view" >> urls.txt

# Convert all files
python cli.py batch-convert urls.txt --folder-id "target_folder_id"
```

### Create Conversion Folder

```bash
python cli.py create-folder "My Converted Sheets"
```

## Module Structure

```
sheets_detector/
├── __init__.py                 # Main package exports
├── sheets_type_detector.py     # Core detection and authentication
├── sheets_converter.py         # Conversion and utility functions
├── cli.py                      # Command-line interface
├── example_usage.py           # Integration examples
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## Core Functions

### Detection Functions

- `detect_sheet_type(url_or_id)` - Detect file type and properties
- `validate_sheet_access(url_or_id)` - Check access permissions
- `extract_spreadsheet_id_from_url(url)` - Extract file ID from URL

### Conversion Functions

- `convert_spreadsheet_to_sheet(url_or_id)` - Convert single file
- `batch_convert_to_sheets(file_list)` - Convert multiple files
- `create_conversion_folder(name)` - Create folder for converted files

### Utility Functions

- `get_sheet_url_from_id(file_id)` - Generate Google Sheets URL
- `quick_detect_and_convert(url, auto_convert)` - One-step detection and conversion

## Integration with google-to-csv.py

To fix your existing `google-to-csv.py` script:

### Method 1: Minimal Changes

Replace the URL extraction function:

```python
# In google-to-csv.py, replace this:
def extract_spreadsheet_id_from_url(url):
    # ... existing code ...

# With this:
from example_usage import enhanced_extract_spreadsheet_id

def extract_spreadsheet_id_from_url(url):
    result = enhanced_extract_spreadsheet_id(url, auto_convert=True)
    if result['error_message']:
        raise ValueError(result['error_message'])
    return result['spreadsheet_id']
```

### Method 2: Enhanced Integration

Use the wrapper function:

```python
from example_usage import integrate_with_existing_script

# Wrap your existing fetch function
def fetch_sheet_data_enhanced(spreadsheet_url):
    return integrate_with_existing_script(
        spreadsheet_url, 
        fetch_sheet_data  # Your original function
    )
```

## Error Handling

The module provides comprehensive error handling:

```python
try:
    result = detect_sheet_type(url)
except ValueError as e:
    print(f"Invalid URL: {e}")
except PermissionError as e:
    print(f"Access denied: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Configuration

### Custom Credentials Location

```python
detector = SheetsTypeDetector(
    client_secret_file='path/to/credentials.json',
    token_file='path/to/token.pickle'
)
```

### Conversion Options

```python
result = convert_spreadsheet_to_sheet(
    url_or_id='1BxC...',
    new_name='Custom Sheet Name',
    parent_folder_id='target_folder_id'
)
```

## Batch Processing

```python
urls = [
    'https://drive.google.com/file/d/1BxC.../view',
    'https://drive.google.com/file/d/2DxE.../view',
]

result = batch_convert_to_sheets(
    urls,
    parent_folder_id='folder_id',
    delay_seconds=1.0  # Rate limiting
)

print(f"Converted {result['successful_conversions']} files")
```

## Output Examples

### Detection Output

```
📊 Sheet Detection Results
==================================================
File ID: 1BxC0123456789
File Name: My Excel File.xlsx
MIME Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Is Native Google Sheet: ❌ No
Is Excel File: ✅ Yes
Can Convert: ✅ Yes

💡 This Excel file can be converted to a native Google Sheet for better compatibility.
```

### Conversion Output

```
🔄 Conversion Results
==================================================
✅ Conversion Successful!
New File ID: 2DxE0123456789
New File Name: My Excel File - Google Sheets
New File URL: https://docs.google.com/spreadsheets/d/2DxE0123456789/edit
Original File ID: 1BxC0123456789
```

## Troubleshooting

### Common Issues

1. **"Client secret file not found"**
   - Download credentials from Google Cloud Console
   - Save as `credentials.json` in the working directory

2. **"Access denied"**
   - Ensure the file is shared with your Google account
   - Check that you have appropriate permissions

3. **"File not found"**
   - Verify the URL format is correct
   - Check that the file exists and is accessible

4. **Rate limiting errors**
   - Use the `delay_seconds` parameter in batch operations
   - Reduce the number of concurrent requests

### Debug Mode

Enable verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This module is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!

## Related

- Original script: [`google-to-csv.py`](https://github.com/juren53/HST-Metadata/blob/master/Photos/Version-2/Code/google-to-csv.py)
- Google Sheets API: [Documentation](https://developers.google.com/sheets/api)
- Google Drive API: [Documentation](https://developers.google.com/drive/api)
