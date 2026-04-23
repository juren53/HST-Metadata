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
    parts = url.split('/')
    for i, part in enumerate(parts):
        if part == 'd' and i+1 < len(parts):
            return parts[i+1]
    return None

def get_google_sheet_data(sheet_id, sheet_range=''):
    creds = authenticate_google_sheets()
    service = build('sheets', 'v4', credentials=creds)
    metadata = service.spreadsheets().get(spreadsheetId=sheet_id, fields="sheets.properties.title").execute()
    if not sheet_range:
        sheet_range = metadata['sheets'][0]['properties']['title']
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    return result.get('values', [])

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
                url = input("Enter Google Sheet URL: ")
                sheet_id = extract_sheet_id_from_url(url)
                if sheet_id:
                    return 'google_sheet', sheet_id
        except Exception:
            pass
        print("Invalid input. Try again.\n")

def clean_dataframe(df):
    df.columns = [str(c).strip() if c else f"Column_{i}" for i, c in enumerate(df.columns)]
    df = df.dropna(how='all')
    df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
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
        rows = values[4:]
        df = pd.DataFrame(rows, columns=headers)

    df = clean_dataframe(df)

    column_map = {
        'Headline': ['Title', 'record.title'],
        'ObjectName': ['ObjectName', 'Accession Number', 'Local Identifier'],
        'Caption-Abstract': ['Description', 'Scopenote'],
        'CopyrightNotice': ['Restrictions', 'Copyright'],
        'By-line': ['Photographer', 'Creator'],
        'By-lineTitle': ['Organization'],
        'Source': ['Collection', 'Source']
    }

    mapped = {}
    for key, options in column_map.items():
        for opt in options:
            matches = [c for c in df.columns if opt.lower() in c.lower()]
            if matches:
                mapped[key] = matches[0]
                break

    essential = ['Headline', 'ObjectName']
    for e in essential:
        if e not in mapped:
            print(f"Missing required field: {e}")
            return

    rename_map = {v: k for k, v in mapped.items()}
    df.rename(columns=rename_map, inplace=True)

    df = df.dropna(subset=essential, how='any')
    df.sort_values(by='ObjectName', na_position='last', inplace=True)

    columns_to_export = essential + [k for k in mapped if k not in essential]
    columns_to_export += [c for c in ['Month', 'Day', 'Year'] if c in df.columns]
    columns_to_export = list(dict.fromkeys(columns_to_export))

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
