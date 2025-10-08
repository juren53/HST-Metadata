#!/usr/bin/env python3
"""
Google Sheets to Pandas DataFrame Script

This script accesses a specified Google Sheet and loads its data into a pandas DataFrame.
It can also export the data to a CSV file with mapped column names.

Usage:
    python x3.py [--sheet-url URL] [--export-csv [FILENAME]]

Options:
    --sheet-url, -u            URL of the Google Spreadsheet
    --export-csv, -e [FILENAME] Export data to CSV file (default: export.csv)
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
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# === TARGET SPREADSHEET ===
# Default spreadsheet ID to use if none provided via command line
DEFAULT_SPREADSHEET_ID = '19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4'

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def extract_spreadsheet_id_from_url(url):
    """
    Extract the spreadsheet ID from a Google Sheets URL.
    
    Args:
        url: URL of the Google Spreadsheet
        
    Returns:
        str: Spreadsheet ID extracted from the URL
    
    Raises:
        ValueError: If the URL does not appear to be a valid Google Sheets URL
    """
    # Handle direct spreadsheet ID input (not a URL)
    if not url.startswith('http'):
        return url.strip()
    
    # Standard URL format: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/...
    match = re.search(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
        
    # Alternative format
    alt_match = re.search(r'spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    if alt_match:
        return alt_match.group(1)
        
    raise ValueError(
        "Invalid Google Sheets URL. Expected format: "
        "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/... "
        "or just the SPREADSHEET_ID itself."
    )

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
        # Get authentication credentials
        creds = get_credentials()
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
        direct_mapping = {
            'title': 'Headline',
            'localIdentifier': 'ObjectName',
            'useRestrictionStatus': 'CopyrightNotice',
            'scopeAndContentNote': 'Caption-Abstract',
            'specificMediaType': 'Source',
            'personalContributorName': 'By-line',
            'copyStatus': 'By-lineTitle'
        }
        
        # Check for missing columns
        missing_columns = [col for col in direct_mapping.keys() if col not in df.columns]
        if missing_columns:
            print(f"Warning: The following columns were not found in the data: {', '.join(missing_columns)}")
            print("Available columns:", ', '.join(df.columns.tolist()))
            proceed = input("Continue anyway with available columns? (y/n): ")
            if proceed.lower() != 'y':
                return False
        
        # Create new DataFrame with mapped columns
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
        description='Load data from a Google Spreadsheet into a pandas DataFrame.',
        epilog="""
Examples:
  python x3.py --sheet-url "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit"
  python x3.py --sheet-url "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit" --export-csv
  python x3.py --sheet-url "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit" --export-csv custom_output.csv
"""
    )
    
    # Add arguments
    parser.add_argument(
        '--sheet-url', '-u',
        default=f"https://docs.google.com/spreadsheets/d/{DEFAULT_SPREADSHEET_ID}/edit",
        help='URL of the Google Spreadsheet'
    )
    
    parser.add_argument(
        '--export-csv', '-e',
        nargs='?',
        const='export.csv',
        help='Export data to CSV file (default filename: export.csv)'
    )
    # Parse arguments
    args = parser.parse_args()
    
    # Extract spreadsheet ID from URL
    try:
        spreadsheet_id = extract_spreadsheet_id_from_url(args.sheet_url)
        print(f"Using spreadsheet ID: {spreadsheet_id}")
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Falling back to default spreadsheet ID: {DEFAULT_SPREADSHEET_ID}")
        spreadsheet_id = DEFAULT_SPREADSHEET_ID
    
    print("Fetching data from Google Sheet...")
    df = fetch_sheet_data(spreadsheet_id)
    
    if df is not None:
        print("\nData loaded successfully!")
        print_dataframe_summary(df)
        print_first_10_rows(df)
        
        # Export to CSV if requested
        if args.export_csv:
            output_file = args.export_csv
            export_success = export_to_csv(df, output_file)
            if not export_success:
                print(f"Warning: CSV export failed")
    else:
        print("\nFailed to load data from the Google Sheet.")
        print("Please check your authentication credentials and spreadsheet ID.")
        sys.exit(1)
if __name__ == "__main__":
    main()
