#!/usr/bin/env python3
"""
Setup script for Google Sheets Type Detection Module

This script helps you set up the sheets_detector module and its dependencies.
Run this script to ensure everything is properly configured.
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.6 or higher."""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✓ Python version OK: {sys.version.split()[0]}")
    return True

def check_required_packages():
    """Check if required packages are installed."""
    required_packages = [
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Try to import the main modules
            if package == 'google-api-python-client':
                import googleapiclient
            elif package == 'google-auth':
                import google.auth
            elif package == 'google-auth-oauthlib':
                import google_auth_oauthlib
            elif package == 'google-auth-httplib2':
                import google_auth_httplib2
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    return missing_packages

def install_packages(packages):
    """Install missing packages using pip."""
    if not packages:
        return True
    
    print(f"\nInstalling missing packages: {', '.join(packages)}")
    
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_sheets_detector_file():
    """Check if sheets_detector.py exists in the current directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sheets_detector_path = os.path.join(current_dir, 'sheets_detector.py')
    
    if os.path.exists(sheets_detector_path):
        print("✓ sheets_detector.py file found")
        return True
    else:
        print("❌ sheets_detector.py file NOT found")
        print(f"   Expected location: {sheets_detector_path}")
        return False

def create_sheets_detector_file():
    """Create the sheets_detector.py file if it doesn't exist."""
    print("\nCreating sheets_detector.py file...")
    
    # The content of the sheets_detector module
    sheets_detector_content = '''"""
Google Sheets Type Detection and Conversion Module

This module provides functionality to detect whether a Google Sheets URL points to:
- A native Google Sheet (application/vnd.google-apps.spreadsheet)
- An Excel file viewed in Google Sheets (retains original Excel mimeType)

It also provides utilities to convert Excel files to native Google Sheets when needed.
"""

import re
import logging
from typing import Optional, Tuple, Dict, Any
from enum import Enum
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetType(Enum):
    """Enumeration of different sheet types."""
    NATIVE_GOOGLE_SHEET = "native_google_sheet"
    EXCEL_FILE = "excel_file"
    UNKNOWN = "unknown"


class GoogleSheetsDetector:
    """
    A class to detect and handle different types of Google Sheets files.
    """
    
    # MIME types for different file formats
    NATIVE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"
    EXCEL_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXCEL_XLS_MIME = "application/vnd.ms-excel"
    
    def __init__(self, credentials):
        """
        Initialize the detector with Google API credentials.
        
        Args:
            credentials: Google API credentials object
        """
        self.credentials = credentials
        self.drive_service = build('drive', 'v3', credentials=credentials)
        self.sheets_service = build('sheets', 'v4', credentials=credentials)
        self.logger = logging.getLogger(__name__)
    
    def extract_file_id(self, url: str) -> Optional[str]:
        """
        Extract the file ID from a Google Sheets/Drive URL.
        
        Args:
            url: Google Sheets or Drive URL
            
        Returns:
            File ID if found, None otherwise
        """
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',  # Standard Sheets URL
            r'/file/d/([a-zA-Z0-9-_]+)',          # Drive file URL
            r'id=([a-zA-Z0-9-_]+)',               # URL parameter
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        self.logger.warning(f"Could not extract file ID from URL: {url}")
        return None
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from Google Drive API.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File metadata dictionary or None if error
        """
        try:
            metadata = self.drive_service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,parents,createdTime,modifiedTime,size'
            ).execute()
            
            self.logger.info(f"Retrieved metadata for file: {metadata.get('name')}")
            return metadata
            
        except HttpError as e:
            self.logger.error(f"Error retrieving file metadata: {e}")
            return None
    
    def detect_sheet_type(self, url: str) -> Tuple[SheetType, Optional[Dict[str, Any]]]:
        """
        Detect the type of sheet from a Googl