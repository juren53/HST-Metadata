#!/usr/bin/env python3
"""
Enhanced Google Sheets to Pandas DataFrame Script

This script accesses a specified Google Sheet and loads its data into a pandas DataFrame.
It can also export the data to a CSV file with mapped column names.

NEW FEATURES:
- Automatically detects Excel files and converts them to Google Sheets
- Enhanced error handling with specific solutions
- Support for both native Google Sheets and Excel files

Usage:
    python google-to-csv-enhanced.py [--sheet-url URL] [--export-csv [FILENAME]] [--auto-convert]

Options:
    --sheet-url, -u            URL of the Google Spreadsheet or Excel file
    --export-csv, -e [FILENAME] Export data to CSV file (default: export.csv)
    --auto-convert, -a         Automatically convert Excel files to Google Sheets
"""

import os
import sys
import pickle
import re
import argparse
import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# === CONFIG ===
CLIENT_SECRET_FILE = 'client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token_sheets.pickle'

# Enhanced scopes to support both Sheets and Drive operations
ENHANCED_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',      # Read/write Google Sheets
    'https://www.googleapis.com/auth/drive',             # Access Google Drive files
    'https://www.googleapis.com/auth/drive.file'         # Manage created files
]

# Fallback scopes for read-only access
READONLY_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# === TARGET SPREADSHEET ===
# Default spreadsheet ID to use if none provided via command line
DEFAULT_SPREADSHEET_ID = '19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4'

def get_credentials(enhanced_mode=True):
    """
    Get or create authentication credentials.
    
    Args:
        enhanced_mode: If True, try to get enhanced scopes for conversion
        
    Returns:
        Valid credentials object
    """
    creds = None
    
    # Try enhanced token first if available
    enhanced_token = 'token_drive_sheets.pickle'
    if enhanced_mode and os.path.exists(enhanced_token):
        try:
            with open(enhanced_token, 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.valid:
                return creds
        except Exception:
            pass
    
    # Fall back to regular token
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            # Choose scopes based on mode
            scopes = ENHANCED_SCOPES if enhanced_mode else READONLY_SCOPES
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes)
                creds = flow.run_local_server(port=0)
                
                # Save token with appropriate name
                token_file = enhanced_token if enhanced_mode else TOKEN_PICKLE_FILE
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                    
            except Exception as e:
                if enhanced_mode:
                    # Fall back to read-only mode
                    print("Enhanced authentication failed, falling back to read-only mode...")
                    return get_credentials(enhanced_mode=False)
                else:
                    raise e
    
    return creds

def extract_spreadsheet_id_from_url(url):
    """
    Extract the spreadsheet ID from a Google Sheets or Drive URL.
    
    Args:
        url: URL of the Google Spreadsheet or Drive file
        
    Returns:
        str: Spreadsheet/file ID extracted from the URL
    
    Raises:
        ValueError: If the URL does not appear to be a valid format
    """
    # Handle direct spreadsheet ID input (not a URL)
    if not url.startswith('http'):
        return url.strip()
    
    # Extended patterns to handle both Sheets and Drive URLs
    patterns = [
        r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'file/d/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
    raise ValueError(
        "Invalid Google Sheets/Drive URL. Expected formats:\n"
        "- https://docs.google.com/spreadsheets/d/ID/...\n"
        "- https://drive.google.com/file/d/ID/...\n"
        "- Or just the ID itself"
    )

def detect_and_convert_if_needed(url_or_id, auto_convert=False):
    """
    Detect file type and convert Excel to Google Sheets if needed.
    
    Args:
        url_or_id: Google Sheets URL or file ID
        auto_convert: If True, automatically convert Excel files
        
    Returns:
        tuple: (final_spreadsheet_id, was_converted, conversion_info)
    """
    try:
        # Import our detection modules
        from sheets_type_detector import SheetsTypeDetector, detect_sheet_type
        from sheets_converter import convert_spreadsheet_to_sheet
        
        file_id = extract_spreadsheet_id_from_url(url_or_id)
        
        # Get enhanced credentials for detection
        creds = get_credentials(enhanced_mode=True)
        
        # Initialize detector
        detector = SheetsTypeDetector(
            client_secret_file=CLIENT_SECRET_FILE,
            token_file='token_drive_sheets.pickle'
        )
        
        # Try to detect file type
        print("🔍 Detecting file type...")
        try:
            file_info = detect_sheet_type(file_id, detector)
            
            print(f"📄 File: {file_info['file_name']}")
            print(f"🏷️  Type: {file_info['mime_type']}")
            
            if file_info['is_native_sheet']:
                print("✅ Native Google Sheet detected - ready to use!")
                return file_id, False, None
                
            elif file_info['is_excel']:
                print("📊 Excel file detected!")
                
                if auto_convert:
                    print("🔄 Converting Excel file to Google Sheets...")
                    
                    conversion_result = convert_spreadsheet_to_sheet(file_id, detector)
                    
                    if conversion_result['success']:
                        print(f"✅ Conversion successful!")
                        print(f"📊 New Google Sheet: {conversion_result['new_file_name']}")
                        print(f"🔗 New URL: {conversion_result['new_file_url']}")
                        
                        return conversion_result['new_file_id'], True, conversion_result
                    else:
                        print(f"❌ Conversion failed: {conversion_result['error_message']}")
                        raise Exception(f"Excel conversion failed: {conversion_result['error_message']}")
                        
                else:
                    # Ask user what to do
                    print("\n💡 This Excel file needs to be converted to a Google Sheet.")
                    print("   Options:")
                    print("   1. Add --auto-convert flag to automatically convert")
                    print("   2. Run: python convert_excel_to_sheets.py \"your_url\"")
                    print("   3. Manually use 'File > Save as Google Sheets' in your browser")
                    
                    raise Exception(
                        "Excel file detected but auto-conversion is disabled. "
                        "Use --auto-convert flag or convert manually."
                    )
            else:
                print(f"⚠️  Unknown file type: {file_info['mime_type']}")
                print("   Attempting to use as-is...")
                return file_id, False, None
                
        except Exception as e:
            error_str = str(e).lower()
            
            if 'access denied' in error_str or 'permission' in error_str:
                print("⚠️  File access issue - trying with current authentication...")
                return file_id, False, None
            elif 'operation is not supported' in error_str:
                print("📊 Excel file detected (based on error pattern)")
                if auto_convert:
                    print("🔄 Attempting conversion...")
                    # Try conversion even without detection
                    try:
                        conversion_result = convert_spreadsheet_to_sheet(file_id, detector)
                        if conversion_result['success']:
                            print(f"✅ Conversion successful!")
                            return conversion_result['new_file_id'], True, conversion_result
                    except Exception:
                        pass
                
                raise Exception(
                    "This appears to be an Excel file. "
                    "Use --auto-convert flag to convert it to Google Sheets format."
                )
            else:
                print(f"⚠️  Detection failed: {e}")
                print("   Proceeding with original file ID...")
                return file_id, False, None
                
    except ImportError:
        # Detection modules not available, proceed normally
        print("📝 Detection modules not available - proceeding with original URL")
        return extract_spreadsheet_id_from_url(url_or_id), False, None

def fetch_sheet_data(spreadsheet_id=DEFAULT_SPREADSHEET_ID):
    """
    Fetch data from Google Sheet and convert to pandas DataFrame.
    
    Args:
        spreadsheet_id: ID of the Google Sheet to access
        
    Returns:
        pandas.DataFrame: Data from the sheet with column headers
    
    Raises:
        Exception: If authentication fails or sheet cannot be accessed
    """
    try:
        # Get authentication credentials (try enhanced first, fall back to read-only)
        try:
            creds = get_credentials(enhanced_mode=True)
        except Exception:
            creds = get_credentials(enhanced_mode=False)
            
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata and first sheet title
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        first_sheet_title = spreadsheet['sheets'][0]['properties']['title']
        print(f"Accessing sheet: {first_sheet_title}")

        # Fetch all values from the first sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{first_sheet_title}"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in the sheet.")
            return None
            
        # Convert to DataFrame
        # Assume the first row contains headers
        headers = values[0]
        data_rows = values[1:]
        
        # Find the maximum number of columns in any row (including header and data rows)
        max_cols = max([len(row) for row in values])
        
        # Check for duplicate headers and make them unique if necessary
        if len(headers) != len(set(headers)):
            print("Warning: Duplicate column names found. Adding suffixes to make them unique.")
            seen = {}
            unique_headers = []
            for header in headers:
                if header in seen:
                    seen[header] += 1
                    unique_headers.append(f"{header}_{seen[header]}")
                else:
                    seen[header] = 0
                    unique_headers.append(header)
            headers = unique_headers
        
        # If there are more columns in the data than in the headers, add generic column names
        if max_cols > len(headers):
            print(f"Warning: Some rows have more columns ({max_cols}) than the header row ({len(headers)}).")
            print("Adding generic column names for the extra columns.")
            for i in range(len(headers), max_cols):
                headers.append(f"Column_{i+1}")
            
        # Create DataFrame, handling rows that might have different column counts than headers
        padded_data = []
        for row in data_rows:
            if len(row) < max_cols:
                # Pad the row with None values
                padded_data.append(row + [None] * (max_cols - len(row)))
            else:
                padded_data.append(row)
                
        df = pd.DataFrame(padded_data, columns=headers)
        return df
        
    except HttpError as error:
        error_message = str(error)
        
        if "This operation is not supported for this document" in error_message:
            print(f"❌ Error: This appears to be an Excel file, not a native Google Sheet.")
            print(f"💡 Solution: Use --auto-convert flag to automatically convert it.")
            print(f"   Example: python {sys.argv[0]} --sheet-url \"your_url\" --auto-convert")
        else:
            print(f"HTTP Error: {error}")
            print("This might be due to incorrect spreadsheet ID or permission issues.")
        return None
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def print_dataframe_summary(df):
    """
    Print a summary of the DataFrame including shape, columns, and first few rows.
    
    Args:
        df: pandas DataFrame to summarize
    """
    if df is None:
        print("No DataFrame to summarize.")
        return
        
    print("\n=== DataFrame Summary ===")
    print(f"Shape: {df.shape} (rows, columns)")
    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Additional summary info
    print("\nData types:")
    print(df.dtypes)


def print_first_10_rows(df):
    """
    Print the first 10 rows of the DataFrame to the console with all columns visible.
    
    Args:
        df: pandas DataFrame to print
    """
    if df is None:
        print("No DataFrame to print.")
        return
        
    print("\n=== First 10 Rows (All Columns) ===")
    # Use option_context to temporarily override display settings
    with pd.option_context('display.max_columns', None, 'display.width', 1000):
        print(df.head(10))

def export_to_csv(df, output_file='export.csv'):
    """
    Export DataFrame to CSV with mapped column names.
    
    Args:
        df: pandas DataFrame to export
        output_file: name of the output CSV file
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    if df is None or df.empty:
        print("Error: No data to export.")
        return False
    
    try:
        print(f"\n=== Exporting Data to CSV: {output_file} ===")
        
        # Define column mappings based on the Google Sheet structure
        # Map from the human-readable column headers (row 3) to IPTC field names
        direct_mapping = {
            'title': 'Headline',
            'localIdentifier': 'ObjectName', 
            'useRestrictionStatus': 'CopyrightNotice',
            'scopeAndContentNote': 'Caption-Abstract',
            'specificMediaType': 'Source',
            'personalContributorName': 'By-line',
            'copyStatus': 'By-lineTitle'
        }
        
        # Check if we have the human-readable row structure (row 3 contains the labels)
        # Look for row 3 content to get the actual column mappings
        human_readable_mapping = {}
        
        # Try to identify the human-readable headers from row 3 of the data
        if len(df) > 2:  # Make sure we have at least 3 rows
            try:
                # Row 3 (index 2) should contain the human-readable headers
                row3_values = df.iloc[2].values
                
                # Create mapping based on what we find in row 3
                for i, col_name in enumerate(df.columns):
                    if i < len(row3_values) and row3_values[i]:
                        header_value = str(row3_values[i]).strip()
                        
                        # Map the human-readable headers to IPTC fields
                        if header_value == 'Title':
                            human_readable_mapping[col_name] = 'Headline'
                        elif header_value == 'Accession Number':
                            human_readable_mapping[col_name] = 'ObjectName'
                        elif header_value in ['Restrictions', 'Copyright Notice']:
                            human_readable_mapping[col_name] = 'CopyrightNotice'
                        elif header_value in ['Scopenote', 'Caption Abstract']:
                            human_readable_mapping[col_name] = 'Caption-Abstract'
                        elif header_value == 'Source':
                            human_readable_mapping[col_name] = 'Source'
                        elif header_value in ['Source Photographer', 'Byline']:
                            human_readable_mapping[col_name] = 'By-line'
                        elif header_value in ['Institutional Creator', 'BylineTitle']:
                            human_readable_mapping[col_name] = 'By-lineTitle'
                        elif header_value in ['Month', 'DateCreated [MM]']:
                            # We'll handle date creation separately
                            pass
                        elif header_value in ['Day', 'DateCreated [DD]']:
                            # We'll handle date creation separately  
                            pass
                        elif header_value in ['Year', 'DateCreated [YYYY]']:
                            # We'll handle date creation separately
                            pass
                            
                print(f"Found human-readable mappings from row 3: {len(human_readable_mapping)} columns")
                        
            except Exception as e:
                print(f"Warning: Could not parse row 3 for human-readable headers: {e}")
        
        # Use human readable mapping if we found any, otherwise fall back to API field mapping
        mapping_to_use = human_readable_mapping if human_readable_mapping else {}
        
        # If no human readable columns found, try API field names
        if not mapping_to_use:
            for api_col, iptc_col in direct_mapping.items():
                if api_col in df.columns:
                    mapping_to_use[api_col] = iptc_col
        
        # Check if we found any mappings
        if not mapping_to_use:
            print("Warning: No recognized columns found for mapping.")
            print("Available columns:", ', '.join(df.columns.tolist()))
            print("Expected columns (human-readable):", ', '.join(human_readable_mapping.keys()))
            print("Expected columns (API fields):", ', '.join(direct_mapping.keys()))
            proceed = input("Continue anyway with available columns? (y/n): ")
            if proceed.lower() != 'y':
                return False
            # Use the first few columns as fallback
            mapping_to_use = {col: col for col in df.columns[:7] if col.strip()}
        
        # Create new DataFrame with mapped columns
        new_df = pd.DataFrame()
        renamed_columns = []
        
        for src_col, dst_col in mapping_to_use.items():
            if src_col in df.columns:
                new_df[dst_col] = df[src_col]
                renamed_columns.append(f"'{src_col}' -> '{dst_col}'")
                print(f"Mapped: '{src_col}' -> '{dst_col}'")
            else:
                print(f"Skipped: '{src_col}' (not found in source data)")
        
        # Add DateCreated column in ISO format (YYYY-MM-DD) from productionDateMonth, productionDateDay, productionDateYear columns
        try:
            if all(col in df.columns for col in ['productionDateMonth', 'productionDateDay', 'productionDateYear']):
                print("Creating 'DateCreated' column in ISO format (YYYY-MM-DD)...")
                
                # Initialize an empty date column the same length as the DataFrame
                new_df['DateCreated'] = ''
                
                # Skip the first 3 rows which contain header information
                # Start processing from index 3 (4th row) onwards
                for idx in range(3, len(df)):
                    try:
                        # Get date components and convert to string, handling None values
                        month_str = str(df.loc[idx, 'productionDateMonth']).strip() if df.loc[idx, 'productionDateMonth'] is not None else ''
                        day_str = str(df.loc[idx, 'productionDateDay']).strip() if df.loc[idx, 'productionDateDay'] is not None else ''
                        year_str = str(df.loc[idx, 'productionDateYear']).strip() if df.loc[idx, 'productionDateYear'] is not None else ''
                        
                        # Replace 'nan', 'None', or 'NaN' strings with empty string
                        month_str = '' if month_str.lower() in ['nan', 'none', 'null'] else month_str
                        day_str = '' if day_str.lower() in ['nan', 'none', 'null'] else day_str
                        year_str = '' if year_str.lower() in ['nan', 'none', 'null'] else year_str
                        
                        # Check if all components are present and look like numbers
                        if (month_str and day_str and year_str and
                            month_str.isdigit() and day_str.isdigit() and year_str.isdigit()):
                            
                            # Convert to integers to validate and handle leading zeros
                            year_int = int(year_str)
                            month_int = int(month_str)
                            day_int = int(day_str)
                            
                            # Basic date validation
                            if 1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 0:
                                # Format with leading zeros for month and day
                                new_df.loc[idx, 'DateCreated'] = f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
                            else:
                                print(f"Skipping row {idx}: Date out of valid range: {month_int}/{day_int}/{year_int}")
                        else:
                            # One or more components missing or not a valid number - skip silently for data rows
                            if idx > 5:  # Only log warnings for non-header rows after index 5
                                print(f"Skipping row {idx}: Incomplete or non-numeric date components")
                    except Exception as e:
                        if idx > 5:  # Only log warnings for non-header rows
                            print(f"Warning: Error processing date at row {idx}: {e}")
                
                print(f"Added 'DateCreated' column with ISO formatted dates (YYYY-MM-DD)")
            else:
                missing_cols = [col for col in ['productionDateMonth', 'productionDateDay', 'productionDateYear'] if col not in df.columns]
                print(f"Warning: Cannot create 'DateCreated' column. Missing required column(s): {', '.join(missing_cols)}")
        except Exception as e:
            print(f"Error creating 'DateCreated' column: {str(e)}")
        
        # Verify we have data to export
        if new_df.empty:
            print("Error: No columns were successfully mapped!")
            return False
            
        print(f"\nSuccessfully mapped {len(renamed_columns)} columns:")
        for mapping in renamed_columns:
            print(f"  {mapping}")
        
        # Export to CSV with UTF-8 encoding
        print(f"\nExporting to '{output_file}' with UTF-8 encoding...")
        new_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"Conversion completed successfully. Output saved to '{output_file}'")
        print(f"Rows processed: {len(new_df)}")
        return True
    
    except Exception as e:
        print(f"Error during CSV export: {str(e)}")
        return False

def main():
    """Main function to execute the script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Load data from a Google Spreadsheet into a pandas DataFrame. Now supports Excel files!',
        epilog="""
Examples:
  # Native Google Sheet
  python google-to-csv-enhanced.py --sheet-url "https://docs.google.com/spreadsheets/d/ID/edit"
  
  # Excel file with auto-conversion
  python google-to-csv-enhanced.py --sheet-url "https://drive.google.com/file/d/ID/view" --auto-convert
  
  # Export to CSV
  python google-to-csv-enhanced.py --sheet-url "URL" --export-csv custom_output.csv
"""
    )
    
    # Add arguments
    parser.add_argument(
        '--sheet-url', '-u',
        default=f"https://docs.google.com/spreadsheets/d/{DEFAULT_SPREADSHEET_ID}/edit",
        help='URL of the Google Spreadsheet or Excel file'
    )
    
    parser.add_argument(
        '--export-csv', '-e',
        nargs='?',
        const='export.csv',
        help='Export data to CSV file (default filename: export.csv)'
    )
    
    parser.add_argument(
        '--auto-convert', '-a',
        action='store_true',
        help='Automatically convert Excel files to Google Sheets'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    print("🚀 Enhanced Google Sheets to CSV Converter")
    print("=" * 60)
    print("Now supports both Google Sheets and Excel files!")
    print()
    
    # Detect file type and convert if needed
    try:
        spreadsheet_id, was_converted, conversion_info = detect_and_convert_if_needed(
            args.sheet_url, 
            auto_convert=args.auto_convert
        )
        
        if was_converted:
            print(f"\n💾 Conversion completed! Using new Google Sheet:")
            print(f"   ID: {spreadsheet_id}")
            print(f"   URL: {conversion_info['new_file_url']}")
            print(f"   💡 Bookmark this URL for future use!")
        else:
            print(f"Using spreadsheet ID: {spreadsheet_id}")
            
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Falling back to default spreadsheet ID: {DEFAULT_SPREADSHEET_ID}")
        spreadsheet_id = DEFAULT_SPREADSHEET_ID
    except Exception as e:
        print(f"Error: {e}")
        if args.auto_convert:
            print("\n💡 Try running without --auto-convert to see more details")
        sys.exit(1)
    
    print("\nFetching data from Google Sheet...")
    df = fetch_sheet_data(spreadsheet_id)
    
    if df is not None:
        print("\n✅ Data loaded successfully!")
        print_dataframe_summary(df)
        print_first_10_rows(df)
        
        # Export to CSV if requested
        if args.export_csv:
            output_file = args.export_csv
            export_success = export_to_csv(df, output_file)
            if not export_success:
                print(f"Warning: CSV export failed")
                
        # Show success message with helpful info
        if was_converted:
            print(f"\n🎉 Success! Your Excel file was converted and processed.")
            print(f"📋 Original file remains unchanged")
            print(f"📊 New Google Sheet URL: {conversion_info['new_file_url']}")
        
    else:
        print("\n❌ Failed to load data from the Google Sheet.")
        if not args.auto_convert:
            print("💡 If this is an Excel file, try adding --auto-convert flag")
        print("Please check your authentication credentials and spreadsheet ID.")
        sys.exit(1)

if __name__ == "__main__":
    main()
