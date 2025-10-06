#!/usr/bin/env python3
"""
Helper script to find 'Sample Related Collection Papers' data in the Google Sheet
"""
import os
import pandas as pd
import sys
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# === CONFIG ===
CLIENT_SECRET_FILE = 'client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token_sheets.pickle'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Target spreadsheet ID
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

def fetch_sheet_data():
    """Fetch data from Google Sheet and find sample related collection values"""
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata and first sheet title
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        first_sheet_title = spreadsheet['sheets'][0]['properties']['title']
        print(f"Accessing sheet: {first_sheet_title}")

        # Fetch all values from the first sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{first_sheet_title}"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in the sheet.")
            return None
            
        # Convert to DataFrame with maximum number of columns
        max_cols = max(len(row) for row in values)
        headers = values[0]
        if len(headers) < max_cols:
            headers.extend([f"Column_{i+1}" for i in range(len(headers), max_cols)])
        
        # Create DataFrame
        data = []
        for row in values[1:]:
            padded_row = row + [''] * (max_cols - len(row))
            data.append(padded_row)
        
        df = pd.DataFrame(data, columns=headers)
        
        # Search for "Sample Related Collection Papers ##" in all cells
        print("\nSearching for 'Sample Related Collection Papers ##' pattern in all cells...")
        
        import re
        pattern = re.compile(r'sample related collection papers\s*\d+', re.IGNORECASE)
        
        found_values = []
        for idx, row in df.iterrows():
            for col_name, cell_value in row.items():
                if isinstance(cell_value, str) and pattern.search(cell_value):
                    found_values.append({
                        'row_index': idx + 1,  # +1 to account for 0-based indexing
                        'column': col_name,
                        'value': cell_value
                    })
        
        # Print results
        if found_values:
            print(f"\nFound {len(found_values)} cells containing 'Sample Related Collection Papers':")
            for i, item in enumerate(found_values, 1):
                print(f"{i}. Row {item['row_index']}, Column '{item['column']}': '{item['value']}'")
        else:
            print("\nNo cells containing 'Sample Related Collection Papers' were found.")
        
        # Look for custodialHistoryNote column
        if 'custodialHistoryNote' in df.columns:
            print("\nChecking custodialHistoryNote column for values:")
            custodial_values = df['custodialHistoryNote'].dropna().unique()
            if len(custodial_values) > 0:
                print("Values found in custodialHistoryNote column:")
                for i, value in enumerate(custodial_values, 1):
                    if len(str(value)) > 100:
                        print(f"{i}. '{str(value)[:100]}...' (truncated)")
                    else:
                        print(f"{i}. '{value}'")
            else:
                print("No values found in custodialHistoryNote column.")

        # Look for _13 column which might contain Related Collection
        if '_13' in df.columns:
            print("\nChecking _13 column for values:")
            col13_values = df['_13'].dropna().unique()
            if len(col13_values) > 0:
                print("Values found in _13 column:")
                for i, value in enumerate(col13_values, 1):
                    if len(str(value)) > 100:
                        print(f"{i}. '{str(value)[:100]}...' (truncated)")
                    else:
                        print(f"{i}. '{value}'")
            else:
                print("No values found in _13 column.")
                
        # Look for any column with Related Collection in row 3
        print("\nChecking for columns with 'Related Collection' in row 3:")
        row3_index = 2  # 0-based indexing
        if len(df) > row3_index:
            for col_name, cell_value in df.iloc[row3_index].items():
                if isinstance(cell_value, str) and "related collection" in cell_value.lower():
                    print(f"Found 'Related Collection' in column '{col_name}' at row 3")
                    # Check values in this column
                    column_values = df[col_name].dropna().unique()
                    if len(column_values) > 0:
                        print(f"Values found in {col_name} column:")
                        for i, value in enumerate(column_values, 1):
                            if len(str(value)) > 100:
                                print(f"{i}. '{str(value)[:100]}...' (truncated)")
                            else:
                                print(f"{i}. '{value}'")
                    else:
                        print(f"No values found in {col_name} column.")
        
        return df
        
    except HttpError as error:
        print(f"HTTP Error: {error}")
        return None
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == "__main__":
    print("Fetching data from Google Sheet to find 'Sample Related Collection Papers'...")
    df = fetch_sheet_data()
    if df is not None:
        print("\nAnalysis complete.")
    else:
        print("\nFailed to analyze spreadsheet data.")

