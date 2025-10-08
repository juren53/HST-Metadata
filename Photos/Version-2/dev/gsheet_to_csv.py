#!/usr/bin/env python3
# Google Sheets to CSV Conversion Script
# This script processes Google Sheets documents by:
# 1. Authenticating with Google Sheets API using OAuth2
# 2. Downloading data from the specified Google Sheet
# 3. Applying column mappings (same as excel_to_csv.py)
# 4. Exporting to CSV with UTF-8 encoding

import pandas as pd
import os
import sys
import argparse
import re
from urllib.parse import urlparse, parse_qs

# Google Sheets API libraries
import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import io
import tempfile

# Google Drive API
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Define the scopes for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def extract_sheet_id_from_url(url):
    """Extract the Google Sheet ID from a Google Sheets URL.
    
    Args:
        url (str): The Google Sheets URL
        
    Returns:
        str: The extracted sheet ID
    """
    # Check if it's a valid Google Sheets URL
    if not url or 'docs.google.com/spreadsheets' not in url:
        raise ValueError("Invalid Google Sheets URL")
    
    # Extract the sheet ID from the URL
    # The ID is the part after /d/ and before /edit
    pattern = r'/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    
    # Alternative parsing using urlparse for different URL formats
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    
    # Find the part that looks like a sheet ID
    for part in path_parts:
        if len(part) > 20 and '.' in part:  # Sheet IDs are typically long alphanumeric strings
            return part
    
    raise ValueError("Could not extract sheet ID from the provided URL")

def get_google_sheet_credentials(force_auth=False):
    """Get or refresh Google API credentials.
    
    Args:
        force_auth (bool): Force reauthentication even if credentials exist
        
    Returns:
        Credentials: The OAuth2 credentials for Google API
    """
    creds = None
    token_file = 'token.pickle'
    
    # Check if token.pickle exists (cached credentials)
    if os.path.exists(token_file) and not force_auth:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
            
        # Check if the token has all the required scopes
        if creds and hasattr(creds, 'scopes'):
            # Convert scopes to sets for comparison (order doesn't matter)
            token_scopes = set(creds.scopes)
            required_scopes = set(SCOPES)
            
            # Check if all required scopes are in the token
            if not required_scopes.issubset(token_scopes):
                print("Token has insufficient scopes. Forcing reauthentication.")
                print(f"Token scopes: {token_scopes}")
                print(f"Required scopes: {required_scopes}")
                creds = None  # Force reauthentication
    
    # If no credentials found, they're invalid, or force_auth is True
    if not creds or not creds.valid or force_auth:
        if creds and creds.expired and creds.refresh_token and not force_auth:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            # Check if client_secret.json exists
            if not os.path.exists('client_secret.json'):
                print("Error: client_secret.json not found.")
                print("\nTo set up Google Sheets API access:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project")
                print("3. Enable the Google Sheets API")
                print("4. Enable the Google Drive API")
                print("5. Create OAuth2 credentials (Desktop Application)")
                print("6. Download the credentials as client_secret.json")
                print("7. Place the client_secret.json file in the same directory as this script")
                sys.exit(1)
                
            print("Initiating authentication flow with scopes:")
            for scope in SCOPES:
                print(f"  - {scope}")
                
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
            print(f"Credentials saved to {token_file}")
    
    return creds

def download_file_from_drive(creds, file_id):
    """Download a file from Google Drive using the file ID.
    
    Args:
        creds: OAuth2 credentials
        file_id (str): The Google Drive file ID
        
    Returns:
        str: Path to the downloaded file
    """
    try:
        # Create Drive API client
        service = build('drive', 'v3', credentials=creds)
        
        # Get file metadata to determine file type
        file_metadata = service.files().get(fileId=file_id, fields="name,mimeType").execute()
        file_name = file_metadata.get('name', f'downloaded_file_{file_id}')
        mime_type = file_metadata.get('mimeType', '')
        
        print(f"File info - Name: {file_name}, Type: {mime_type}")
        
        # For Excel files exported from Google Sheets, we need to export in Excel format
        if mime_type == 'application/vnd.google-apps.spreadsheet':
            print("Native Google Sheet detected, exporting as Excel...")
            request = service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            print("Non-native Google Sheet detected, downloading directly...")
            request = service.files().get_media(fileId=file_id)
        
        # Download to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)  # Close the file descriptor
        
        with open(temp_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}% complete")
        
        print(f"File downloaded to temporary location: {temp_path}")
        return temp_path
    
    except Exception as e:
        print(f"Error downloading file from Google Drive: {str(e)}")
        raise

def get_sheet_data(sheet_id):
    """Retrieve data from a Google Sheet using the sheet ID.
    This function attempts to:
    1. Open the file as a Google Sheet directly using gspread
    2. If that fails, fall back to downloading the file via Google Drive API
       and processing it with pandas
    
    Args:
        sheet_id (str): The Google Sheet ID
        
    Returns:
        pandas.DataFrame: The sheet data as a DataFrame
    """
    # Get credentials
    creds = get_google_sheet_credentials(force_auth=False)
    
    # Method 1: Try using Google Sheets API first
    try:
        print(f"Attempting to access as native Google Sheet with ID: {sheet_id}")
        
        # Create a gspread client
        gc = gspread.authorize(creds)
        
        # Try to open the Google Sheet
        sheet = gc.open_by_key(sheet_id)
        
        # Get the first worksheet (default)
        worksheet = sheet.get_worksheet(0)
        
        # Get all values
        data = worksheet.get_all_records()
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        
        print("Successfully accessed as a native Google Sheet")
        return df
        
    except gspread.exceptions.APIError as e:
        error_msg = str(e)
        if "This operation is not supported for this document" in error_msg:
            print("This file is not a native Google Sheet. Falling back to Google Drive API...")
            
            # Method 2: Download the file using Google Drive API and process with pandas
            try:
                # Try with existing credentials first
                try:
                    temp_file_path = download_file_from_drive(creds, sheet_id)
                except Exception as drive_error:
                    if "insufficient authentication scopes" in str(drive_error).lower() or "insufficient permission" in str(drive_error).lower():
                        print("Credentials have insufficient scopes for Google Drive API. Reauthenticating...")
                        # Force reauthentication to get the right scopes
                        creds = get_google_sheet_credentials(force_auth=True)
                        temp_file_path = download_file_from_drive(creds, sheet_id)
                    else:
                        raise
                
                # Read the Excel file using pandas
                print(f"Reading Excel file from temp location: {temp_file_path}")
                df = pd.read_excel(temp_file_path)
                
                # Clean up the temporary file
                try:
                    os.remove(temp_file_path)
                    print(f"Temporary file removed: {temp_file_path}")
                except:
                    print(f"Warning: Could not remove temporary file: {temp_file_path}")
                
                return df
                
            except Exception as drive_error:
                print(f"Error downloading/processing file with Google Drive API: {str(drive_error)}")
                raise
        else:
            print(f"Error accessing Google Sheet: {error_msg}")
            raise
    
    except Exception as e:
        print(f"Unexpected error accessing Google Sheet: {str(e)}")
        raise

def analyze_sheet_structure(df):
    """Analyze the structure of the Google Sheet data and print debugging information.
    
    Args:
        df (pandas.DataFrame): The DataFrame containing the sheet data
        
    Returns:
        pandas.DataFrame: The input DataFrame (unchanged)
    """
    print("\n=== GOOGLE SHEET STRUCTURE ANALYSIS ===")
    
    # Print shape information
    print(f"Sheet shape: {df.shape} (rows × columns)")
    
    # Print the first 5 rows to understand structure
    print("\nFirst 5 rows of the Google Sheet:")
    print(df.head(5).to_string())
    
    # Print all column names
    print("\nColumn names in the sheet:")
    for i, col in enumerate(df.columns):
        print(f"  Column {i}: {col} (Type: {type(col).__name__})")
    
    # Check for potential header rows
    print("\nExamining first few rows for patterns:")
    for i in range(min(5, len(df))):
        row_content = ' '.join([str(x) for x in df.iloc[i].tolist()])
        print(f"  Row {i}: {row_content[:100]}{'...' if len(row_content) > 100 else ''}")
        if "HST" in row_content and "DRUPAL" in row_content:
            print(f"  --> Potential header row found at index {i}")
    
    print("=== END OF ANALYSIS ===\n")
    return df

def convert_gsheet_to_csv(sheet_url, output_file="export.csv", analyze=False):
    """Process a Google Sheet and convert it to CSV.
    
    Args:
        sheet_url (str): The URL of the Google Sheet
        output_file (str): The output CSV file path
        analyze (bool): Whether to run analysis on the sheet structure
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract the sheet ID from the URL
        sheet_id = extract_sheet_id_from_url(sheet_url)
        print(f"Extracted sheet ID: {sheet_id}")
        
        # Get sheet data
        print(f"Retrieving data from Google Sheet...")
        df = get_sheet_data(sheet_id)
        
        # Run analysis if requested
        if analyze:
            df = analyze_sheet_structure(df)
        
        # Add debugging information
        print("\nDataFrame columns after loading (exact names):")
        for col in df.columns:
            print(f"  '{col}'")
        
        print("\nFirst row of data:")
        if len(df) > 0:
            print(df.iloc[0].to_string())
        else:
            print("No data rows found")
        
        # Drop any NaN columns and rows with all NaN
        df = df.dropna(axis=1, how='all')
        
        # Print information about loaded data
        print(f"\nDataFrame shape after dropping empty columns: {df.shape} rows × {len(df.columns)} columns")
        if df.empty:
            print("Error: DataFrame is empty after loading!")
            return False
        
        # Step 2: Define direct column mappings - same as in excel_to_csv.py
        print("Setting up column mappings...")
        
        # These mappings are the same as in excel_to_csv.py
        direct_mapping = {
            'title': 'Headline',
            'localIdentifier': 'ObjectName',
            'useRestriction.status': 'CopyrightNotice',
            'scopeAndContentNote': 'Caption-Abstract', 
            'physicalOccurrences.0.mediaOccurrences.0.specificMediaType': 'Source',
            'contributors.0.heading': 'By-line',
            'physicalOccurrences.0.copyStatus': 'By-lineTitle'
        }
        
        # Check for missing columns
        missing_columns = [col for col in direct_mapping.keys() if col not in df.columns]
        if missing_columns:
            print(f"Warning: The following columns were not found in the file: {', '.join(missing_columns)}")
            print("Available columns:", ', '.join(df.columns.tolist()))
            proceed = input("Continue anyway with available columns? (y/n): ")
            if proceed.lower() != 'y':
                return False
        
        # Step 3: Apply renaming only for columns that exist and create new DataFrame with only those columns
        new_df = pd.DataFrame()
        renamed_columns = []
        
        for src_col, dst_col in direct_mapping.items():
            if src_col in df.columns:
                new_df[dst_col] = df[src_col]
                renamed_columns.append(f"'{src_col}' -> '{dst_col}'")
                print(f"Mapped: '{src_col}' -> '{dst_col}'")
            else:
                print(f"Skipped: '{src_col}' (not found in source data)")
        
        # Verify we have data to export
        if new_df.empty:
            print("Error: No columns were successfully mapped!")
            return False
            
        print(f"\nSuccessfully mapped {len(renamed_columns)} columns:")
        for mapping in renamed_columns:
            print(f"  {mapping}")
        
        # Step 4: Export to CSV with UTF-8 encoding
        print(f"\nExporting to '{output_file}' with UTF-8 encoding...")
        new_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"Conversion completed successfully. Output saved to '{output_file}'")
        print(f"Rows processed: {len(new_df)}")
        return True
    
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(description='Google Sheets to CSV Conversion Tool')
    parser.add_argument('sheet_url', nargs='?', help='Google Sheets URL')
    parser.add_argument('-o', '--output', default='export.csv', help='Output CSV file (default: export.csv)')
    parser.add_argument('--analyze', action='store_true', help='Run sheet structure analysis')
    parser.add_argument('--force-auth', action='store_true', help='Force reauthentication (useful when changing API scopes)')
    
    args = parser.parse_args()
    
    print("Google Sheets to CSV Conversion Tool")
    print("-----------------------------------")
    
    # If no URL provided, prompt for it
    # If no URL provided, prompt for it
    sheet_url = args.sheet_url
    if not sheet_url:
        sheet_url = input("Enter Google Sheets URL: ")
    
    # Force reauthentication if requested
    if args.force_auth:
        print("Forcing reauthentication...")
        # Just getting credentials with force_auth will trigger reauthentication
        get_google_sheet_credentials(force_auth=True)
    
    # Run the conversion
    success = convert_gsheet_to_csv(sheet_url, args.output, args.analyze)

if __name__ == "__main__":
    main()

