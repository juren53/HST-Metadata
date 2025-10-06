#!/usr/bin/env python3

import pandas as pd
import sys

# Import the functions we need from g2c
from g2c import fetch_sheet_data, DEFAULT_SPREADSHEET_ID

def find_content():
    """Find actual text content in the dataframe."""
    
    print("Fetching data from Google Sheet...")
    df = fetch_sheet_data(DEFAULT_SPREADSHEET_ID)
    
    if df is None:
        print("Failed to fetch data")
        return
    
    print(f"DataFrame shape: {df.shape}")
    
    # Look for rows with actual content (skipping header rows)
    print("\nLooking for rows with substantial text content...")
    
    text_columns = ['title', 'scopeAndContentNote', '_10', '_11', '_12']  # Common text fields
    
    for i in range(20, min(30, len(df))):  # Look at rows 20-30
        has_content = False
        row_content = []
        
        for col in df.columns:
            val = str(df.loc[i, col]) if pd.notna(df.loc[i, col]) else ""
            if len(val) > 10 and val.lower() not in ['nan', 'none', '']:
                has_content = True
                row_content.append(f"{col}: {repr(val[:100])}")
        
        if has_content:
            print(f"\nRow {i}:")
            for content in row_content:
                print(f"  {content}")

if __name__ == "__main__":
    find_content()
