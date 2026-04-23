#!/usr/bin/env python3
"""
Excel and Google Sheets to CSV Converter for HST Metadata

This script reads Excel files or Google Sheets containing HST metadata, removes the first 3 rows,
makes the row with "HST - DRUPAL FIELDS" the header row, renames specific columns
according to a predefined mapping, and exports the result to a CSV file.

Usage:
    python process_excel.py

Requirements for Google Sheets:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import pandas as pd
import os
import sys
import glob
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def authenticate_google_sheets():
    """
    Authenticate to Google Sheets API.
    
    Returns:
        google.auth.credentials.Credentials: Authenticated credentials for Google Sheets
    """
    # Using the minimal scope required for the app
    # This reduces the verification requirements for the OAuth consent screen
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly'
        # Removed drive.readonly scope to simplify verification
    ]
    creds = None
    max_retries = 3
    retry_count = 0

    print("\n" + "="*80)
    print("GOOGLE SHEETS AUTHENTICATION".center(80))
    print("="*80)
    
    # Check if token.json exists with stored credentials
    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as token_file:
                creds = Credentials.from_authorized_user_info(json.load(token_file))
            print("✓ Loaded existing credentials from token.json")
        except Exception as e:
            print(f"✗ Error loading credentials: {e}")
            print("  Will attempt to reauthenticate...")
    
    # If no valid credentials, authenticate
    while (not creds or not creds.valid) and retry_count < max_retries:
        retry_count += 1
        print(f"Authentication attempt {retry_count} of {max_retries}")
        
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing expired token...")
                creds.refresh(Request())
                print("Token refreshed successfully.")
                
                # Save the refreshed credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                    
                break  # Successfully refreshed
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                print("Will attempt to reauthenticate from scratch...")
                creds = None
        
        # If credentials couldn't be refreshed, need to authenticate from scratch
        if not creds:
            # Check if credentials.json exists
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found.")
                print("Please download OAuth 2.0 credentials from Google Cloud Console")
                print("and save as 'credentials.json' in the current directory.")
                return None
            
            try:
                print("\n" + "-"*80)
                print("STARTING NEW AUTHENTICATION FLOW".center(80))
                print("-"*80)
                print("\nINFORMATION ABOUT VERIFICATION STATUS:")
                print("  • This application uses Google's OAuth to access your Google Sheets")
                print("  • You may see a warning: \"Google hasn't verified this app\"")
                print("  • This is normal for applications that aren't publicly distributed")
                print("  • The app only requests read-only access to your spreadsheets")
                print("\nHOW TO PROCEED:")
                print("  1. When the browser opens, sign in with your Google account")
                print("  2. If you see the verification warning, click \"Advanced\"")
                print("  3. Then click \"Go to hstl-photo-metadata (unsafe)\"")
                print("  4. Review the permissions and click \"Continue\" to grant access")
                print("\nA browser window will open momentarily...")
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("\n✓ Authentication successful! Credentials saved to token.json")
                break  # Successfully authenticated
            except Exception as e:
                error_message = str(e).lower()
                
                # Check for common OAuth errors and provide more helpful messages
                if "access_denied" in error_message:
                    print("\n✗ Authentication failed: You denied access to the application")
                    print("  If you want to use this application, you need to allow access")
                    print("  Please try again and click 'Allow' when prompted")
                elif "verification_required" in error_message or "hasn't been verified" in error_message:
                    print("\n✗ Authentication failed: App verification issue")
                    print("\nDETAILS ABOUT THE VERIFICATION WARNING:")
                    print("  This application hasn't been verified by Google yet.")
                    print("  To proceed anyway:")
                    print("  1. Click 'Advanced' on the warning screen")
                    print("  2. Click 'Go to hstl-photo-metadata (unsafe)'")
                    print("  3. Continue with the authentication process")
                else:
                    print(f"\n✗ Error during authentication attempt {retry_count}: {e}")
                
                if retry_count >= max_retries:
                    print("\n⚠ Maximum retries reached. Authentication failed.")
                    print("\nTROUBLESHOOTING STEPS:")
                    print("  1. Check your internet connection")
                    print("  2. Ensure you're using the correct Google account")
                    print("  3. Try deleting the token.json file and restart the application")
                    print("  4. If the error persists, you may need to set up your own OAuth credentials:")
                    print("     a. Go to https://console.cloud.google.com/")
                    print("     b. Create a project and enable the Google Sheets API")
                    print("     c. Set up OAuth consent screen and create credentials")
                    print("     d. Download the credentials.json file to this directory")
                    return None
                print(f"\nRetrying authentication (attempt {retry_count+1}/{max_retries})...")
    
    return creds

def get_google_sheet_data(spreadsheet_id, sheet_range=''):
    """
    Get data from Google Sheets.
    
    Args:
        spreadsheet_id (str): The ID of the spreadsheet
        sheet_range (str): The range of cells to retrieve (e.g., 'Sheet1!A1:Z1000')
    
    Returns:
        list: The values from the spreadsheet
    """
    print(f"\nAttempting to access Google Sheet with ID: {spreadsheet_id}")
    creds = authenticate_google_sheets()
    if not creds:
        print("Failed to authenticate with Google Sheets. Please check your credentials.")
        print("You may need to delete token.json and re-authenticate.")
        return None
    
    try:
        # Build the service with more detailed debugging
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        # First validate access to the spreadsheet by checking metadata
        print("Verifying access to the spreadsheet...")
        try:
            # Try to get basic metadata first to validate access
            metadata = sheet.get(spreadsheetId=spreadsheet_id, fields="properties,sheets.properties.title").execute()
            print("Successfully accessed spreadsheet metadata.")
            
            # Check if we can get sheet names
            sheet_titles = [s['properties']['title'] for s in metadata.get('sheets', [])]
            print(f"Available sheets: {', '.join(sheet_titles)}")
            
            # Check spreadsheet permissions 
            print(f"Spreadsheet title: {metadata.get('properties', {}).get('title', 'Unknown')}")
            
            # If no range is specified, get the first sheet
            if not sheet_range:
                if sheet_titles:
                    first_sheet_name = sheet_titles[0]
                    sheet_range = f"{first_sheet_name}"
                    print(f"Using first sheet: {first_sheet_name}")
                else:
                    print("ERROR: No sheets found in the spreadsheet.")
                    return None
            
        except HttpError as error:
            error_details = json.loads(error.content.decode('utf-8'))
            status_code = error.resp.status
            
            print(f"Error accessing spreadsheet metadata: {error}")
            print(f"Status code: {status_code}")
            print(f"Error details: {error_details}")
            
            if status_code == 403:
                print("\nACCESS DENIED: You don't have permission to access this spreadsheet.")
                print("Possible issues:")
                print("1. The spreadsheet is not shared with your Google account")
                print("2. The Google Cloud project is not properly configured")
                print("3. Your OAuth consent screen needs verification")
                print("\nSuggested actions:")
                print("- Ensure the spreadsheet is shared with your Google account")
                print("- Check Google Cloud Console for OAuth verification status")
                print("- Try a different spreadsheet that you own")
            elif status_code == 404:
                print("\nNOT FOUND: The spreadsheet ID doesn't exist or has been deleted.")
            
            return None
        
        # Now try to get the values
        print(f"Retrieving data from sheet range: {sheet_range}...")
        try:
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
            values = result.get('values', [])
            
            if not values:
                print('WARNING: No data found in the specified sheet range.')
                return None
                
            print(f"Successfully retrieved {len(values)} rows of data.")
            return values
            
        except HttpError as value_error:
            error_details = json.loads(value_error.content.decode('utf-8'))
            print(f"Error retrieving values: {value_error}")
            print(f"Error details: {error_details}")
            
            if "This operation is not supported for this document" in str(value_error):
                print("\nSPECIAL ERROR: This operation is not supported for this document")
                print("This typically happens when:")
                print("1. The document is not a Google Sheet (might be a Google Doc or other type)")
                print("2. The spreadsheet requires a different access method")
                print("3. The Google Sheet has specific sharing restrictions")
                
                print("\nTrying alternative access method via Drive API...")
                try:
                    # If Sheets API fails, try using Drive API to at least confirm the file type
                    drive_service = build('drive', 'v3', credentials=creds)
                    file_metadata = drive_service.files().get(fileId=spreadsheet_id, fields="name,mimeType").execute()
                    
                    print(f"File information from Drive API:")
                    print(f"- Name: {file_metadata.get('name', 'Unknown')}")
                    print(f"- Type: {file_metadata.get('mimeType', 'Unknown')}")
                    
                    if file_metadata.get('mimeType') != 'application/vnd.google-apps.spreadsheet':
                        print("\nERROR: The specified ID is not a Google Sheet!")
                        print(f"It appears to be a {file_metadata.get('mimeType')}")
                        print("Please provide a valid Google Sheet ID.")
                    else:
                        print("\nThe file is confirmed to be a Google Sheet, but there may be special")
                        print("access restrictions or settings preventing the API from reading it.")
                except Exception as drive_error:
                    print(f"Drive API check also failed: {drive_error}")
            
            return None
            
    except Exception as e:
        print(f"Unexpected error accessing Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return None

def google_sheet_to_dataframe(sheet_values):
    """
    Convert Google Sheets data to a pandas DataFrame.
    
    Args:
        sheet_values (list): The values from the Google Sheet
    
    Returns:
        pandas.DataFrame: DataFrame containing the sheet data
    """
    if not sheet_values:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(sheet_values)
    
    # Set the first row as headers
    df.columns = df.iloc[0]
    df = df[1:]
    
    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    return df

def extract_sheet_id_from_url(url):
    """
    Extract the spreadsheet ID from a Google Sheets URL.
    
    Args:
        url (str): The Google Sheets URL
    
    Returns:
        str: The spreadsheet ID
    """
    # Common format: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit...
    parts = url.split('/')
    for i, part in enumerate(parts):
        if part == 'd' and i+1 < len(parts):
            return parts[i+1]
    return None

def select_excel_file():
    """
    Lists all Excel files in the current directory and lets the user select one,
    or allows them to use a Google Sheet URL.
    
    Returns:
        tuple: (data_source, file_or_id) where:
            - data_source is 'excel' or 'google_sheet'
            - file_or_id is the Excel filename or Google Sheet ID
    """
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get the list of Excel files in the working directory
    excel_files = [file for file in os.listdir() if file.endswith('.xlsx') or file.endswith('.xls')]
    
    # Build the menu options
    options = []
    
    # Add Excel files to options
    for file in excel_files:
        options.append(('excel', file))
    
    # Add Google Sheets option
    options.append(('google_sheet', 'Google Sheet (Enter URL)'))
    
    # Print the options
    print("Select a data source:")
    for i, (source, name) in enumerate(options):
        print(f"{i + 1}. {name}")
    
    # Ask the user to select an option
    try:
        selected_index = int(input("\nEnter your choice (number): ")) - 1
        if selected_index < 0 or selected_index >= len(options):
            print("Invalid selection. Please enter a valid number.")
            return select_excel_file()  # Recursive call to try again
        
        data_source, selected_option = options[selected_index]
        
        if data_source == 'excel':
            print(f"\nSelected Excel file: {selected_option}")
            return ('excel', selected_option)
        elif data_source == 'google_sheet':
            # Prompt for Google Sheet URL
            sheet_url = input("\nEnter the Google Sheet URL: ")
            sheet_id = extract_sheet_id_from_url(sheet_url)
            
            if not sheet_id:
                print("Invalid Google Sheet URL. Could not extract Sheet ID.")
                return select_excel_file()  # Try again
            
            print(f"\nSelected Google Sheet ID: {sheet_id}")
            return ('google_sheet', sheet_id)
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return select_excel_file()  # Recursive call to try again

def is_string_column(series):
    """
    Check if a pandas Series contains string data.
    
    Args:
        series: A pandas Series object
        
    Returns:
        bool: True if the series contains string data
    """
    return series.dtypes == 'object' or series.dtypes == 'string'

def process_data_source(data_source, source_identifier, output_file="export.csv"):
    """
    Process the Excel file or Google Sheet by removing rows and renaming headers.
    
    Args:
        data_source (str): 'excel' or 'google_sheet'
        source_identifier (str): Excel file name or Google Sheet ID
        output_file (str): Name of the output CSV file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize df_raw and df based on the data source
        if data_source == 'excel':
            # Print status message
            print(f"Reading Excel file: {source_identifier}...")
            
            # Read the Excel file into a pandas DataFrame
            df_raw = pd.read_excel(source_identifier)
            print(f"Original DataFrame shape: {df_raw.shape}")

            # Display the first few rows for debugging
            print("\nFirst 5 rows of the raw file:")
            for i in range(min(5, len(df_raw))):
                print(f"Row {i}: {df_raw.iloc[i].values}")

            # We want to skip the first 3 rows and use the 4th row as header
            # Read the excel file again but use skiprows to skip the first 3 rows
            # and header=0 to use the first row of the remaining data as header
            df = pd.read_excel(source_identifier, skiprows=3, header=0)
            print(f"\nDataFrame shape after skipping first 3 rows: {df.shape}")
            
        elif data_source == 'google_sheet':
            print(f"Reading Google Sheet with ID: {source_identifier}...")
            
            # Get the Google Sheet data
            sheet_values = get_google_sheet_data(source_identifier)
            if not sheet_values:
                print("Failed to retrieve data from Google Sheet.")
                return False
                
            # Convert to DataFrame
            df_raw = pd.DataFrame(sheet_values)
            print(f"Original DataFrame shape: {df_raw.shape}")
            
            # Display the first few rows for debugging
            print("\nFirst 5 rows of the raw file:")
            for i in range(min(5, len(df_raw))):
                print(f"Row {i}: {df_raw.iloc[i].values}")
                
            # Skip the first 3 rows (similar to Excel processing)
            if len(df_raw) <= 3:
                print("Google Sheet has fewer than 4 rows, cannot skip first 3 rows.")
                return False
                
            df = pd.DataFrame(sheet_values[3:])
            # Set the first row (index 0, which is the 4th row of the original data) as header
            if len(df) > 0:
                df.columns = df.iloc[0]
                df = df[1:]
                df.reset_index(drop=True, inplace=True)
            print(f"\nDataFrame shape after skipping first 3 rows: {df.shape}")
        else:
            print(f"Unsupported data source: {data_source}")
            return False
        
        # Display column headers
        print("\nColumn headers after skipping first 3 rows:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        # Clean up NaN column names
        # Replace NaN column names with 'Column_X'
        new_columns = []
        for i, col in enumerate(df.columns):
            if pd.isna(col) or col == '' or col is None:
                new_columns.append(f'Column_{i}')
            else:
                new_columns.append(col)
        
        df.columns = new_columns
        
        print("\nColumn headers after cleanup:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        # Define a more flexible column mapping with multiple potential matches for each field
        # The first match found will be used
        column_map_options = {
            'Title': ['Title', 'record.title', 'title'],
            'ObjectName': [
                'ObjectName', 'Accession Number', 'Local Identifier', 'localIdentifier', 
                'Record ID', 'ID', 'Object ID', 'Identifier', 'Number'
            ],
            'Restrictions': ['Restrictions', 'Use Restriction Status', 'Copyright', 'Rights'],
            'Scopenote': ['Scopenote', 'Scope and Content Note', 'Description', 'Caption'],
            'Source': ['Related Collection', 'Source', 'Collection', 'Archive'],
            'By-line': ['Source Photographer', 'Photographer', 'Creator', 'Author', 'Artist'],
            'By-lineTitle': ['Institutional Creator', 'Creator Role', 'Organization']
        }
        
        # Initialize the results dictionary
        column_map = {key: None for key in column_map_options}
        
        print("\nLooking for column matches...")
        
        # First pass: Look for exact matches
        for target_field, possible_matches in column_map_options.items():
            for match_option in possible_matches:
                if match_option in df.columns:
                    column_map[target_field] = match_option
                    print(f"✓ Found exact match for '{target_field}': '{match_option}'")
                    break
        
        # Second pass: For columns not found, try partial matches
        for target_field, possible_matches in column_map_options.items():
            if column_map[target_field] is None:
                for match_option in possible_matches:
                    for col in df.columns:
                        if match_option.lower() in col.lower():
                            column_map[target_field] = col
                            print(f"✓ Found partial match for '{target_field}': '{col}'")
                            break
                    if column_map[target_field] is not None:
                        break
        
        # Special handling for ObjectName if still not found - prioritize Accession Number
        if column_map['ObjectName'] is None:
            # First, check for an exact Accession Number column
            if 'Accession Number' in df.columns:
                column_map['ObjectName'] = 'Accession Number'
                print(f"✓ Using 'Accession Number' as ObjectName")
            else:
                # Otherwise look for similar columns
                for col in df.columns:
                    if 'accession' in col.lower() or 'number' in col.lower():
                        column_map['ObjectName'] = col
                        print(f"✓ Using '{col}' as ObjectName (based on column name)")
                    
                    # Special handling: If we're using Accession Number for ObjectName,
                    # we need to ensure it's properly renamed in later steps
                    if 'accession' in col.lower():
                        print(f"   Note: Will map '{col}' → 'ObjectName' in final output")
                    break
        
        # Final attempt: Look for anything that could be an identifier column
        if column_map['ObjectName'] is None:
            for col in df.columns:
                if 'id' in col.lower() or 'identifier' in col.lower() or 'number' in col.lower():
                    column_map['ObjectName'] = col
                    print(f"✓ Using '{col}' as ObjectName (based on column name pattern)")
                    break
                    
        # For any remaining columns, scan the data for likely matches
        # This helps identify columns based on their content
        if column_map['ObjectName'] is None:
            row_check_limit = min(5, len(df))
            print("\nSearching data for potential identifier columns...")
            for i, col in enumerate(df.columns):
                # Skip columns we've already mapped
                if col in column_map.values():
                    continue
                    
                # Look for columns with short values that could be identifiers
                for j in range(row_check_limit):
                    try:
                        cell_value = str(df.iloc[j, i])
                        # Look for patterns that suggest an identifier
                        if (len(cell_value) < 15 and 
                            (('-' in cell_value) or 
                             any(c.isdigit() for c in cell_value))):
                            print(f"Possible identifier in column {i}: '{col}' with value '{cell_value}'")
                            if column_map['ObjectName'] is None:
                                column_map['ObjectName'] = col
                                print(f"✓ Using '{col}' as ObjectName (based on data pattern)")
                                break
                    except:
                        pass  # Skip any errors when examining cells
                
                if column_map['ObjectName'] is not None:
                    break
        # Print the column mapping results with detailed information
        print("\nFinal column mapping found:")
        for key, value in column_map.items():
            if value:
                # Get a sample value from the column for verification
                try:
                    sample_value = df.iloc[0][value]
                    sample_str = str(sample_value) if len(str(sample_value)) < 50 else str(sample_value)[:47] + "..."
                    print(f"  ✓ {key} → {value} (sample: {sample_str})")
                except:
                    print(f"  ✓ {key} → {value}")
            else:
                print(f"  ✗ {key} → Not found")
        
        # Define required columns (must have these for successful processing)
        required_columns = ['Title', 'ObjectName']
        
        # Check if we're missing any required columns
        missing_required = [key for key in required_columns if column_map.get(key) is None]
        missing_other = [key for key, value in column_map.items() 
                         if value is None and key not in required_columns]
        
        if missing_required:
            print("\nERROR: The following required columns were not found:")
            for col in missing_required:
                print(f"  - {col}")
            print("\nProcessing cannot continue without these columns.")
            print("Please check your Excel file structure or choose another file.")
            return False
        
        if missing_other:
            print("\nWARNING: Some optional columns were not found:")
            for col in missing_other:
                print(f"  - {col}")
            print("Processing will continue, but these fields will be empty in the output.")
            
        # Display sample data for columns we're using
        print("\nSample data from identified columns (first row):")
        first_row = df.iloc[0]
        for key, col_name in column_map.items():
            if col_name is not None:
                try:
                    value = first_row[col_name]
                    print(f"  {key} ({col_name}): {value}")
                except:
                    print(f"  {key} ({col_name}): <error accessing value>")
        
        # Create the target header mapping - map from actual column names to our target names
        header_mapping = {}
        # Define the mapping from our internal names to target output names
        target_mapping = {
            'Title': 'Headline',
            'ObjectName': 'ObjectName',  # Already named correctly
            'Restrictions': 'CopyrightNotice',
            'Scopenote': 'Caption-Abstract',
            'Source': 'Source',  # Already named correctly
            'By-line': 'By-line',  # Already named correctly
            'By-lineTitle': 'By-lineTitle',  # Already named correctly
            # Add fallbacks for specific column types
            'Accession Number': 'ObjectName',  # Map Accession Number to ObjectName as fallback
            'ID': 'ObjectName',  # Map ID to ObjectName as fallback
            'Record ID': 'ObjectName',  # Map Record ID to ObjectName as fallback
            'Local Identifier': 'ObjectName'  # Map Local Identifier to ObjectName as fallback
        }
        
        # Build the mapping from actual column names to target names
        # Build the mapping from actual column names to target names
        for internal_name, actual_col in column_map.items():
            if actual_col:  # Only add to mapping if we found the column
                new_name = target_mapping.get(internal_name, internal_name)
                header_mapping[actual_col] = new_name
        
        # Add any date columns we want to preserve
        date_columns = ['Month', 'Day', 'Year']
        for date_col in date_columns:
            if date_col in df.columns:
                header_mapping[date_col] = date_col  # Keep the same name
        print("\nFinal header mapping to be applied:")
        for old, new in header_mapping.items():
            print(f"  {old} → {new}")
        
        # Rename the columns according to the mapping
        df = df.rename(columns=header_mapping)
        
        # Create a list of columns to keep (both renamed and important original columns)
        renamed_columns = list(header_mapping.values())
        
        # Print the renamed columns
        print("\nColumns after renaming:")
        for i, col in enumerate(df.columns):
            if col in renamed_columns:
                print(f"  {i}: {col} (renamed)")
            else:
                print(f"  {i}: {col}")
        
        # Filter the dataframe to only include non-null rows in important columns
        # Get a sample of the data to verify it looks correct
        print("\nSample of the data (first 3 rows):")
        print(df.head(3))
        
        # Remove rows that have NaN in all renamed columns (initial filtering)
        important_columns = renamed_columns
        df_filtered = df.dropna(subset=important_columns, how='all')
        print(f"\nInitial filtered DataFrame shape: {df_filtered.shape}")
        
        # Export to CSV with UTF-8 encoding
        print(f"Exporting to CSV: {output_file}...")
        
        # Option 1: Export all columns
        # df.to_csv(output_file, index=False, encoding='utf-8')
        
        # Option 2: Export only the renamed columns and other essential columns
        # Determine which columns to keep
        columns_to_keep = []
        
        # First, add all the renamed columns
        for col in renamed_columns:
            if col in df_filtered.columns:
                columns_to_keep.append(col)
        
        # Add any other important columns that might not have been renamed
        # For example, we might want to keep date information, accession numbers, etc.
        other_important_columns = ['Month', 'Day', 'Year', 'Accession Number', 'ID', 'Record ID']
        for col in other_important_columns:
            if col in df_filtered.columns:
                columns_to_keep.append(col)
        
        # Remove duplicates from columns_to_keep while preserving order
        columns_to_keep = list(dict.fromkeys(columns_to_keep))
        
        print(f"\nExporting {len(columns_to_keep)} columns to CSV:")
        for col in columns_to_keep:
            print(f"  - {col}")
        # Create a new DataFrame with only the columns we want to keep
        # Create a new DataFrame with only the columns we want to keep
        try:
            export_df = df_filtered[columns_to_keep].copy()
        except KeyError as e:
            # Handle case where a column is missing
            missing_col = str(e).strip("'")
            print(f"\nERROR: Required column '{missing_col}' not found in the data")
            print("Available columns:", sorted(df_filtered.columns.tolist()))
            print("\nPossible solutions:")
            print("1. Choose a different Excel file with the required columns")
            print("2. Modify the script to use different column names for mapping")
            print("\nExport failed. Please check column mappings.")
            return False
        # Additional data cleaning and validation
        print("\nPerforming additional data cleaning and validation...")
        
        # 0. Print initial data quality statistics
        initial_row_count = len(export_df)
        print(f"Initial row count: {initial_row_count}")
        
        # Count rows with any data in key columns
        key_columns = {'Headline': 0, 'ObjectName': 0, 'Caption-Abstract': 0}
        for col in key_columns:
            if col in export_df.columns:
                key_columns[col] = export_df[col].notna().sum()
                print(f"Rows with {col}: {key_columns[col]}")
        
        # 1. Remove rows where essential fields are empty
        print("\nRemoving rows with missing essential fields...")
        essential_fields = ['Headline', 'ObjectName']
        # Use list comprehension with explicit comparison to avoid Series operations
        essential_fields_present = [col for col in essential_fields if col in export_df.columns.tolist()]
        
        if len(essential_fields_present) == 0:
            print("Error: No essential fields found in the data")
            return False
            
        if len(essential_fields_present) > 0:
            original_row_count = len(export_df)
            # Use how='any' to remove rows where ANY of the essential fields are missing
            export_df = export_df.dropna(subset=essential_fields_present, how='any')
            removed_rows = original_row_count - len(export_df)
            print(f"Removed {removed_rows} rows where any of these fields were empty: {', '.join(essential_fields_present)}")
            print(f"Remaining rows: {len(export_df)}")
        
        
        # 2. Clean up whitespace in text fields
        print("\nCleaning text fields...")
        # Process each column individually to avoid Series-wide operations
        for col in export_df.columns:
            if is_string_column(export_df[col]):  # Only process string columns
                try:
                    print(f"  Cleaning column: {col}...")
                    
                    # Create a new column to avoid modifying during iteration
                    cleaned_values = []
                    
                    # Process each value individually to avoid Series evaluation
                    for i in range(len(export_df)):
                        # Get the value safely using .iloc
                        value = export_df.iloc[i][col]
                        
                        # Handle null values properly
                        if pd.isna(value) or value is None:
                            cleaned_values.append(pd.NA)
                        # Handle string values
                        elif isinstance(value, str):
                            cleaned = value.strip()
                            # Replace empty strings with NA
                            cleaned_values.append(pd.NA if cleaned == "" else cleaned)
                        # Keep non-string values as is
                        else:
                            cleaned_values.append(value)
                    
                    # Replace the column with cleaned values
                    export_df[col] = cleaned_values
                    print(f"  ✓ Cleaned text in column: {col}")
                    
                except Exception as e:
                    print(f"  ⚠ Error cleaning text in column {col}: {e}")
                    
        # After all text cleaning is done, process date columns
        try:
            print("\nConverting date fields to integers...")
            date_columns = ['Month', 'Day', 'Year']
            
            # Get available columns as a list to avoid Series operations
            available_columns = export_df.columns.tolist()
            
            # Process each date column individually and row by row
            for col in date_columns:
                # Check if column exists using list membership 
                if col in available_columns:
                    try:
                        print(f"  Processing date column: {col}...")
                        
                        # Create a new list to store converted values
                        converted_dates = []
                        
                        # Process each row individually to avoid Series operations
                        row_count = len(export_df)
                        for idx in range(row_count):
                            try:
                                # Get the value safely using .iloc and extract scalar value
                                val = export_df.iloc[idx][col]
                                
                                # Check for null/empty values - use scalar comparison
                                if pd.isna(val) or val is None:  # Handles scalar value
                                    converted_dates.append(pd.NA)
                                    continue
                                
                                # Handle string values
                                if isinstance(val, str):
                                    if val.strip() == "":
                                        converted_dates.append(pd.NA)
                                        continue
                                        
                                    # Try to convert string to number
                                    try:
                                        num_val = float(val.strip())
                                        # Convert to integer if possible
                                        if num_val.is_integer():
                                            converted_dates.append(int(num_val))
                                        else:
                                            converted_dates.append(num_val)
                                    except ValueError:
                                        # Not a valid number
                                        converted_dates.append(pd.NA)
                                # Handle numeric values
                                elif isinstance(val, (int, float)):
                                    converted_dates.append(val)
                                else:
                                    # Other types - use NA
                                    converted_dates.append(pd.NA)
                            except Exception as e:
                                # If any error occurs for this row, use NA
                                print(f"  ⚠ Error processing date in row {idx}: {e}")
                                converted_dates.append(pd.NA)
                            
                        # Only replace the column if we processed all rows successfully
                        if len(converted_dates) == row_count:
                            # Replace the column with our processed values
                            export_df[col] = converted_dates
                            
                            # Try to convert to nullable integer type if possible
                            try:
                                export_df[col] = export_df[col].astype('Int64')
                                print(f"  ✓ Converted {col} to integer format")
                            except Exception as type_error:
                                print(f"  ⚠ Warning: Could not convert {col} to Int64: {str(type_error)}")
                                print(f"    Column '{col}' will remain as basic numeric type")
                        else:
                            print(f"  ⚠ Warning: Mismatch in row count for {col}, skipping conversion")
                            
                    except Exception as e:
                        print(f"  ⚠ Warning: Could not process date column '{col}': {str(e)}")
                        print(f"    Column '{col}' will remain in its original format")
        except Exception as date_error:
            print(f"  ⚠ Warning: Date conversion error: {str(date_error)}")
            print("    Continuing with export without date conversion")

        # Try to sort by ObjectName if it exists
        try:
            # First approach: Sort with NAs at the end using pandas defaults
            export_df = export_df.sort_values('ObjectName', na_position='last')
            print("✓ Successfully sorted data by ObjectName")
        except Exception as sort_error:
            print(f"  Warning: Simple sort failed: {str(sort_error)}")
            print("  Trying alternative sorting method...")
            try:
                # Second approach: Create a completely new sorting column to avoid modifying the original
                print("  Creating separate sorting column...")
                temp_df = export_df.copy()
                
                # Create a new column for sorting that won't affect the original data
                temp_df['_temp_sort_key'] = pd.Series(['' for _ in range(len(temp_df))], index=temp_df.index)
                
                # Process each row individually to avoid Series boolean operations
                for idx in temp_df.index:
                    val = temp_df.at[idx, 'ObjectName']
                    # Use pd.isna() for scalar values only
                    if pd.isna(val) or val is None:
                        temp_df.at[idx, '_temp_sort_key'] = 'ZZZZZZ'  # Place NAs at the end
                    else:
                        temp_df.at[idx, '_temp_sort_key'] = str(val).lower()  # Case-insensitive sort
                
                # Sort using the temporary column
                temp_df = temp_df.sort_values('_temp_sort_key')
                
                # Remove the temporary column and update the export dataframe
                temp_df = temp_df.drop(columns=['_temp_sort_key'])
                export_df = temp_df
                
                print("✓ Successfully sorted data using alternative method")
            except Exception as alt_error:
                print(f"  Warning: Alternative sort also failed: {str(alt_error)}")
                print("  Proceeding with unsorted data")
        except Exception as e:
            print(f"⚠ Warning: Could not sort by ObjectName: {str(e)}")
            print("  Processing will continue with unsorted data")
        
        # Print sample of cleaned data after all processing is complete
        print("\nSample of cleaned data (first 3 rows):")
        try:
            print(export_df.head(3).to_string())
        except Exception as sample_err:
            print(f"  Could not display sample data: {str(sample_err)}")
            print("  Continuing with export anyway...")
            
        # Export to CSV with UTF-8 encoding
        try:
            # Define a function to properly format each value in the dataframe
            def format_value(val):
                # Handle null values
                if val is None or (hasattr(pd, 'isna') and pd.isna(val)) or (hasattr(pd, 'isnull') and pd.isnull(val)):
                    return ""
                # Handle pd.NA explicitly
                if hasattr(pd, '_libs') and hasattr(pd._libs, 'missing') and hasattr(pd._libs.missing, 'NAType'):
                    if isinstance(val, pd._libs.missing.NAType):
                        return ""
                # Handle numeric values - convert to int if possible
                if isinstance(val, (int, float)):
                    try:
                        if val == int(val):  # Check if it's a whole number
                            return str(int(val))
                    except:
                        pass
                # Default case - convert to string
                return str(val)
            print("\nFormatting data for CSV export...")
            
            # Use a simplified, robust CSV export approach
            try:
                print("Exporting data to CSV...")
                import csv
                
                # Safely convert columns to list to avoid Series operations
                columns_list = export_df.columns.tolist()
                total_rows = len(export_df)
                
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header row
                    writer.writerow(columns_list)
                    
                    # Track successfully written rows
                    rows_written = 0
                    
                    # Process each row individually
                    for row_idx in range(total_rows):
                        try:
                            # Create a new row for this iteration
                            row_data = []
                            
                            # Process each column in the row
                            for col in columns_list:
                                try:
                                    # Get scalar value with iloc - safer than direct indexing
                                    val = export_df.iloc[row_idx][col]
                                    
                                    # Handle None values first (simple equality check)
                                    if val is None:
                                        row_data.append("")
                                        continue
                                    
                                    # Handle NA/NaN values safely using scalar operations
                                    try:
                                        if pd.isna(val):  # Works on scalar values
                                            row_data.append("")
                                            continue
                                    except:
                                        # If isna check fails, continue with the value
                                        pass
                                    
                                    # Process different value types
                                    if isinstance(val, (int, float)):
                                        # Numeric values - convert integers cleanly
                                        try:
                                            # Convert to float first to handle all numeric types
                                            float_val = float(val)
                                            int_val = int(float_val)
                                            
                                            # Check if it's effectively an integer (allowing for float precision)
                                            if abs(float_val - int_val) < 1e-10:
                                                row_data.append(str(int_val))
                                            else:
                                                row_data.append(str(float_val))
                                        except:
                                            # If conversion fails, use string representation
                                            row_data.append(str(val))
                                    elif isinstance(val, str):
                                        # String values - strip whitespace
                                        row_data.append(val.strip())
                                    else:
                                        # All other types - convert to string
                                        row_data.append(str(val))
                                except Exception as cell_err:
                                    # Cell-level error handling
                                    row_data.append("")
                                    print(f"  Note: Could not process cell [{row_idx}, {col}]: {str(cell_err)}")
                            
                            # Write the completed row
                            writer.writerow(row_data)
                            rows_written += 1
                            
                        except Exception as row_err:
                            # Row-level error handling
                            print(f"  Warning: Could not process row {row_idx}: {str(row_err)}")
                    
                    # Report success
                    if rows_written > 0:
                        print(f"✓ Successfully exported {rows_written} of {total_rows} rows to {output_file}")
                        return True
                    else:
                        print("✗ No rows were exported - check for data processing issues")
                        return False
                        
            except Exception as csv_err:
                print(f"CSV export failed: {str(csv_err)}")
                print("Trying emergency failsafe export method...")
                
                # Emergency failsafe method - direct text file writing
                try:
                    print("Attempting emergency failsafe export...")
                    
                    # Write directly to a text file as CSV
                    with open(output_file, 'w', encoding='utf-8') as f:
                        # Write header first as a comma-separated line
                        header_line = ','.join([str(col) for col in export_df.columns]) + '\n'
                        f.write(header_line)
                        
                        # Manual row-by-row processing
                        rows_written = 0
                        
                        for idx in range(len(export_df)):
                            try:
                                # Build the row as CSV data
                                cells = []
                                for col_idx, col in enumerate(export_df.columns):
                                    try:
                                        # Get value safely as scalar
                                        val = export_df.iat[idx, col_idx]
                                        
                                        # Format it for CSV - handle None first
                                        if val is None:
                                            cells.append('')
                                            continue
                                            
                                        # Check for NaN/NA values
                                        try:
                                            if pd.isna(val):
                                                cells.append('')
                                                continue
                                        except:
                                            # If isna check fails, continue with the value
                                            pass
                                            
                                        # Format and escape for CSV
                                        try:
                                            # Special handling for numeric values
                                            if isinstance(val, (int, float)):
                                                # Convert to int if it's a whole number
                                                float_val = float(val)
                                                int_val = int(float_val)
                                                if abs(float_val - int_val) < 1e-10:
                                                    str_val = str(int_val)
                                                else:
                                                    str_val = str(float_val)
                                            else:
                                                # String and other types
                                                str_val = str(val)
                                                
                                            # Escape quotes and add quotes around the value
                                            str_val = str_val.replace('"', '""')
                                            cells.append(f'"{str_val}"')
                                        except:
                                            # If conversion fails, add empty quoted string
                                            cells.append('""')
                                    except Exception as cell_err:
                                        # If cell access fails, use empty string
                                        cells.append('""')
                                        
                                # Join cells with commas and write the line
                                row_line = ','.join(cells) + '\n'
                                f.write(row_line)
                                rows_written += 1
                                
                            except Exception as row_err:
                                # Skip problematic rows but log the error
                                print(f"  Warning: Error processing row {idx}: {str(row_err)}")
                                continue
                                
                        # Report success after all rows are processed
                        print(f"Emergency export completed: {rows_written} rows written to {output_file}")
                        return True
                        
                except Exception as emergency_error:
                    print(f"Emergency export method failed: {str(emergency_error)}")
                    print(f"All export methods failed. Please check your data and try again.")
                    return False
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
    except Exception as outer_e:
        print(f"Unexpected error during processing: {str(outer_e)}")
        return False
    return False

if __name__ == "__main__":
    try:
        # Let the user select a data source
        data_source, source_identifier = select_excel_file()
        
        # Process the selected data source
        if data_source == 'excel':
            # Check if the selected Excel file exists
            if not os.path.exists(source_identifier):
                print(f"Error: {source_identifier} not found in the current directory.")
                sys.exit(1)
        
        # Process the selected data source
        success = process_data_source(data_source, source_identifier)
        
        if success:
            print("\n=================================")
            print("✓ Processing completed successfully!")
            print("=================================")
            
            # Optionally, display the first few rows of the output file
            try:
                result_df = pd.read_csv("export.csv")
                print("\nFirst 5 rows of the output CSV file:")
                print(result_df.head())
                print("\nYou can now use this CSV file for your metadata needs.")
            except Exception as e:
                print(f"Note: Could not display the CSV content: {str(e)}")
                print("The CSV file was still created successfully.")
        else:
            print("\n=================================")
            print("✗ Processing failed")
            print("=================================")
            print("Please check the error messages above and try again with a different file or format.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)
