#!/usr/bin/env python3
"""
Simple setup script for Google Sheets Type Detection Module
This script checks dependencies and creates the necessary files.
"""

import os
import sys
import subprocess
import urllib.request

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

def create_sheets_detector_file():
    """Create the sheets_detector.py file."""
    print("\nCreating sheets_detector.py file...")
    
    # Create the file with proper string handling
    content_lines = [
        '"""',
        'Google Sheets Type Detection and Conversion Module',
        '',
        'This module provides functionality to detect whether a Google Sheets URL points to:',
        '- A native Google Sheet (application/vnd.google-apps.spreadsheet)',
        '- An Excel file viewed in Google Sheets (retains original Excel mimeType)',
        '',
        'It also provides utilities to convert Excel files to native Google Sheets when needed.',
        '"""',
        '',
        'import re',
        'import logging',
        'from typing import Optional, Tuple, Dict, Any',
        'from enum import Enum',
        'from googleapiclient.discovery import build',
        'from googleapiclient.errors import HttpError',
        '',
        '',
        'class SheetType(Enum):',
        '    """Enumeration of different sheet types."""',
        '    NATIVE_GOOGLE_SHEET = "native_google_sheet"',
        '    EXCEL_FILE = "excel_file"',
        '    UNKNOWN = "unknown"',
        '',
        '',
        'class GoogleSheetsDetector:',
        '    """',
        '    A class to detect and handle different types of Google Sheets files.',
        '    """',
        '    ',
        '    # MIME types for different file formats',
        '    NATIVE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"',
        '    EXCEL_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"',
        '    EXCEL_XLS_MIME = "application/vnd.ms-excel"',
        '    ',
        '    def __init__(self, credentials):',
        '        """',
        '        Initialize the detector with Google API credentials.',
        '        ',
        '        Args:',
        '            credentials: Google API credentials object',
        '        """',
        '        self.credentials = credentials',
        '        self.drive_service = build(\'drive\', \'v3\', credentials=credentials)',
        '        self.sheets_service = build(\'sheets\', \'v4\', credentials=credentials)',
        '        self.logger = logging.getLogger(__name__)',
        '    ',
        '    def extract_file_id(self, url: str) -> Optional[str]:',
        '        """',
        '        Extract the file ID from a Google Sheets/Drive URL.',
        '        ',
        '        Args:',
        '            url: Google Sheets or Drive URL',
        '            ',
        '        Returns:',
        '            File ID if found, None otherwise',
        '        """',
        '        patterns = [',
        '            r\'/spreadsheets/d/([a-zA-Z0-9-_]+)\',  # Standard Sheets URL',
        '            r\'/file/d/([a-zA-Z0-9-_]+)\',          # Drive file URL',
        '            r\'id=([a-zA-Z0-9-_]+)\',               # URL parameter',
        '        ]',
        '        ',
        '        for pattern in patterns:',
        '            match = re.search(pattern, url)',
        '            if match:',
        '                return match.group(1)',
        '        ',
        '        self.logger.warning(f"Could not extract file ID from URL: {url}")',
        '        return None',
        '    ',
        '    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:',
        '        """',
        '        Get file metadata from Google Drive API.',
        '        ',
        '        Args:',
        '            file_id: Google Drive file ID',
        '            ',
        '        Returns:',
        '            File metadata dictionary or None if error',
        '        """',
        '        try:',
        '            metadata = self.drive_service.files().get(',
        '                fileId=file_id,',
        '                fields=\'id,name,mimeType,parents,createdTime,modifiedTime,size\'',
        '            ).execute()',
        '            ',
        '            self.logger.info(f"Retrieved metadata for file: {metadata.get(\'name\')}")',
        '            return metadata',
        '            ',
        '        except HttpError as e:',
        '            self.logger.error(f"Error retrieving file metadata: {e}")',
        '            return None',
        '    ',
        '    def detect_sheet_type(self, url: str) -> Tuple[SheetType, Optional[Dict[str, Any]]]:',
        '        """',
        '        Detect the type of sheet from a Google Sheets URL.',
        '        ',
        '        Args:',
        '            url: Google Sheets URL',
        '            ',
        '        Returns:',
        '            Tuple of (SheetType, metadata_dict)',
        '        """',
        '        file_id = self.extract_file_id(url)',
        '        if not file_id:',
        '            return SheetType.UNKNOWN, None',
        '        ',
        '        metadata = self.get_file_metadata(file_id)',
        '        if not metadata:',
        '            return SheetType.UNKNOWN, None',
        '        ',
        '        mime_type = metadata.get(\'mimeType\')',
        '        ',
        '        if mime_type == self.NATIVE_SHEET_MIME:',
        '            return SheetType.NATIVE_GOOGLE_SHEET, metadata',
        '        elif mime_type in [self.EXCEL_XLSX_MIME, self.EXCEL_XLS_MIME]:',
        '            return SheetType.EXCEL_FILE, metadata',
        '        else:',
        '            self.logger.warning(f"Unknown MIME type: {mime_type}")',
        '            return SheetType.UNKNOWN, metadata',
        '    ',
        '    def validate_sheet_access(self, file_id: str) -> bool:',
        '        """',
        '        Validate that the user has access to read the sheet.',
        '        ',
        '        Args:',
        '            file_id: Google Drive file ID',
        '            ',
        '        Returns:',
        '            True if accessible, False otherwise',
        '        """',
        '        try:',
        '            # Test both Drive and Sheets API access',
        '            drive_result = self.drive_service.files().get(fileId=file_id).execute()',
        '            ',
        '            # For sheets, try to get basic sheet info',
        '            if drive_result.get(\'mimeType\') == self.NATIVE_SHEET_MIME:',
        '                sheets_result = self.sheets_service.spreadsheets().get(',
        '                    spreadsheetId=file_id',
        '                ).execute()',
        '            ',
        '            return True',
        '            ',
        '        except HttpError as e:',
        '            self.logger.error(f"Access validation failed: {e}")',
        '            return False',
        '    ',
        '    def convert_excel_to_native_sheet(self, file_id: str,',
        '                                    new_name: Optional[str] = None) -> Optional[str]:',
        '        """',
        '        Convert an Excel file to a native Google Sheet.',
        '        ',
        '        Args:',
        '            file_id: File ID of the Excel file',
        '            new_name: Optional new name for the converted sheet',
        '            ',
        '        Returns:',
        '            File ID of the new native Google Sheet, or None if failed',
        '        """',
        '        try:',
        '            # Get original file metadata',
        '            original_metadata = self.get_file_metadata(file_id)',
        '            if not original_metadata:',
        '                return None',
        '            ',
        '            # Determine the new name',
        '            if not new_name:',
        '                original_name = original_metadata.get(\'name\', \'Converted Sheet\')',
        '                new_name = f"{original_name} (Google Sheets)"',
        '            ',
        '            # Copy the file and convert to Google Sheets format',
        '            copy_metadata = {',
        '                \'name\': new_name,',
        '                \'mimeType\': self.NATIVE_SHEET_MIME',
        '            }',
        '            ',
        '            result = self.drive_service.files().copy(',
        '                fileId=file_id,',
        '                body=copy_metadata',
        '            ).execute()',
        '            ',
        '            new_file_id = result.get(\'id\')',
        '            self.logger.info(f"Successfully converted Excel file to Google Sheet: {new_file_id}")',
        '            ',
        '            return new_file_id',
        '            ',
        '        except HttpError as e:',
        '            self.logger.error(f"Error converting Excel to Google Sheet: {e}")',
        '            return None',
        '    ',
        '    def ensure_native_google_sheet(self, url: str) -> Tuple[str, bool]:',
        '        """',
        '        Ensure the URL points to a native Google Sheet, converting if necessary.',
        '        ',
        '        Args:',
        '            url: Original Google Sheets URL',
        '            ',
        '        Returns:',
        '            Tuple of (native_sheet_url, was_converted)',
        '        """',
        '        sheet_type, metadata = self.detect_sheet_type(url)',
        '        ',
        '        if sheet_type == SheetType.NATIVE_GOOGLE_SHEET:',
        '            return url, False',
        '        ',
        '        elif sheet_type == SheetType.EXCEL_FILE:',
        '            file_id = self.extract_file_id(url)',
        '            if not file_id:',
        '                raise ValueError("Could not extract file ID from URL")',
        '            ',
        '            # Convert Excel to native Google Sheet',
        '            new_file_id = self.convert_excel_to_native_sheet(file_id)',
        '            if not new_file_id:',
        '                raise RuntimeError("Failed to convert Excel file to Google Sheet")',
        '            ',
        '            # Generate new URL',
        '            new_url = f"https://docs.google.com/spreadsheets/d/{new_file_id}/edit"',
        '            return new_url, True',
        '        ',
        '        else:',
        '            raise ValueError(f"Unsupported or unknown sheet type: {sheet_type}")',
        '',
        '',
        '# Convenience functions for easy use',
        'def create_detector(credentials) -> GoogleSheetsDetector:',
        '    """Create a GoogleSheetsDetector instance."""',
        '    return GoogleSheetsDetector(credentials)',
        '',
        '',
        'def quick_detect_type(url: str, credentials) -> SheetType:',
        '    """Quick function to detect sheet type."""',
        '    detector = GoogleSheetsDetector(credentials)',
        '    sheet_type, _ = detector.detect_sheet_type(url)',
        '    return sheet_type',
        '',
        '',
        'def ensure_compatible_url(url: str, credentials) -> str:',
        '    """',
        '    Ensure URL is compatible with tools expecting native Google Sheets.',
        '    ',
        '    This is the main function to use with existing code that requires',
        '    native Google Sheets URLs.',
        '    """',
        '    detector = GoogleSheetsDetector(credentials)',
        '    native_url, was_converted = detector.ensure_native_google_sheet(url)',
        '    ',
        '    if was_converted:',
        '        logging.info("Excel file was converted to native Google Sheet")',
        '    ',
        '    return native_url',
        '',
        '',
        'if __name__ == "__main__":',
        '    print("Google Sheets Type Detection Module")',
        '    print("=" * 40)',
        '    print("This module helps detect and convert between:")',
        '    print("- Native Google Sheets")',
        '    print("- Excel files viewed in Google Sheets")',
        '    print("\\nKey functions:")',
        '    print("- detect_sheet_type(): Identify the sheet type")',
        '    print("- ensure_compatible_url(): Convert to native sheet if needed")',
        '    print("- validate_sheet_access(): Check access permissions")',
        '    print("- convert_excel_to_native_sheet(): Convert Excel to Google Sheets")',
    ]
    
    try:
        with open('sheets_detector.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        print("✓ sheets_detector.py file created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating sheets_detector.py: {e}")
        return False

def test_import():
    """Test if the sheets_detector module can be imported."""
    try:
        import sheets_detector
        print("✓ sheets_detector module imports successfully")
        
        # Test basic functionality without credentials
        detector_class = getattr(sheets_detector, 'GoogleSheetsDetector', None)
        sheet_type_enum = getattr(sheets_detector, 'SheetType', None)
        
        if detector_class and sheet_type_enum:
            print("✓ Core classes are available")
            return True
        else:
            print("❌ Core classes not found in module")
            return False
            
    except ImportError as e:
        print(f"❌ Error importing sheets_detector: {e}")
        return False

def main():
    """Main setup function."""
    print("Google Sheets Type Detection Module Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check required packages
    missing_packages = check_required_packages()
    
    if missing_packages:
        print(f"\nFound {len(missing_packages)} missing packages.")
        install_choice = input("Install missing packages? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes']:
            if not install_packages(missing_packages):
                print("\n❌ Setup failed due to package installation errors")
                return
        else:
            print("\n⚠️  Setup incomplete - missing packages need to be installed manually")
            print("Run: pip install " + " ".join(missing_packages))
            return
    
    # Create sheets_detector.py
    if not os.path.exists('sheets_detector.py'):
        print("\nCreating sheets_detector.py file...")
        if not create_sheets_detector_file():
            print("\n❌ Setup failed - could not create sheets_detector.py")
            return
    else:
        print("✓ sheets_detector.py file already exists")
    
    # Test import
    print("\nTesting module import...")
    if test_import():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Set up your Google API credentials")
        print("2. Run your integration_example.py or modify your existing code")
        print("3. Use ensure_compatible_url() to handle different sheet types")
        print("\nExample usage:")
        print("  from sheets_detector import ensure_compatible_url")
        print("  compatible_url = ensure_compatible_url(your_url, credentials)")
    else:
        print("\n❌ Setup completed but module import failed")
        print("Please check for errors and try again.")

if __name__ == "__main__":
    main()
