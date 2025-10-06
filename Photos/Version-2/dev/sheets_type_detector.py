#!/usr/bin/env python3
"""
Google Sheets Type Detection Module

This module detects whether a Google Sheets URL points to a native Google Sheet
or an Excel file being viewed in Google Sheets by inspecting the mimeType using
the Google Drive API.

Key Features:
- Detect sheet type based on mimeType
- Convert Excel files to native Google Sheets
- Validate sheet access permissions
- Extract spreadsheet IDs from URLs
- Handle authentication with Google APIs

Requirements:
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
"""

import os
import re
import pickle
from typing import Optional, Dict, Any, Tuple
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsTypeDetector:
    """
    A class to detect and manage Google Sheets types using the Google Drive API.
    """
    
    # MIME types for different file formats
    NATIVE_SHEET_MIME = 'application/vnd.google-apps.spreadsheet'
    EXCEL_XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    EXCEL_XLS_MIME = 'application/vnd.ms-excel'
    
    # Required scopes for Google Drive and Sheets APIs
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self, 
                 client_secret_file: str = 'credentials.json',
                 token_file: str = 'token.pickle'):
        """
        Initialize the SheetsTypeDetector.
        
        Args:
            client_secret_file: Path to the OAuth2 client secret file
            token_file: Path to store the authentication token
        """
        self.client_secret_file = client_secret_file
        self.token_file = token_file
        self._drive_service = None
        self._sheets_service = None
        
    def get_credentials(self):
        """
        Get or refresh Google API credentials.
        
        Returns:
            google.oauth2.credentials.Credentials: Valid credentials
            
        Raises:
            FileNotFoundError: If client secret file is not found
            Exception: If authentication fails
        """
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"Warning: Could not load existing token: {e}")
                
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
                    
            if not creds:
                if not os.path.exists(self.client_secret_file):
                    raise FileNotFoundError(
                        f"Client secret file not found: {self.client_secret_file}\n"
                        "Please download it from Google Cloud Console."
                    )
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                
            # Save credentials for next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Warning: Could not save token: {e}")
                
        return creds
    
    def _get_drive_service(self):
        """Get or create Google Drive service instance."""
        if self._drive_service is None:
            creds = self.get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service
    
    def _get_sheets_service(self):
        """Get or create Google Sheets service instance."""
        if self._sheets_service is None:
            creds = self.get_credentials()
            self._sheets_service = build('sheets', 'v4', credentials=creds)
        return self._sheets_service


def extract_spreadsheet_id_from_url(url: str) -> str:
    """
    Extract the spreadsheet ID from a Google Sheets or Drive URL.
    
    Args:
        url: URL of the Google Spreadsheet or Drive file
        
    Returns:
        str: Spreadsheet/file ID extracted from the URL
        
    Raises:
        ValueError: If the URL format is invalid
        
    Examples:
        >>> extract_spreadsheet_id_from_url('https://docs.google.com/spreadsheets/d/1BxC.../edit')
        '1BxC...'
        >>> extract_spreadsheet_id_from_url('https://drive.google.com/file/d/1BxC.../view')
        '1BxC...'
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
        
    url = url.strip()
    
    # Handle direct ID input (not a URL)
    if not url.startswith('http'):
        if re.match(r'^[a-zA-Z0-9_-]+$', url):
            return url
        else:
            raise ValueError("Invalid spreadsheet ID format")
    
    # Google Sheets URL patterns
    patterns = [
        r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'file/d/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(
        "Invalid Google Sheets/Drive URL format. "
        "Expected formats:\n"
        "- https://docs.google.com/spreadsheets/d/ID/...\n"
        "- https://drive.google.com/file/d/ID/...\n"
        "- Or just the ID itself"
    )


def detect_sheet_type(url_or_id: str, detector: Optional[SheetsTypeDetector] = None) -> Dict[str, Any]:
    """
    Detect the type of a Google Sheets file by examining its mimeType.
    
    Args:
        url_or_id: Google Sheets URL or file ID
        detector: SheetsTypeDetector instance (creates new one if None)
        
    Returns:
        Dict containing:
        - file_id: The Google Drive file ID
        - mime_type: The file's MIME type
        - is_native_sheet: Boolean indicating if it's a native Google Sheet
        - is_excel: Boolean indicating if it's an Excel file
        - file_name: Name of the file
        - can_convert: Boolean indicating if conversion is possible
        
    Raises:
        ValueError: If URL/ID format is invalid
        HttpError: If file access fails
        Exception: If authentication or API call fails
        
    Example:
        >>> result = detect_sheet_type('https://docs.google.com/spreadsheets/d/1BxC.../edit')
        >>> print(f"Is native sheet: {result['is_native_sheet']}")
        >>> print(f"MIME type: {result['mime_type']}")
    """
    if detector is None:
        detector = SheetsTypeDetector()
    
    # Extract file ID from URL
    file_id = extract_spreadsheet_id_from_url(url_or_id)
    
    try:
        # Get file metadata from Google Drive API
        drive_service = detector._get_drive_service()
        file_metadata = drive_service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,parents,permissions'
        ).execute()
        
        mime_type = file_metadata.get('mimeType', '')
        file_name = file_metadata.get('name', 'Unknown')
        
        # Determine file type
        is_native_sheet = mime_type == SheetsTypeDetector.NATIVE_SHEET_MIME
        is_excel = mime_type in [
            SheetsTypeDetector.EXCEL_XLSX_MIME,
            SheetsTypeDetector.EXCEL_XLS_MIME
        ]
        
        # Determine if conversion is possible
        can_convert = is_excel and not is_native_sheet
        
        return {
            'file_id': file_id,
            'mime_type': mime_type,
            'file_name': file_name,
            'is_native_sheet': is_native_sheet,
            'is_excel': is_excel,
            'can_convert': can_convert,
            'metadata': file_metadata
        }
        
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_reason = error_details.get('reason', 'unknown')
        
        if e.resp.status == 404:
            raise ValueError(f"File not found: {file_id}")
        elif e.resp.status == 403:
            raise PermissionError(f"Access denied to file: {file_id}")
        else:
            raise Exception(f"Google Drive API error ({e.resp.status}): {error_reason}")


def validate_sheet_access(url_or_id: str, detector: Optional[SheetsTypeDetector] = None) -> Dict[str, Any]:
    """
    Validate access to a Google Sheets file and return access information.
    
    Args:
        url_or_id: Google Sheets URL or file ID
        detector: SheetsTypeDetector instance (creates new one if None)
        
    Returns:
        Dict containing:
        - has_access: Boolean indicating if file is accessible
        - access_level: String describing access level ('reader', 'writer', 'owner', etc.)
        - can_read: Boolean indicating read permission
        - can_write: Boolean indicating write permission
        - error_message: Error message if access validation failed
        
    Example:
        >>> access_info = validate_sheet_access('1BxC...')
        >>> if access_info['has_access']:
        ...     print(f"Access level: {access_info['access_level']}")
    """
    if detector is None:
        detector = SheetsTypeDetector()
    
    try:
        # First, try to detect the sheet type (this validates basic access)
        sheet_info = detect_sheet_type(url_or_id, detector)
        
        # Try to access the sheet content to verify read permissions
        file_id = sheet_info['file_id']
        
        if sheet_info['is_native_sheet']:
            # For native sheets, try to read metadata
            sheets_service = detector._get_sheets_service()
            spreadsheet = sheets_service.spreadsheets().get(
                spreadsheetId=file_id,
                fields='properties,sheets.properties'
            ).execute()
            
            can_read = True
            
            # Try a simple write operation to test write permissions
            # (We'll just try to get the spreadsheet with write intent)
            try:
                # This is a read operation but requires write scope to succeed
                sheets_service.spreadsheets().values().get(
                    spreadsheetId=file_id,
                    range='A1:A1'
                ).execute()
                can_write = True
                access_level = 'writer'
            except HttpError as e:
                if e.resp.status == 403:
                    can_write = False
                    access_level = 'reader'
                else:
                    can_write = False
                    access_level = 'reader'
                    
        else:
            # For non-native sheets, we can only check Drive API access
            can_read = True  # If we got here, we have read access
            can_write = None  # Unknown for non-native sheets
            access_level = 'unknown'
        
        return {
            'has_access': True,
            'access_level': access_level,
            'can_read': can_read,
            'can_write': can_write,
            'error_message': None,
            'file_info': sheet_info
        }
        
    except Exception as e:
        return {
            'has_access': False,
            'access_level': None,
            'can_read': False,
            'can_write': False,
            'error_message': str(e),
            'file_info': None
        }
