"""
Google Sheets Type Detection and Conversion Package

This package provides tools to detect whether a Google Sheets URL points to a native
Google Sheet or an Excel file being viewed in Google Sheets, and convert Excel files
to native Google Sheets when needed.

Main Components:
- SheetsTypeDetector: Core class for authentication and API access
- detect_sheet_type(): Detect the type of a Google Sheets file
- validate_sheet_access(): Validate access permissions to a file
- convert_spreadsheet_to_sheet(): Convert Excel files to native Google Sheets
- extract_spreadsheet_id_from_url(): Extract file IDs from URLs

Example Usage:
    from sheets_detector import detect_sheet_type, convert_spreadsheet_to_sheet
    
    # Detect file type
    result = detect_sheet_type('https://docs.google.com/spreadsheets/d/1BxC.../edit')
    print(f"Is native sheet: {result['is_native_sheet']}")
    
    # Convert Excel to Google Sheets if needed
    if result['is_excel']:
        conversion = convert_spreadsheet_to_sheet(result['file_id'])
        if conversion['success']:
            print(f"Converted to: {conversion['new_file_url']}")
"""

from .sheets_type_detector import (
    SheetsTypeDetector,
    detect_sheet_type,
    validate_sheet_access,
    extract_spreadsheet_id_from_url
)

from .sheets_converter import (
    convert_spreadsheet_to_sheet,
    batch_convert_to_sheets,
    get_sheet_url_from_id,
    create_conversion_folder,
    list_files_in_folder
)

__version__ = "1.0.0"
__author__ = "Assistant"
__email__ = ""
__description__ = "Google Sheets Type Detection and Conversion Tools"

# Main exports for easy importing
__all__ = [
    # Core detector class
    'SheetsTypeDetector',
    
    # Detection functions
    'detect_sheet_type',
    'validate_sheet_access',
    'extract_spreadsheet_id_from_url',
    
    # Conversion functions
    'convert_spreadsheet_to_sheet',
    'batch_convert_to_sheets',
    
    # Utility functions
    'get_sheet_url_from_id',
    'create_conversion_folder',
    'list_files_in_folder',
]


def quick_detect_and_convert(url_or_id: str, auto_convert: bool = False) -> dict:
    """
    Quick utility function to detect sheet type and optionally convert.
    
    Args:
        url_or_id: Google Sheets URL or file ID
        auto_convert: If True, automatically convert Excel files to Google Sheets
        
    Returns:
        Dict with detection results and conversion results (if applicable)
        
    Example:
        >>> result = quick_detect_and_convert('1BxC...', auto_convert=True)
        >>> if result['conversion_needed'] and result['conversion_success']:
        ...     print(f"Use this URL: {result['final_url']}")
    """
    # Detect the sheet type
    detection_result = detect_sheet_type(url_or_id)
    
    response = {
        'detection_result': detection_result,
        'conversion_needed': False,
        'conversion_attempted': False,
        'conversion_success': False,
        'conversion_result': None,
        'final_url': None,
        'recommendation': None
    }
    
    if detection_result['is_native_sheet']:
        # Already a native sheet, no conversion needed
        response['final_url'] = get_sheet_url_from_id(detection_result['file_id'])
        response['recommendation'] = "File is already a native Google Sheet. No conversion needed."
        
    elif detection_result['is_excel']:
        # Excel file that can be converted
        response['conversion_needed'] = True
        response['recommendation'] = "Excel file detected. Consider converting to native Google Sheets for better compatibility."
        
        if auto_convert:
            response['conversion_attempted'] = True
            conversion_result = convert_spreadsheet_to_sheet(url_or_id)
            response['conversion_result'] = conversion_result
            
            if conversion_result['success']:
                response['conversion_success'] = True
                response['final_url'] = conversion_result['new_file_url']
                response['recommendation'] = f"Successfully converted to native Google Sheet: {conversion_result['new_file_name']}"
            else:
                response['final_url'] = get_sheet_url_from_id(detection_result['file_id'])
                response['recommendation'] = f"Conversion failed: {conversion_result['error_message']}. Using original file."
        else:
            response['final_url'] = get_sheet_url_from_id(detection_result['file_id'])
            
    else:
        # Unknown file type
        response['final_url'] = get_sheet_url_from_id(detection_result['file_id'])
        response['recommendation'] = f"Unknown file type: {detection_result['mime_type']}. May not be compatible with Sheets operations."
    
    return response
