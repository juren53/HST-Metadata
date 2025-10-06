#!/usr/bin/env python3

import pandas as pd
import sys
import os

# Add the current directory to the path so we can import g2c
sys.path.append('.')

# Import the functions we need from g2c
from g2c import fetch_sheet_data, clean_dataframe_encoding, DEFAULT_SPREADSHEET_ID

def test_title_data():
    """Test if title data exists in the dataframe."""
    
    print("Fetching data from Google Sheet...")
    df = fetch_sheet_data(DEFAULT_SPREADSHEET_ID)
    
    if df is None:
        print("Failed to fetch data")
        return
    
    print(f"DataFrame shape: {df.shape}")
    
    # Look for title column
    title_cols = [col for col in df.columns if 'title' in col.lower()]
    print(f"Title-related columns: {title_cols}")
    
    if 'title' in df.columns:
        print("\nFirst 10 values in 'title' column:")
        for i in range(min(10, len(df))):
            val = df.loc[i, 'title']
            print(f"Row {i}: {repr(val)}")
    
    # Check for Spanish/French/German test data
    print("\nLooking for test data with accented characters...")
    for col in df.columns:
        for i in range(len(df)):
            val = str(df.loc[i, col]) if pd.notna(df.loc[i, col]) else ""
            if any(char in val for char in ['ñ', 'é', 'ü', 'ç', 'á', 'í', 'ó']):
                print(f"Found accented text in column '{col}', row {i}: {repr(val)}")
            if any(pattern in val for pattern in ['Spanish', 'French', 'German', 'Valle', 'Mémorial', 'für']):
                print(f"Found test marker in column '{col}', row {i}: {repr(val)}")
    
    # Apply encoding cleaning and check again
    print("\nApplying encoding cleaning...")
    df_cleaned = clean_dataframe_encoding(df)
    
    if 'title' in df_cleaned.columns:
        print("\nFirst 10 values in cleaned 'title' column:")
        for i in range(min(10, len(df_cleaned))):
            val = df_cleaned.loc[i, 'title']
            print(f"Row {i}: {repr(val)}")

if __name__ == "__main__":
    test_title_data()
