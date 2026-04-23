#!/usr/bin/env python3
"""
Google Spreadsheet Downloader

This script downloads a Google Spreadsheet as an Excel file based on a provided URL.
It uses the Google Drive API with service account authentication.

Usage:
    python download_google_sheet.py <spreadsheet_url>
    python download_google_sheet.py <spreadsheet_url> -o <output_filename>
"""

import sys
import re
import os
import io
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError

def extract_spreadsheet_id(url):
    """Extract the spreadsheet ID from a Google Sheets URL."""
    # Pattern to match spreadsheet ID in Google Sheets URL
    pattern = r'spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    
    if not match:
        # Try alternate format
        pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheets URL. Could not extract spreadsheet ID.")


def get_service_account_credentials(credentials_path="credentials.json"):
    """
    Get service account credentials from the credentials.json file.
    
    Args:
        credentials_path (str): Path to the credentials JSON file
        
    Returns:
        The credentials object for the service account
    """
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        print(f"Error: Credentials file '{credentials_path}' not found.")
        sys.exit(1)
    
    try:
        # Verify that it's a service account key file
        with open(credentials_path, 'r') as f:
            import json
            creds_data = json.load(f)
            
            # Check if this is a service account key file
            if 'type' in creds_data and creds_data['type'] == 'service_account':
                # This is a service account key file
                pass
            else:
                # This is likely an OAuth client credentials file, not a service account
                print("Error: The credentials file is not a service account key file.")
                print("You need to create a service account in the Google Cloud Console and download its key.")
                print("See: https://cloud.google.com/iam/docs/creating-managing-service-accounts")
                sys.exit(1)
        
        # Define OAuth 2.0 scopes needed for Drive API
        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        
        # Create credentials from the service account file
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scopes=scopes)
        return credentials
    except json.JSONDecodeError:
        print(f"Error: '{credentials_path}' is not a valid JSON file.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        sys.exit(1)
def download_spreadsheet(url, output_path=None):
    """
    Download a Google Spreadsheet as an Excel file using service account authentication.
    
    Args:
        url (str): URL of the Google Spreadsheet
        output_path (str, optional): Path to save the Excel file. 
                                     If None, saves as downloaded_spreadsheet.xlsx in current directory.
    
    Returns:
        str: Path to the saved Excel file
    """
    try:
        # Extract spreadsheet ID from URL
        spreadsheet_id = extract_spreadsheet_id(url)
        print(f"Extracted spreadsheet ID: {spreadsheet_id}")
        
        # Set up authentication with service account
        credentials = get_service_account_credentials()
        
        # Build the Drive API service
        service = build('drive', 'v3', credentials=credentials)
        
        # Verify that we can access the Drive API
        try:
            # Try a simple API call to verify authentication
            service.files().get(fileId=spreadsheet_id).execute()
        except HttpError as e:
            if e.resp.status == 404:
                print(f"Error: File not found. Make sure the spreadsheet exists and is shared with the service account.")
                print(f"Service account email should be listed in the sharing settings of the Google Sheet.")
                sys.exit(1)
            elif e.resp.status in [401, 403]:
                print(f"Error: Authentication failed or insufficient permissions.")
                print(f"Make sure the service account has access to the spreadsheet.")
                sys.exit(1)
            else:
                raise
        
        # If output path is not specified, use a default name
        if output_path is None:
            output_path = "downloaded_spreadsheet.xlsx"
            
        print("Accessing spreadsheet...")
        
        # Request the file as an Excel file
        request = service.files().export_media(
            fileId=spreadsheet_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Download the file content
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        # Download the file in chunks
        done = False
        print("Downloading spreadsheet...")
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")
        
        # Save the file to disk
        fh.seek(0)
        with open(output_path, 'wb') as f:
            f.write(fh.getvalue())
        
        print(f"Successfully downloaded spreadsheet to: {output_path}")
        return output_path
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except HttpError as e:
        print(f"Error: Could not access spreadsheet. Make sure the spreadsheet exists and is shared with the service account.")
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line args and download process."""
    # Create argument parser
    parser = argparse.ArgumentParser(description="Download a Google Spreadsheet as an Excel file")
    parser.add_argument("url", nargs="?", 
                      default="https://docs.google.com/spreadsheets/d/1zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I/edit?gid=1418369420#gid=141836942",
                      help="URL of the Google Spreadsheet (default: specified URL)")
    parser.add_argument("-o", "--output", help="Output Excel file path (default: downloaded_spreadsheet.xlsx)")
    parser.add_argument("-c", "--credentials", default="credentials.json",
                      help="Path to the service account credentials file (default: credentials.json)")
    
    args = parser.parse_args()
    
    # Use the credentials file specified in the command line
    try:
        download_spreadsheet(args.url, args.output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
