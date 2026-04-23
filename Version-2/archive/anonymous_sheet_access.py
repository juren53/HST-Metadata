#!/usr/bin/env python3
"""
Anonymous Google Sheet Access Script

This script demonstrates how to access a Google Sheets document anonymously
(without authentication), assuming the sheet has been made public or published
to the web.

IMPORTANT: For this script to work, the Google Sheet MUST be either:
1. Published to the web, or
2. Shared publicly with "Anyone with the link" having "Viewer" access

HOW TO MAKE YOUR GOOGLE SHEET ACCESSIBLE:

Method 1 - Publish to the web (Preferred for this script):
1. Open your Google Sheet in a browser
2. Click File > Share > Publish to the web
3. Select the sheet you want to publish and format (CSV or web page)
4. Click Publish
5. Copy the link provided (or use your original sheet URL)

Method 2 - Share with anyone (Alternative):
1. Open your Google Sheet in a browser
2. Click the Share button in the top right
3. Click "Change to anyone with the link"
4. Make sure the permission is set to "Viewer"
5. Click "Done"

NOTE: This script attempts multiple methods to access the sheet:
- Using the published CSV export format
- Using the Google Sheets API v4 public endpoint

If your sheet is not properly shared, all methods will fail.
"""

import re
import sys
import json
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple, Union

import requests

# Try to import pandas if available for DataFrame output
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def extract_sheet_details(sheet_url: str) -> Tuple[str, str]:
    """
    Extract the spreadsheet ID and sheet ID (gid) from a Google Sheets URL.
    
    Args:
        sheet_url: The Google Sheets URL
        
    Returns:
        Tuple of (spreadsheet_id, sheet_gid)
        
    Raises:
        ValueError: If the URL format is invalid or IDs can't be extracted
    """
    # Extract spreadsheet ID (should be between /d/ and / or ? or #)
    spreadsheet_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', sheet_url)
    if not spreadsheet_id_match:
        raise ValueError("Invalid Google Sheets URL: Could not find spreadsheet ID")
    
    # Extract the ID and remove anything after a potential slash
    spreadsheet_id = spreadsheet_id_match.group(1).split('/')[0]
    
    # Extract gid from URL parameters
    parsed_url = urllib.parse.urlparse(sheet_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    # Look for gid in the query parameters
    gid = query_params.get('gid', ['0'])[0]
    
    # Also check for gid in the fragment (after #)
    if not gid or gid == '0':
        fragment_params = urllib.parse.parse_qs(parsed_url.fragment)
        if 'gid' in fragment_params:
            gid = fragment_params['gid'][0]
    
    return spreadsheet_id, gid


def get_sheet_as_csv(spreadsheet_id: str, gid: str) -> List[List[str]]:
    """
    Retrieve a Google Sheet as CSV using the public export URL.
    This requires the sheet to be published to the web.
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        gid: The specific sheet ID (gid parameter)
        
    Returns:
        List of rows, where each row is a list of cell values
        
    Raises:
        requests.RequestException: If the request fails
        ValueError: If the sheet is not accessible
    """
    # Construct the export URL for CSV format
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&id={spreadsheet_id}&gid={gid}"
    
    response = requests.get(export_url)
    
    # Check for successful response
    if response.status_code != 200:
        if response.status_code == 404:
            raise ValueError("Sheet not found or not published to the web")
        else:
            raise ValueError(f"Failed to access sheet: HTTP {response.status_code}")
    
    # Parse CSV content
    content = response.text
    
    # Simple CSV parsing (handles most cases)
    rows = []
    for line in content.splitlines():
        # Handle basic CSV format (doesn't handle all edge cases)
        # For more robust parsing, consider using the csv module
        if line:
            # Handle quoted values with commas inside them
            in_quotes = False
            current_field = ""
            row = []
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    row.append(current_field.strip('"'))
                    current_field = ""
                else:
                    current_field += char
            
            # Add the last field
            row.append(current_field.strip('"'))
            rows.append(row)
    
    return rows


def get_sheet_with_sheets_api(spreadsheet_id: str, sheet_range: str = "A1:Z1000") -> List[List[str]]:
    """
    Retrieve a Google Sheet using the Sheets API v4 public endpoint.
    This requires the sheet to be shared publicly with "Anyone with the link".
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        sheet_range: The range of cells to retrieve (default: A1:Z1000)
        
    Returns:
        List of rows, where each row is a list of cell values
        
    Raises:
        requests.RequestException: If the request fails
        ValueError: If the sheet is not accessible
    """
    # Construct the API URL for public access
    api_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_range}?key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM"
    
    response = requests.get(api_url)
    
    # Check for successful response
    if response.status_code != 200:
        if response.status_code == 403:
            raise ValueError("Sheet is not publicly accessible with the API key")
        elif response.status_code == 404:
            raise ValueError("Sheet not found or API key invalid")
        else:
            raise ValueError(f"Failed to access sheet via API: HTTP {response.status_code}")
    
    # Parse JSON response
    data = response.json()
    
    # Extract values
    if 'values' in data:
        return data['values']
    else:
        # Sheet might be empty or no data in the requested range
        return []


def print_sheet_data(data: List[List[str]], max_rows: int = 10):
    """
    Print sheet data in a formatted way.
    
    Args:
        data: List of rows to print
        max_rows: Maximum number of rows to print
    """
    if not data:
        print("No data found in the sheet.")
        return
    
    # Determine column widths for pretty printing
    col_widths = [max(len(str(row[i])) for row in data if i < len(row)) 
                 for i in range(max(len(row) for row in data))]
    
    # Print header
    if data:
        header = data[0]
        header_line = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(header) if i < len(col_widths))
        print(header_line)
        print("-" * len(header_line))
    
    # Print rows (limited to max_rows)
    for row in data[1:max_rows+1]:
        row_str = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row) if i < len(col_widths))
        print(row_str)
    
    # Indicate if more rows were truncated
    if len(data) > max_rows + 1:
        print(f"... and {len(data) - max_rows - 1} more rows")


def convert_to_dataframe(data: List[List[str]]) -> Any:
    """
    Convert sheet data to a pandas DataFrame if pandas is available.
    
    Args:
        data: List of rows where the first row is treated as headers
        
    Returns:
        pandas.DataFrame or None if pandas is not available
    """
    if not PANDAS_AVAILABLE or not data:
        return None
    
    headers = data[0]
    rows = data[1:]
    
    # Ensure all rows have the same length as the header
    rows_fixed = []
    for row in rows:
        # Extend short rows with empty strings
        if len(row) < len(headers):
            row = row + [''] * (len(headers) - len(row))
        # Truncate long rows
        elif len(row) > len(headers):
            row = row[:len(headers)]
        rows_fixed.append(row)
    
    return pd.DataFrame(rows_fixed, columns=headers)


def main():
    # Default URL from the query
    default_url = "https://docs.google.com/spreadsheets/d/1hnG1mav-ma1AWgexyJQoM_3at5QciLm78UNABHm4QVM/edit?gid=1068149081#gid=1068149081"
    
    # Get URL from command line if provided, otherwise use default
    sheet_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    print(f"=== Anonymous Google Sheet Access ===")
    print(f"Attempting to access: {sheet_url}")
    
    try:
        # Extract spreadsheet ID and gid
        spreadsheet_id, gid = extract_sheet_details(sheet_url)
        print(f"Extracted spreadsheet ID: {spreadsheet_id}")
        print(f"Sheet gid: {gid}")
        
        # Try different methods to access the sheet
        data = None
        errors = []
        
        # Method 1: Try to get the sheet as CSV (requires "Publish to web")
        print("\nMethod 1: Attempting to access as published CSV...")
        try:
            data = get_sheet_as_csv(spreadsheet_id, gid)
            print("✓ Success! Retrieved data using CSV export.")
        except Exception as e:
            errors.append(f"CSV method failed: {str(e)}")
            print(f"✗ Failed: {str(e)}")
        
        # Method 2: Try Google Sheets API v4 (requires "Anyone with the link")
        if data is None:
            print("\nMethod 2: Attempting to access using Sheets API v4...")
            try:
                data = get_sheet_with_sheets_api(spreadsheet_id)
                print("✓ Success! Retrieved data using Sheets API.")
            except Exception as e:
                errors.append(f"API method failed: {str(e)}")
                print(f"✗ Failed: {str(e)}")
        
        # Display the data if we got it
        if data:
            print("\n=== Sheet Data ===")
            print_sheet_data(data)
            
            # Convert to DataFrame if pandas is available
            if PANDAS_AVAILABLE:
                df = convert_to_dataframe(data)
                print("\n=== DataFrame ===")
                print(df.head())
                print("\nDataFrame shape:", df.shape)
        else:
            print("\n✗ All methods failed. Please ensure the Google Sheet is either:")
            print("  1. Published to the web (File > Share > Publish to the web)")
            print("  2. Shared with 'Anyone with the link' as a Viewer")
            print("\nErrors encountered:")
            for error in errors:
                print(f"- {error}")
    
    except ValueError as e:
        print(f"\n✗ Error: {str(e)}")
        print("Please check that the URL is a valid Google Sheets URL.")
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()

