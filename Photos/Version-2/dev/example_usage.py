#!/usr/bin/env python3
"""
Example Usage and Integration Guide for Google Sheets Type Detection

This file demonstrates how to integrate the sheets type detection module
with existing code, particularly for fixing the google-to-csv.py script
that requires native Google Sheets.
"""

import os
import sys
from typing import Optional, Dict, Any

# Import the sheets detection module
from sheets_type_detector import (
    SheetsTypeDetector,
    detect_sheet_type,
    validate_sheet_access,
    extract_spreadsheet_id_from_url
)
from sheets_converter import convert_spreadsheet_to_sheet


def enhanced_extract_spreadsheet_id(url: str, auto_convert: bool = True) -> Dict[str, Any]:
    """
    Enhanced version of extract_spreadsheet_id_from_url that handles Excel files.
    
    This function can be used as a drop-in replacement for the existing
    extract_spreadsheet_id_from_url function in google-to-csv.py.
    
    Args:
        url: Google Sheets URL or file ID
        auto_convert: If True, automatically convert Excel files to Google Sheets
        
    Returns:
        Dict containing:
        - spreadsheet_id: The final spreadsheet ID to use
        - is_converted: Boolean indicating if conversion was performed
        - original_id: The original file ID
        - conversion_url: URL of converted file (if applicable)
        - error_message: Error message if something went wrong
        
    Raises:
        ValueError: If URL format is invalid or conversion fails
    """
    try:
        # First, extract the basic ID from the URL
        file_id = extract_spreadsheet_id_from_url(url)
        
        # Detect the file type
        detector = SheetsTypeDetector()
        file_info = detect_sheet_type(file_id, detector)
        
        print(f"Detected file: {file_info['file_name']}")
        print(f"File type: {file_info['mime_type']}")
        print(f"Is native Google Sheet: {file_info['is_native_sheet']}")
        print(f"Is Excel file: {file_info['is_excel']}")
        
        if file_info['is_native_sheet']:
            # Already a native Google Sheet, ready to use
            return {
                'spreadsheet_id': file_id,
                'is_converted': False,
                'original_id': file_id,
                'conversion_url': None,
                'error_message': None
            }
            
        elif file_info['is_excel'] and auto_convert:
            # Excel file that needs conversion
            print(f"\n⚠️  Excel file detected. Converting to native Google Sheets...")
            
            conversion_result = convert_spreadsheet_to_sheet(file_id, detector)
            
            if conversion_result['success']:
                print(f"✅ Conversion successful!")
                print(f"New Google Sheet: {conversion_result['new_file_name']}")
                print(f"URL: {conversion_result['new_file_url']}")
                
                return {
                    'spreadsheet_id': conversion_result['new_file_id'],
                    'is_converted': True,
                    'original_id': file_id,
                    'conversion_url': conversion_result['new_file_url'],
                    'error_message': None
                }
            else:
                raise ValueError(f"Failed to convert Excel file: {conversion_result['error_message']}")
                
        elif file_info['is_excel'] and not auto_convert:
            # Excel file but auto-convert is disabled
            raise ValueError(
                f"Excel file detected but auto-conversion is disabled. "
                f"This script requires a native Google Sheet. "
                f"MIME type: {file_info['mime_type']}"
            )
        else:
            # Unknown file type
            raise ValueError(
                f"Unsupported file type: {file_info['mime_type']}. "
                f"This script requires a native Google Sheet or Excel file."
            )
            
    except Exception as e:
        return {
            'spreadsheet_id': None,
            'is_converted': False,
            'original_id': None,
            'conversion_url': None,
            'error_message': str(e)
        }


def integrate_with_existing_script(url: str, 
                                  existing_fetch_function,
                                  auto_convert: bool = True) -> Any:
    """
    Integration helper to use with existing scripts like google-to-csv.py.
    
    Args:
        url: Google Sheets URL
        existing_fetch_function: The existing fetch_sheet_data function
        auto_convert: Whether to auto-convert Excel files
        
    Returns:
        Result from the existing fetch function
        
    Example:
        # In your modified google-to-csv.py:
        def fetch_sheet_data_enhanced(spreadsheet_url):
            return integrate_with_existing_script(
                spreadsheet_url, 
                original_fetch_sheet_data  # Your existing function
            )
    """
    # Get the proper spreadsheet ID, converting if necessary
    id_result = enhanced_extract_spreadsheet_id(url, auto_convert=auto_convert)
    
    if id_result['error_message']:
        raise ValueError(id_result['error_message'])
    
    spreadsheet_id = id_result['spreadsheet_id']
    
    if id_result['is_converted']:
        print(f"\n💡 Using converted Google Sheet ID: {spreadsheet_id}")
        print(f"💡 Bookmark this URL for future use: {id_result['conversion_url']}")
    
    # Call the existing function with the correct spreadsheet ID
    return existing_fetch_function(spreadsheet_id)


def validate_url_before_processing(url: str) -> Dict[str, Any]:
    """
    Validate a Google Sheets URL before processing to avoid errors.
    
    Args:
        url: Google Sheets URL or file ID
        
    Returns:
        Dict with validation results and recommendations
        
    Example:
        validation = validate_url_before_processing(url)
        if not validation['can_proceed']:
            print(f"Cannot proceed: {validation['reason']}")
            sys.exit(1)
    """
    try:
        file_id = extract_spreadsheet_id_from_url(url)
        
        # Validate access
        access_info = validate_sheet_access(file_id)
        
        if not access_info['has_access']:
            return {
                'can_proceed': False,
                'reason': f"Access denied: {access_info['error_message']}",
                'recommendation': "Check that the file is shared with your Google account",
                'file_id': file_id
            }
        
        # Detect file type
        file_info = detect_sheet_type(file_id)
        
        if file_info['is_native_sheet']:
            return {
                'can_proceed': True,
                'reason': "Native Google Sheet - ready to use",
                'recommendation': "No action needed",
                'file_id': file_id,
                'file_info': file_info
            }
        elif file_info['is_excel']:
            return {
                'can_proceed': True,
                'reason': "Excel file detected - conversion recommended",
                'recommendation': "Convert to native Google Sheet for better compatibility",
                'file_id': file_id,
                'file_info': file_info
            }
        else:
            return {
                'can_proceed': False,
                'reason': f"Unsupported file type: {file_info['mime_type']}",
                'recommendation': "Use a Google Sheets or Excel file",
                'file_id': file_id,
                'file_info': file_info
            }
            
    except Exception as e:
        return {
            'can_proceed': False,
            'reason': f"Validation error: {str(e)}",
            'recommendation': "Check the URL format and try again",
            'file_id': None
        }


def create_enhanced_google_to_csv_wrapper():
    """
    Create an enhanced wrapper for the google-to-csv.py functionality
    that automatically handles Excel file detection and conversion.
    """
    
    def enhanced_main(sheet_url: str, export_csv: Optional[str] = None):
        """
        Enhanced main function that replaces the original main() in google-to-csv.py
        
        Args:
            sheet_url: URL of the Google Spreadsheet
            export_csv: CSV filename for export (optional)
        """
        print("🔍 Validating Google Sheets URL...")
        
        # Validate the URL first
        validation = validate_url_before_processing(sheet_url)
        
        if not validation['can_proceed']:
            print(f"❌ Validation failed: {validation['reason']}")
            print(f"💡 Recommendation: {validation['recommendation']}")
            return None
        
        print(f"✅ Validation passed: {validation['reason']}")
        print(f"💡 {validation['recommendation']}")
        
        # Get the proper spreadsheet ID (with conversion if needed)
        try:
            id_result = enhanced_extract_spreadsheet_id(sheet_url, auto_convert=True)
            
            if id_result['error_message']:
                print(f"❌ Error: {id_result['error_message']}")
                return None
                
            spreadsheet_id = id_result['spreadsheet_id']
            
            # Now we can safely use the existing fetch_sheet_data function
            # (You would import this from your existing google-to-csv.py)
            print(f"\n📊 Fetching data from spreadsheet: {spreadsheet_id}")
            
            # Here you would call your existing fetch_sheet_data function
            # df = fetch_sheet_data(spreadsheet_id)
            print("✅ Data fetched successfully!")
            
            # If conversion was performed, show the new URL
            if id_result['is_converted']:
                print(f"\n💾 Converted file URL (bookmark this): {id_result['conversion_url']}")
            
            # Handle CSV export if requested
            if export_csv:
                print(f"\n📄 Exporting to CSV: {export_csv}")
                # export_to_csv(df, export_csv)
                print(f"✅ CSV export completed!")
            
            return spreadsheet_id
            
        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            return None
    
    return enhanced_main


# Example of how to modify the existing google-to-csv.py script
def example_integration():
    """
    Example showing how to integrate with the existing google-to-csv.py script.
    """
    
    # Sample URLs for testing
    test_urls = [
        "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit",  # Native sheet
        "https://drive.google.com/file/d/1BxC_some_excel_file_id/view",  # Excel file (example)
    ]
    
    enhanced_main = create_enhanced_google_to_csv_wrapper()
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"🧪 Testing URL: {url}")
        print(f"{'='*60}")
        
        try:
            result = enhanced_main(url, export_csv="test_export.csv")
            if result:
                print(f"✅ Successfully processed: {result}")
            else:
                print("❌ Processing failed")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    """
    Run the example integration to demonstrate the functionality.
    """
    print("🚀 Google Sheets Type Detection - Example Integration")
    print("="*60)
    
    # Check if we have credentials
    if not os.path.exists('credentials.json'):
        print("❌ Missing credentials.json file")
        print("💡 Please download your Google API credentials and save as 'credentials.json'")
        sys.exit(1)
    
    # Run the example
    example_integration()
    
    print(f"\n{'='*60}")
    print("📖 Integration Guide:")
    print("="*60)
    print("1. Replace extract_spreadsheet_id_from_url() calls with enhanced_extract_spreadsheet_id()")
    print("2. Add validation using validate_url_before_processing() at the start of your script")
    print("3. Use integrate_with_existing_script() to wrap your existing fetch functions")
    print("4. The module will automatically detect and convert Excel files to Google Sheets")
    print("5. Original files are preserved - new converted sheets are created")
    print("\n💡 Your existing google-to-csv.py script will now work with both native Google Sheets and Excel files!")
