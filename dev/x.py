#!/usr/bin/env python3
"""
Google Sheets to Pandas DataFrame Script

This script accesses a specified Google Sheet and loads its data into a pandas DataFrame.
"""

import os
import sys
import pickle
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
SPREADSHEET_ID = '19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4'

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

def fetch_sheet_data(spreadsheet_id=SPREADSHEET_ID):
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
            
        # Create DataFrame, handling rows that might have fewer columns than headers
        max_cols = len(headers)
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

def main():
    """Main function to execute the script."""
    print("Fetching data from Google Sheet...")
    df = fetch_sheet_data()
    
    if df is not None:
        print("\nData loaded successfully!")
        print_dataframe_summary(df)
    else:
        print("\nFailed to load data from the Google Sheet.")
        print("Please check your authentication credentials and spreadsheet ID.")
        sys.exit(1)

if __name__ == "__main__":
    main()
