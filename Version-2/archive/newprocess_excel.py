#!/usr/bin/env python3
"""
Cleaned-up version of process_excel.py
- Simplified logic
- Refactored redundancy
- Enhanced safety and structure
"""

import pandas as pd
import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def authenticate_google_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token_file:
            creds = Credentials.from_authorized_user_info(json.load(token_file))

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def extract_sheet_id_from_url(url):
    try:
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'd' and i+1 < len(parts):
                # Get the ID part and remove any additional parameters
                sheet_id = parts[i+1].split('?')[0].split('#')[0]
                if sheet_id:
                    return sheet_id
        raise ValueError("Could not find sheet ID in URL")
    except Exception as e:
        print("\nError: Invalid Google Sheet URL format.")
        print("Please ensure:")
        print("1. The URL is from a Google Sheet (not a Doc or other Google document)")
        print("2. The sheet is shared with viewing access")
        print("3. You've copied the entire URL from your browser")
        print("\nExample URL format:")
        print("https://docs.google.com/spreadsheets/d/[YOUR-SHEET-ID]/edit?usp=sharing")
        return None

def get_google_sheet_data(sheet_id, sheet_range=''):
    try:
        creds = authenticate_google_sheets()
        service = build('sheets', 'v4', credentials=creds)
        
        try:
            metadata = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties.title").execute()
        except HttpError as e:
            if "This operation is not supported for this document" in str(e):
                print("\nError: Cannot access the Google Sheet.")
                print("Please check:")
                print("1. The URL is from a Google Sheet (not a Doc or other Google document)")
                print("2. The sheet is shared with viewing access")
                print("3. You have the correct permissions to access the sheet")
                return []
            raise e

        if not sheet_range:
            sheet_range = metadata['sheets'][0]['properties']['title']
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, 
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("\nError: The sheet appears to be empty or inaccessible.")
            return []
            
        return values
    except HttpError as e:
        if "Requested entity was not found" in str(e):
            print("\nError: The Google Sheet could not be found.")
            print("Please check if the sheet ID is correct and the sheet is shared properly.")
        else:
            print(f"\nError accessing Google Sheet: {str(e)}")
        return []
    except Exception as e:
        print(f"\nUnexpected error while accessing Google Sheet: {str(e)}")
        return []

def select_data_source():
    while True:
        excel_files = [f for f in os.listdir() if f.endswith(('.xls', '.xlsx'))]
        print("Select a data source:")
        for i, f in enumerate(excel_files):
            print(f"{i+1}. {f}")
        print(f"{len(excel_files)+1}. Google Sheet (Enter URL)")

        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= len(excel_files):
                return 'excel', excel_files[choice-1]
            elif choice == len(excel_files) + 1:
                while True:
                    url = input("Enter Google Sheet URL: ")
                    sheet_id = extract_sheet_id_from_url(url)
                    if sheet_id:
                        return 'google_sheet', sheet_id
                    print("\nPlease try again or press Ctrl+C to exit.")
        except ValueError:
            print("Invalid input. Please enter a number.\n")
        except Exception as e:
            print(f"Error: {str(e)}\n")
        print("Invalid input. Try again.\n")

def clean_dataframe(df):
    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]
    
    # Drop completely empty rows
    df = df.dropna(how='all')
    
    # Clean string values
    for col in df.columns:
        if df[col].dtypes == object:  # Fix: changed df[col].dtype to df[col].dtypes
            df[col] = df[col].apply(lambda x: str(x).strip() if pd.notnull(x) else x)
    
    return df

def process_data(data_source, identifier, output_file="export.csv"):
    if data_source == 'excel':
        df = pd.read_excel(identifier, skiprows=3)
    else:
        values = get_google_sheet_data(identifier)
        if len(values) < 4:
            print("Insufficient data rows.")
            return

        headers = values[3]
        header_length = len(headers)

        # Process rows to match header length
        processed_rows = []
        for row in values[4:]:
            if row:  # Skip empty rows
                # If row is longer than headers, trim it
                if len(row) > header_length:
                    processed_row = row[:header_length]
                # If row is shorter than headers, pad with empty strings
                elif len(row) < header_length:
                    processed_row = row + [''] * (header_length - len(row))
                else:
                    processed_row = row
                processed_rows.append(processed_row)

        df = pd.DataFrame(processed_rows, columns=headers)

    # Clean up column names and remove empty columns
    df = clean_dataframe(df)
    
    # Remove columns that are entirely empty
    df = df.dropna(axis=1, how='all')
    
    # Convert all columns to string type for consistent handling
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    # Remove columns that contain only empty strings after conversion
    df = df.loc[:, ~df.apply(lambda x: x.str.strip().eq('').all())]

    column_map = {
        'Headline': ['Title', 'record.title'],
        'ObjectName': ['ObjectName', 'Accession Number', 'Local Identifier', 'NAID'],
        'Caption-Abstract': ['Description', 'Scopenote'],
        'CopyrightNotice': ['Restrictions', 'Copyright'],
        'By-line': ['Photographer', 'Creator', 'Source Photographer'],
        'By-lineTitle': ['Organization', 'Institutional Creator'],
        'Source': ['Collection', 'Source', 'Related Collection']
    }

    mapped = {}
    for key, options in column_map.items():
        for opt in options:
            matches = [c for c in df.columns if any(o.lower() in str(c).lower() for o in [opt, key])]
            if matches:
                mapped[key] = matches[0]
                break

    essential = ['Headline', 'ObjectName']
    missing = [e for e in essential if e not in mapped]
    if missing:
        print(f"Missing required fields: {', '.join(missing)}")
        print("Available columns:", ', '.join(df.columns))
        return

    rename_map = {v: k for k, v in mapped.items()}
    df.rename(columns=rename_map, inplace=True)

    # Keep only rows where at least one essential field has a non-empty value
    df = df.dropna(subset=essential, how='all')
    # Keep rows where at least one essential field has a non-empty value after stripping
    df = df[df[essential].apply(lambda x: x.apply(lambda y: str(y).strip() != '')).any(axis=1)]
    
    df.sort_values(by='ObjectName', na_position='last', inplace=True)

    # Determine columns to export: essential fields first, then mapped fields, then date fields
    columns_to_export = essential + [k for k in mapped if k not in essential]
    date_columns = [c for c in ['Month', 'Day', 'Year'] if c in df.columns]
    columns_to_export += date_columns
    
    # Remove duplicates while preserving order
    columns_to_export = list(dict.fromkeys(columns_to_export))
    
    # Export only non-empty rows
    df = df[columns_to_export]
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✓ Exported {len(df)} rows to {output_file}")

if __name__ == '__main__':
    try:
        source_type, identifier = select_data_source()
        process_data(source_type, identifier)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
