#!/usr/bin/env python3
"""
Google Sheets to Pandas DataFrame Loader

This script loads data from a Google Spreadsheet into a pandas DataFrame.
It handles authentication with Google's APIs and provides multiple methods
to access spreadsheet data.

Usage:
    python load_sheet_to_pandas.py [options]

Options:
    --url, -u           : URL of the Google Spreadsheet
    --sheet, -s         : Specific sheet name to access
    --drive-first, -d   : Use Drive API first instead of Sheets API
    --open-browser, -o  : Open the spreadsheet URL in a browser
    --test, -t          : Run in test mode using known public spreadsheets
    --direct            : Try direct access for public spreadsheets
    --regenerate-token, -r : Force regeneration of the OAuth token

Access requirements:
    - The Google Spreadsheet must be accessible to your Google account
    - For private spreadsheets, you must have at least view access
    - For public spreadsheets, they must be shared with "Anyone with the link"

Common issues:
    - "File not found" errors usually indicate the spreadsheet doesn't exist or you don't have access
    - "This operation is not supported for this document" may indicate a non-standard Google Sheet
    - Permission issues may require regenerating the OAuth token with --regenerate-token
    - Some spreadsheets may require specific access methods depending on their sharing settings
"""

import os
import sys
import json
import pickle
import re
import requests
import subprocess
import webbrowser
import tempfile
import argparse
import io
import logging
import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# === CONFIG ===
CLIENT_SECRET_FILE = 'client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token_sheets.pickle'  # Using a different pickle file to avoid scope issues

# Define scopes - we'll need both Sheets and Drive API access
# For more information on OAuth scopes, see:
# https://developers.google.com/identity/protocols/oauth2/scopes
SHEETS_SCOPE = 'https://www.googleapis.com/auth/spreadsheets.readonly'  # Read-only access to Google Sheets
DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'  # Read-only access to Google Drive files
SCOPES = [SHEETS_SCOPE, DRIVE_SCOPE]  # Combined scopes for both APIs

# If you're having permission issues, you may need to regenerate your token
# using the --regenerate-token flag to ensure these scopes are included

# Fallback URL to known public Google Sheets (for testing)
FALLBACK_URL = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"

# Alternative public test sheets
PUBLIC_TEST_SHEETS = [
    # Google Sheets sample data - Class Data
    "https://docs.google.com/spreadsheets/d/1AgI2lUJY1jIayEMibCxJY68Cf5bqMGnAY6EIKOJFIVs/edit",
    # Another public sample sheet
    "https://docs.google.com/spreadsheets/d/1i_IchQZWe2BjNjpDjmJe2-vYJb2ME-X6a_WjL8CO1vM/edit"
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_credentials():
    """Get valid user credentials from storage or run the OAuth flow.
    
    Returns:
        Credentials, the obtained credentials.
    """
    credentials = None
    
    # Try to load credentials from the token pickle file
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            try:
                credentials = pickle.load(token)
                print("Loaded credentials from token file")
            except Exception as e:
                print(f"Error loading token file: {e}")
    
    # If no valid credentials available, run the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                print("Refreshed expired credentials")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                credentials = None
        
        # If still no valid credentials, run the flow
        if not credentials:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES)
                
                print("\n===== AUTHENTICATION REQUIRED =====")
                print("Please authenticate using your browser...")
                print("A browser window/tab should open automatically.")
                print("If not, please manually open the URL that will be displayed.")
                print("You'll need to sign in with a Google account that has access to the spreadsheet.")
                print("=====================================\n")
                
                credentials = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open(TOKEN_PICKLE_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
                print("Saved new credentials to token file")
                print("These credentials will be reused for future requests")
                print("If you experience permission issues, run with --regenerate-token")
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                raise
    
    return credentials

def check_token_scopes(credentials):
    """
    Check if the token has the necessary scopes for accessing Google Sheets.
    
    Args:
        credentials: Google OAuth credentials
        
    Returns:
        tuple: (is_valid, missing_scopes)
    """
    if not credentials:
        return False, SCOPES
    
    # Get the scopes that the credentials have
    token_scopes = getattr(credentials, 'scopes', [])
    if isinstance(token_scopes, str):
        token_scopes = [token_scopes]
    
    logger.info(f"Token has the following scopes: {token_scopes}")
    
    # Check if all required scopes are present
    missing_scopes = []
    for scope in SCOPES:
        if scope not in token_scopes:
            missing_scopes.append(scope)
    
    if missing_scopes:
        logger.warning(f"Token is missing these scopes: {missing_scopes}")
        return False, missing_scopes
    
    return True, []

def detect_file_type(url):
    """
    Detect if a URL is for a Google Sheet or another file type like Excel.
    
    Args:
        url: The URL to check
        
    Returns:
        str: 'sheet', 'excel', or 'unknown'
    """
    # Check for Excel file extensions
    excel_patterns = [r'\.xlsx$', r'\.xls$', r'\.xlsm$', r'\.xlsb$', r'format=xlsx', r'exportFormat=xlsx']
    
    for pattern in excel_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            logger.info(f"URL appears to be for an Excel file: {url}")
            return 'excel'
    
    # Check for Google Sheets URL patterns
    if 'docs.google.com/spreadsheets' in url:
        logger.info(f"URL appears to be for a Google Sheet: {url}")
        return 'sheet'
    
    logger.info(f"Unable to determine file type for URL: {url}")
    return 'unknown'

def extract_spreadsheet_info(spreadsheet_url):
    """
    Extract the spreadsheet ID and GID from a Google Sheets URL.
    Handles various URL formats including:
    - Standard: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit?gid=GID
    - With export: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/export?format=xlsx
    - With share: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/view?usp=sharing
    - With direct path: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=GID
    - With unusual structures: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/anythingelse
    
    Args:
        spreadsheet_url: URL of the Google Spreadsheet
        
    Returns:
        tuple: (spreadsheet_id, gid) where gid might be None if not specified
    """
    logger.info(f"Extracting spreadsheet info from URL: {spreadsheet_url}")
    
    # Check if this might be an Excel file URL instead of a Sheet
    file_type = detect_file_type(spreadsheet_url)
    if file_type == 'excel':
        logger.warning("This appears to be an Excel file URL, not a Google Sheet URL.")
        logger.warning("Will attempt to process as a Google Sheet, but this may fail.")
    
    # Handle different URL patterns for the spreadsheet ID
    # Pattern 1: Standard URL format
    standard_match = re.search(r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9_-]+)', spreadsheet_url)
    
    # Pattern 2: Alternative format with different structure
    alt_match = re.search(r'spreadsheets/d/([a-zA-Z0-9_-]+)', spreadsheet_url)
    
    # Pattern 3: Just the ID itself (in case someone pastes just the ID)
    if not standard_match and not alt_match and len(spreadsheet_url.strip()) > 25:
        # If it's just the ID (not a URL), use it directly
        spreadsheet_id = spreadsheet_url.strip()
        logger.info(f"Using directly provided spreadsheet ID: {spreadsheet_id}")
    elif standard_match:
        spreadsheet_id = standard_match.group(1)
    elif alt_match:
        spreadsheet_id = alt_match.group(1)
    else:
        raise ValueError(
            "Invalid Google Sheets URL or ID. Expected format: "
            "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/... "
            "or just the SPREADSHEET_ID itself."
        )
    
    # Aggressively clean up the spreadsheet ID
    # First split by common delimiters
    spreadsheet_id = spreadsheet_id.split('/')[0].split('?')[0].split('#')[0]
    
    # Remove any special characters or whitespace
    spreadsheet_id = spreadsheet_id.strip()
    
    # Some spreadsheet IDs have additional formatting issues
    # Specifically handle potential issues with the ID format from the original URL
    if 'zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I' in spreadsheet_id:
        # This appears to be the problematic ID that's failing with "File not found"
        # There might be hidden characters or formatting issues
        logger.warning("Detected potentially problematic spreadsheet ID")
        logger.warning("Original ID: " + repr(spreadsheet_id))
        
        # Try to create a cleaned version by extracting only allowed characters
        clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', spreadsheet_id)
        logger.warning(f"Cleaned ID: {clean_id}")
        
        if clean_id != spreadsheet_id:
            logger.warning("Spreadsheet ID was cleaned - removed invalid characters")
            spreadsheet_id = clean_id
    
    logger.info(f"Final spreadsheet ID after cleaning: {spreadsheet_id}")
    
    # Extract GID if available using various patterns
    gid = None
    
    # Pattern 1: Standard gid parameter
    gid_match = re.search(r'[?&]gid=(\d+)', spreadsheet_url)
    if gid_match:
        gid = gid_match.group(1)
    
    # Pattern 2: Hash-based gid (used in some URLs)
    if not gid:
        hash_gid_match = re.search(r'#gid=(\d+)', spreadsheet_url)
        if hash_gid_match:
            gid = hash_gid_match.group(1)
    
    return spreadsheet_id, gid

def check_url_accessibility(url):
    """
    Check if a URL is publicly accessible by making a simple HTTP request.
    
    Args:
        url: The URL to check
        
    Returns:
        tuple: (is_accessible, message)
    """
    try:
        logger.info(f"Checking URL accessibility: {url}")
        
        # Add a User-Agent header to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.head(url, timeout=5, headers=headers)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("URL is directly accessible")
            return True, "URL is accessible"
        elif response.status_code == 302 or response.status_code == 303:
            logger.info(f"URL redirects (status code: {response.status_code}), which is normal for Google Docs")
            # Try to follow the redirect to see where it leads
            try:
                redirect_response = requests.get(url, timeout=5, headers=headers, allow_redirects=True)
                logger.info(f"Redirect final status code: {redirect_response.status_code}")
                if redirect_response.status_code == 200:
                    return True, "URL is accessible after redirect"
                else:
                    return False, f"URL redirected but final destination returned status code: {redirect_response.status_code}"
            except requests.RequestException as e:
                logger.warning(f"Error following redirect: {e}")
                # Still consider it potentially accessible since initial redirect is normal
                return True, f"URL redirects but couldn't follow: {e}"
        else:
            logger.warning(f"URL returned status code: {response.status_code}")
            return False, f"URL returned status code: {response.status_code}"
    except requests.RequestException as e:
        logger.warning(f"Error accessing URL: {e}")
        return False, f"Error accessing URL: {e}"

def verify_google_sheet_url(url):
    """
    Verify if a URL is a valid and accessible Google Sheet.
    
    Args:
        url: The URL to check
        
    Returns:
        bool: True if the URL appears to be a valid Google Sheet, False otherwise
    """
    logger.info(f"Verifying if URL is a valid Google Sheet: {url}")
    
    # First check if the URL is in the correct format
    if 'docs.google.com/spreadsheets' not in url and not url.strip().isalnum():
        logger.warning("URL does not appear to be a Google Sheet URL")
        return False
    
    # Check if the URL is accessible
    is_accessible, message = check_url_accessibility(url)
    if not is_accessible:
        logger.warning(f"URL is not accessible: {message}")
        return False
    
    logger.info(f"URL appears to be accessible: {message}")
    return True

def try_open_in_browser(url):
    """
    Attempts to open the URL in a web browser.
    """
    try:
        print(f"\nAttempting to open URL in your default browser: {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Failed to open browser: {e}")
        return False

def get_sheet_data(service, spreadsheet_id, gid=None):
    """
    Retrieve data from a Google Spreadsheet using various fallback methods.
    
    Args:
        service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        gid: Optional sheet ID (gid parameter)
        
    Returns:
        DataFrame: Pandas DataFrame containing the sheet data
    """
    # Define common fallback ranges to try for direct data access
    fallback_ranges = [
        "",  # Empty range retrieves all data from first sheet
        "A1:Z1000",  # Try without sheet name
        "Sheet1!A1:Z1000",  # Common default sheet name
        "'Sheet 1'!A1:Z1000",  # Sheet name with spaces
        "Data!A1:Z1000",  # Another common sheet name
        "'Sheet1'!A:Z",  # All columns, all rows in Sheet1 
        "A:Z",  # All columns, all rows in default sheet
    ]
    
    # If we have a gid but no sheet name yet, add it to our fallback ranges
    if gid:
        fallback_ranges.insert(0, f"gid={gid}!A1:Z1000")  # Try with gid as sheet name (might not work)
    
    try:
        # Try direct data access first - this is the most reliable approach for non-standard sheets
        print("Attempting direct data access first (most reliable for non-standard sheets)...")
        result = None
        successful_range = None
        
        # Try each fallback range until one works
        for fallback_range in fallback_ranges:
            try:
                print(f"Trying range: '{fallback_range or '[default range]'}'")
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=fallback_range
                ).execute()
                successful_range = fallback_range or "[default range]"
                print(f"Successfully accessed data with range: {successful_range}")
                break  # Exit the loop if successful
            except HttpError as e:
                if "Invalid range" in str(e) or "Unable to parse range" in str(e):
                    print(f"Range '{fallback_range}' not valid, trying next...")
                    continue
                elif "not supported for this document" in str(e):
                    print("Warning: This document doesn't support standard Sheets API operations.")
                    print("Will try alternative methods...")
                    raise ValueError("Standard access not supported")
                else:
                    # Re-raise other errors
                    raise
        
        # Process the data from either approach
        values = result.get('values', [])
        
        if not values:
            raise ValueError("No data found in the sheet. The sheet may be empty.")
        
        # Convert to pandas DataFrame
        # Handle case where the header row might be missing or incomplete
        if len(values) == 1:
            # Only one row, assume it's headers
            print("Warning: Only one row found. Treating it as headers with no data.")
            columns = values[0]
            df = pd.DataFrame(columns=columns)
        else:
            # Multiple rows - use first as headers
            headers = values[0]
            
            # Make sure we have unique column names (pandas requirement)
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
            
            # Create DataFrame
            data_rows = values[1:]
            
            # Handle rows that might have fewer columns than the header
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
        if 'not found' in str(error).lower():
            raise ValueError(f"Spreadsheet not found. Please verify the ID and your access permissions.")
        elif 'permission' in str(error).lower():
            raise ValueError(f"Permission denied. Make sure you have access to this spreadsheet.")
        elif 'not supported for this document' in str(error).lower():
            raise ValueError(
                "This document ID exists but doesn't seem to be a standard Google Sheet. "
                "It might be a Google Doc or another type of file. "
                "Please verify the URL is for a Google Spreadsheet."
            )
        else:
            raise ValueError(f"Error accessing spreadsheet: {error}")
    
    except Exception as error:
        raise ValueError(f"Unexpected error: {error}")

def get_drive_document_info(drive_service, doc_id):
    """
    Get information about a document from the Drive API.
    
    Args:
        drive_service: Google Drive API service instance
        doc_id: ID of the document
        
    Returns:
        dict: Document metadata or None if not found
    """
    try:
        file_metadata = drive_service.files().get(
            fileId=doc_id, 
            fields="id,name,mimeType,createdTime,modifiedTime,version,webViewLink,exportLinks"
        ).execute()
        
        return file_metadata
    except HttpError as error:
        print(f"Error getting file metadata from Drive API: {error}")
        return None

def export_drive_file(drive_service, doc_id, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
    """
    Export a Drive file to a specified format.
    
    Args:
        drive_service: Google Drive API service instance
        doc_id: ID of the document
        mime_type: MIME type to export to (default is Excel format)
        
    Returns:
        BytesIO: File data as a BytesIO object or None if export fails
    """
    try:
        # First check if the file can be exported to the desired format
        file_metadata = drive_service.files().get(
            fileId=doc_id, 
            fields="exportLinks"
        ).execute()
        
        export_links = file_metadata.get('exportLinks', {})
        
        # If the requested mime type isn't available, try to find an alternative
        if mime_type not in export_links:
            print(f"Export format {mime_type} not available for this document.")
            print("Available export formats:")
            for available_mime in export_links:
                print(f"- {available_mime}")
            
            # Try to find a suitable alternative
            if "text/csv" in export_links:
                mime_type = "text/csv"
                print(f"Using CSV format instead: {mime_type}")
            elif "application/pdf" in export_links:
                mime_type = "application/pdf"
                print(f"Using PDF format instead: {mime_type}")
            elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in export_links:
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                print(f"Using Excel format: {mime_type}")
            elif export_links:
                # Use the first available format if none of the preferred formats are available
                mime_type = list(export_links.keys())[0]
                print(f"Using available format: {mime_type}")
            else:
                print("No export formats available for this document.")
                return None
        
        # Create a BytesIO object to store the downloaded file
        file_data = io.BytesIO()
        
        # Export the file
        request = drive_service.files().export_media(fileId=doc_id, mimeType=mime_type)
        downloader = MediaIoBaseDownload(file_data, request)
        
        # Download the file
        done = False
        print("Exporting document...")
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")
        
        # Reset the file pointer to the beginning of the file
        file_data.seek(0)
        
        return file_data, mime_type
    
    except HttpError as error:
        print(f"Error exporting file: {error}")
        return None, None

def load_data_from_export(file_data, mime_type):
    """
    Load data from an exported file into a pandas DataFrame.
    
    Args:
        file_data: BytesIO object containing the file data
        mime_type: MIME type of the exported file
        
    Returns:
        DataFrame: Pandas DataFrame containing the data
    """
    try:
        print(f"Loading data from exported file (format: {mime_type})...")
        
        if mime_type == "text/csv":
            # Load CSV data
            return pd.read_csv(file_data)
            
        elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            # Load Excel data
            return pd.read_excel(file_data)
        
        elif mime_type == "application/pdf":
            # PDFs are more complex - we'd need additional libraries like tabula-py
            # This is a simplified demonstration
            print("PDF format detected. PDF parsing requires additional libraries.")
            print("Install tabula-py for PDF table extraction.")
            return None
        
        else:
            print(f"Unsupported export format: {mime_type}")
            return None
            
    except Exception as e:
        print(f"Error loading data from export: {e}")
        print(f"Error loading data from export: {e}")
        return None

def access_public_sheet(sheet_id, api_key=None):
    """
    Access a public Google Sheet using a more direct approach.
    This method uses the public sheets API endpoint which works for publicly shared sheets.
    
    Args:
        sheet_id: ID of the public spreadsheet
        api_key: Optional API key (not required for public sheets)
        
    Returns:
        DataFrame: Pandas DataFrame containing the sheet data or None if failed
    """
    try:
        # Construct the public sheets API URL
        # This endpoint works for sheets that are publicly shared with "Anyone with the link"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Sheet1"
        if api_key:
            url += f"?key={api_key}"
        
        logger.info(f"Attempting to access public sheet directly: {url}")
        
        # Add headers to make the request look like a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Send the request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            values = data.get('values', [])
            
            if values:
                # Convert to DataFrame
                if len(values) > 1:
                    df = pd.DataFrame(values[1:], columns=values[0])
                else:
                    df = pd.DataFrame(columns=values[0] if values else [])
                
                logger.info("Successfully accessed public sheet directly")
                return df
            else:
                logger.warning("No data found in public sheet")
                return None
        else:
            logger.warning(f"Failed to access public sheet. Status code: {response.status_code}")
            logger.warning(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error accessing public sheet: {e}")
        return None

def test_authentication():
    """
    Test if authentication is working by attempting to access a known public sheet.
    
    Returns:
        bool: True if authentication works, False otherwise
    """
    try:
        logger.info("Testing authentication with a public test sheet")
        
        # Get credentials
        credentials = get_credentials()
        if not credentials:
            logger.error("Failed to get credentials")
            return False
        
        # Check token scopes
        has_scopes, missing_scopes = check_token_scopes(credentials)
        if not has_scopes:
            logger.warning(f"Token missing scopes: {missing_scopes}")
            logger.warning("Will attempt to proceed anyway")
        
        # Build the Sheets API service
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        # Use the fallback URL
        sheet_id = extract_spreadsheet_info(FALLBACK_URL)[0]
        
        # Try to access basic metadata
        try:
            metadata = sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id,
                fields="spreadsheetId,properties.title"
            ).execute()
            
            logger.info(f"Successfully authenticated and accessed sheet: {metadata.get('properties', {}).get('title')}")
            return True
            
        except HttpError as e:
            logger.error(f"Error accessing test sheet: {e}")
            
            # Try another public test sheet
            for test_url in PUBLIC_TEST_SHEETS:
                logger.info(f"Trying alternative public test sheet: {test_url}")
                test_id = extract_spreadsheet_info(test_url)[0]
                
                try:
                    metadata = sheets_service.spreadsheets().get(
                        spreadsheetId=test_id,
                        fields="spreadsheetId,properties.title"
                    ).execute()
                    
                    logger.info(f"Successfully authenticated and accessed sheet: {metadata.get('properties', {}).get('title')}")
                    return True
                except HttpError as e2:
                    logger.error(f"Error accessing alternative test sheet: {e2}")
            
            return False
        
    except Exception as e:
        logger.error(f"Error testing authentication: {e}")
        return False

def load_spreadsheet_to_dataframe(spreadsheet_url, sheet_name=None, use_drive_api=False):
    """
    Main function to load a Google Spreadsheet into a pandas DataFrame.
    
    Args:
        spreadsheet_url: URL of the Google Spreadsheet
        sheet_name: Optional name of the sheet to load (overrides GID if provided)
        use_drive_api: Whether to use Drive API first instead of Sheets API
        
    Returns:
        DataFrame: Pandas DataFrame containing the sheet data
    """
    try:
        # Extract spreadsheet ID and GID from URL
        spreadsheet_id, gid = extract_spreadsheet_info(spreadsheet_url)
        print(f"Extracted spreadsheet ID: {spreadsheet_id}")
        if gid:
            print(f"Extracted GID: {gid}")
        if sheet_name:
            print(f"Using specified sheet name: {sheet_name}")
        
        # Get credentials and build the API services
        credentials = get_credentials()
        if not credentials:
            raise ValueError("Authentication failed. Unable to proceed.")
        # Build both Sheets and Drive API services
        sheets_service = build('sheets', 'v4', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Get document info from Drive API
        print("Getting document information from Drive API...")
        file_info = get_drive_document_info(drive_service, spreadsheet_id)
        
        if file_info:
            print("\n=== Document Information ===")
            print(f"Name: {file_info.get('name', 'Unknown')}")
            print(f"MIME Type: {file_info.get('mimeType', 'Unknown')}")
            print(f"Created: {file_info.get('createdTime', 'Unknown')}")
            print(f"Last Modified: {file_info.get('modifiedTime', 'Unknown')}")
            print(f"Web View Link: {file_info.get('webViewLink', 'Unknown')}")
            
            # Check if this is actually a spreadsheet
            mime_type = file_info.get('mimeType', '')
            is_google_sheet = mime_type == 'application/vnd.google-apps.spreadsheet'
            
            if not is_google_sheet:
                print(f"\nWarning: This document is not a standard Google Sheet. MIME type: {mime_type}")
                if 'document' in mime_type:
                    print("This appears to be a Google Document, not a spreadsheet.")
                elif 'presentation' in mime_type:
                    print("This appears to be a Google Presentation, not a spreadsheet.")
                elif 'form' in mime_type:
                    print("This appears to be a Google Form, not a spreadsheet.")
                print("Will attempt to export and convert it.")
        else:
            print("Warning: Could not get document information from Drive API.")
            print("Will attempt to access document directly.")
        
        # Try different approaches based on parameters
        df = None
        
        # If Drive API first is requested or if we know it's not a Sheet
        if use_drive_api or (file_info and not is_google_sheet):
            print("\nAttempting to export document via Drive API...")
            file_data, mime_type = export_drive_file(drive_service, spreadsheet_id)
            
            if file_data:
                df = load_data_from_export(file_data, mime_type)
                if df is not None:
                    print("Successfully loaded data via Drive API export.")
                    return df
                else:
                    print("Failed to load data from Drive API export. Trying Sheets API...")
            else:
                print("Failed to export document via Drive API. Trying Sheets API...")
        
        # Try Sheets API approach if Drive API didn't work or wasn't used first
        print("\nAttempting to access spreadsheet data via Sheets API...")
        
        # If sheet_name was provided, use it instead of handling GID
        if sheet_name:
            # Try to get sheet data with specific sheet name
            try:
                print(f"Requesting data from sheet: '{sheet_name}'")
                result = sheets_service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=sheet_name
                ).execute()
                
                values = result.get('values', [])
                if values:
                    # Convert to pandas DataFrame
                    if len(values) > 1:
                        df = pd.DataFrame(values[1:], columns=values[0])
                    else:
                        df = pd.DataFrame(columns=values[0])
                    
                    print(f"Successfully accessed data from sheet: '{sheet_name}'")
                    return df
                else:
                    print(f"No data found in sheet: '{sheet_name}'")
            except HttpError as e:
                print(f"Error accessing sheet '{sheet_name}': {e}")
                print("Trying standard approach...")
        
        # Use standard approach with GID
        df = get_sheet_data(sheets_service, spreadsheet_id, gid)
        
        return df
        
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("\n===== TROUBLESHOOTING TIPS =====")
        print("1. Check if the URL is for a Google Spreadsheet (not a Google Doc, Form, etc.)")
        print("2. Ensure you have permission to access this spreadsheet")
        print("   - The spreadsheet must be shared with your Google account")
        print("   - For public sheets, it must be shared with 'Anyone with the link'")
        print("3. The spreadsheet might be in a non-standard format or might be corrupted")
        print("4. Try opening the spreadsheet in your browser to verify it exists and you can access it")
        print(f"   URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        print("\n5. Common error causes and solutions:")
        print("   - 'File not found': The spreadsheet ID is incorrect or you don't have access")
        print("   - 'Not supported for this document': The URL might be for a different type of Google document")
        print("   - 'Permission denied': You need to regenerate your OAuth token (use --regenerate-token)")
        print("   - 'Invalid range': The sheet name or range might be incorrect (try specifying with --sheet)")
        print("\n6. Try running with different options:")
        print("   - Use --test to verify authentication with a known public sheet")
        print("   - Use --direct to try accessing the sheet as a public resource")
        print("   - Use --drive-first to prioritize Drive API for accessing the document")
        print("   - Use --regenerate-token to create a new OAuth token")
        print("=====================================\n")
        return None
        
    except Exception as e:
        print(f"Unexpected error loading spreadsheet: {e}")
        import traceback
        print(traceback.format_exc())
        return None
def main():
    """
    Main function to parse arguments and run the script.
    """
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Load data from a Google Spreadsheet into a pandas DataFrame.',
        epilog="""
Examples:
  python load_sheet_to_pandas.py --url "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
  python load_sheet_to_pandas.py --test  # Test with a known public spreadsheet
  python load_sheet_to_pandas.py --regenerate-token  # Force new authentication
  python load_sheet_to_pandas.py --direct  # Try direct access for public spreadsheets

This script supports multiple methods for accessing Google Sheets and will
attempt various fallback approaches if the primary access method fails.
"""
    )
    
    # Default URL from the task
    default_url = "https://docs.google.com/spreadsheets/d/1zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I/edit?gid=1418369420"
    
    # Add arguments
    parser.add_argument(
        '--url', '-u', 
        default=default_url,
        help=f'URL of the Google Spreadsheet (default: {default_url})'
    )
    parser.add_argument(
        '--sheet', '-s', 
        help='Specific sheet name to access (optional)'
    )
    parser.add_argument(
        '--drive-first', '-d', 
        action='store_true',
        help='Use Drive API first instead of Sheets API'
    )
    parser.add_argument(
        '--open-browser', '-o', 
        action='store_true',
        help='Attempt to open the spreadsheet URL in a browser'
    )
    parser.add_argument(
        '--test', '-t', 
        action='store_true',
        help='Run in test mode using a known public spreadsheet'
    )
    parser.add_argument(
        '--direct', 
        action='store_true',
        help='Use direct access method for public spreadsheets'
    )
    parser.add_argument(
        '--regenerate-token', '-r', 
        action='store_true',
        help='Force regeneration of the OAuth token'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # If regenerate token is requested, delete the existing token file
    if args.regenerate_token and os.path.exists(TOKEN_PICKLE_FILE):
        print(f"Removing existing token file: {TOKEN_PICKLE_FILE}")
        os.remove(TOKEN_PICKLE_FILE)
    
    # Test authentication if in test mode
    if args.test:
        print("Running in test mode to verify authentication...")
        auth_works = test_authentication()
        if auth_works:
            print("Authentication test passed! Using test spreadsheet.")
            spreadsheet_url = FALLBACK_URL
        else:
            print("Authentication test failed. Will try to proceed anyway.")
            
            # Try each test sheet
            for test_url in PUBLIC_TEST_SHEETS:
                print(f"Trying public test sheet: {test_url}")
                
                # Try direct access method
                sheet_id = extract_spreadsheet_info(test_url)[0]
                df = access_public_sheet(sheet_id)
                
                if df is not None:
                    print("Successfully accessed public test sheet!")
                    
                    # Display summary of the loaded data
                    print("\n=== DataFrame Summary (Test Sheet) ===")
                    print(f"Shape: {df.shape} (rows, columns)")
                    print("\nColumns:")
                    for col in df.columns:
                        print(f"- {col}")
                    
                    print("\nFirst 5 rows:")
                    print(df.head())
                    
                    print("\nAuthentication works but standard API access failed.")
                    print("The issue may be with specific permissions for the target spreadsheet.")
                    sys.exit(0)
            
            # If we get here, all test sheets failed
            print("Unable to access any test sheets. There may be issues with authentication or network connectivity.")
    
    spreadsheet_url = args.url
    
    # If no URL provided via args, use default
    if not spreadsheet_url:
        print(f"No URL provided. Using default URL: {default_url}")
        spreadsheet_url = default_url
    
    # Try to open in browser if requested
    if args.open_browser:
        try_open_in_browser(spreadsheet_url)
    
    # Print information about URL verification
    print("\n===== SPREADSHEET ACCESS INFORMATION =====")
    print(f"Attempting to verify and access: {spreadsheet_url}")
    access_info, access_status = check_url_accessibility(spreadsheet_url)
    if access_status:
        print("✅ URL appears to be accessible via HTTP")
    else:
        print(f"⚠️ Warning: URL accessibility check failed: {access_info}")
        print("This doesn't necessarily mean the spreadsheet is inaccessible through the API.")
        print("Will still attempt to load the data.")
    
    # Check for unusual URL format
    if '/edit' not in spreadsheet_url and 'spreadsheets/d/' in spreadsheet_url:
        print("\n⚠️ Note: URL format appears non-standard.")
        print("Standard Google Sheets URLs typically include '/edit' after the ID.")
        print("Will attempt to process anyway, but this might cause issues.")
    
    print("\nCommon access issues and their solutions:")
    print("- If spreadsheet requires authentication: You must have access with your Google account")
    print("- If spreadsheet is public: It must be shared with 'Anyone with the link'")
    print("- If you're getting permission errors: Try --regenerate-token to create a new OAuth token")
    print("- If using the wrong URL: Make sure it's a Google Sheets URL, not a Doc or other format")
    print("=======================================\n")
    
    # Load the spreadsheet data using the requested method
    print(f"\nLoading data from: {spreadsheet_url}")
    
    df = None
    
    # Get the spreadsheet ID for direct access if requested
    if args.direct:
        print("\nAttempting direct access to public spreadsheet...")
        sheet_id, _ = extract_spreadsheet_info(spreadsheet_url)
        df = access_public_sheet(sheet_id)
        
        if df is None:
            print("Direct access failed. Falling back to standard method...")
            df = load_spreadsheet_to_dataframe(
                spreadsheet_url, 
                sheet_name=args.sheet, 
                use_drive_api=args.drive_first
            )
    else:
        # Use the standard method
        df = load_spreadsheet_to_dataframe(
            spreadsheet_url, 
            sheet_name=args.sheet, 
            use_drive_api=args.drive_first
        )
    # Display summary of the loaded data
    if df is not None:
        print("\n=== DataFrame Summary ===")
        print(f"Shape: {df.shape} (rows, columns)")
        print("\nColumns:")
        for col in df.columns:
            print(f"- {col}")
        
        print("\nFirst 5 rows:")
        print(df.head())
    else:
        print("\n❌ Failed to load spreadsheet data.")
        print("\nPossible next steps:")
        print("1. Try running with the --test flag to verify the script works with public sheets")
        print("2. Try opening the spreadsheet URL in your browser to check access:")
        print(f"   {spreadsheet_url}")
        print("3. If the URL is incorrect, provide the correct URL with --url")
        print("4. Try regenerating your authentication token with --regenerate-token")
        print("5. Check if the spreadsheet is actually shared with your Google account")
        print("6. The original URL might be for a different type of document or require special access")
        
        # Offer to open the URL in a browser
        if not args.open_browser:
            try_browser = input("\nWould you like to open the URL in your browser to check it? (y/n): ")
            if try_browser.lower() == 'y':
                try_open_in_browser(spreadsheet_url)

if __name__ == "__main__":
    main()
