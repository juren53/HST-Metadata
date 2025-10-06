#!/usr/bin/env python3
"""
Diagnostic Script for Google Sheets Access Issues

This script helps diagnose and fix common issues with Google Sheets access,
including the "This operation is not supported for this document" error.
"""

import sys
import os
import re
from typing import Dict, Any

try:
    from sheets_type_detector import (
        SheetsTypeDetector,
        detect_sheet_type,
        extract_spreadsheet_id_from_url
    )
    from sheets_converter import convert_spreadsheet_to_sheet
    print("✅ Detection module loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import detection module: {e}")
    sys.exit(1)

def analyze_url(url: str) -> Dict[str, Any]:
    """Analyze the provided URL and extract information"""
    print(f"\n🔍 Analyzing URL:")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        # Extract the file ID
        file_id = extract_spreadsheet_id_from_url(url)
        print(f"✅ Extracted File ID: {file_id}")
        
        # Analyze URL structure
        if "docs.google.com/spreadsheets" in url:
            print("📊 URL Type: Google Sheets URL")
        elif "drive.google.com" in url:
            print("📁 URL Type: Google Drive URL")
        else:
            print("🆔 URL Type: Direct File ID")
        
        # Check for special parameters
        if "gid=" in url:
            gid_match = re.search(r'gid=(\d+)', url)
            if gid_match:
                print(f"📋 Sheet GID detected: {gid_match.group(1)}")
        
        return {
            'file_id': file_id,
            'original_url': url,
            'analysis_success': True
        }
        
    except Exception as e:
        print(f"❌ URL Analysis Failed: {e}")
        return {
            'file_id': None,
            'original_url': url,
            'analysis_success': False,
            'error': str(e)
        }

def diagnose_access_issue(file_id: str) -> Dict[str, Any]:
    """Diagnose access issues with the file"""
    print(f"\n🔬 Diagnosing Access Issues:")
    print("=" * 60)
    
    # Initialize detector
    credentials_file = "client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json"
    
    try:
        detector = SheetsTypeDetector(
            client_secret_file=credentials_file,
            token_file="token_sheets.pickle"
        )
        print("✅ Detector initialized successfully")
    except Exception as e:
        return {
            'diagnosis': 'initialization_failed',
            'error': str(e),
            'recommendation': 'Check credentials file and authentication'
        }
    
    # Try to detect file type
    try:
        print(f"🔍 Attempting to detect file type for: {file_id}")
        result = detect_sheet_type(file_id, detector)
        
        print(f"✅ File detected successfully!")
        print(f"   📄 File Name: {result['file_name']}")
        print(f"   🏷️  MIME Type: {result['mime_type']}")
        print(f"   📊 Is Native Google Sheet: {'Yes' if result['is_native_sheet'] else 'No'}")
        print(f"   📈 Is Excel File: {'Yes' if result['is_excel'] else 'No'}")
        
        return {
            'diagnosis': 'success',
            'file_info': result,
            'recommendation': get_recommendation(result)
        }
        
    except PermissionError as e:
        return {
            'diagnosis': 'permission_denied',
            'error': str(e),
            'recommendation': 'File is not shared with your Google account or you lack permissions'
        }
    except Exception as e:
        error_str = str(e).lower()
        
        if 'not found' in error_str:
            return {
                'diagnosis': 'file_not_found',
                'error': str(e),
                'recommendation': 'File does not exist or URL is incorrect'
            }
        elif 'operation is not supported' in error_str:
            return {
                'diagnosis': 'unsupported_operation',
                'error': str(e),
                'recommendation': 'This appears to be an Excel file being viewed through Google Sheets'
            }
        else:
            return {
                'diagnosis': 'unknown_error',
                'error': str(e),
                'recommendation': 'Unknown error occurred - check authentication and file access'
            }

def get_recommendation(file_info: Dict[str, Any]) -> str:
    """Get specific recommendations based on file type"""
    if file_info['is_native_sheet']:
        return "File is a native Google Sheet - should work with google-to-csv.py"
    elif file_info['is_excel']:
        return "File is an Excel file - needs conversion to Google Sheets format"
    else:
        return f"File type ({file_info['mime_type']}) may not be compatible with Google Sheets operations"

def provide_solutions(diagnosis: Dict[str, Any], file_id: str):
    """Provide specific solutions based on diagnosis"""
    print(f"\n💡 Solutions and Next Steps:")
    print("=" * 60)
    
    diagnosis_type = diagnosis.get('diagnosis', 'unknown')
    
    if diagnosis_type == 'success':
        file_info = diagnosis['file_info']
        
        if file_info['is_native_sheet']:
            print("✅ This file should work with your google-to-csv.py script!")
            print(f"   Use this command:")
            print(f"   python google-to-csv.py --sheet-url \"https://docs.google.com/spreadsheets/d/{file_id}/edit\"")
            
        elif file_info['is_excel']:
            print("🔄 This Excel file needs to be converted to a Google Sheet.")
            print(f"   Option 1 - Use CLI to convert:")
            print(f"   python cli.py --credentials \"client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json\" convert \"{file_id}\" --auto-convert")
            print(f"   ")
            print(f"   Option 2 - Use enhanced extraction in your script:")
            print(f"   from example_usage import enhanced_extract_spreadsheet_id")
            print(f"   result = enhanced_extract_spreadsheet_id('{file_id}', auto_convert=True)")
            
        else:
            print(f"⚠️  Unknown file type: {file_info['mime_type']}")
            print(f"   This file may not be compatible with Google Sheets operations.")
    
    elif diagnosis_type == 'permission_denied':
        print("🔐 Permission Issue Detected")
        print("   Solutions:")
        print("   1. Ask the file owner to share the file with your Google account")
        print("   2. Request 'Editor' or 'Viewer' access to the file")
        print("   3. Check if the file URL is correct and accessible")
        print("   4. Make sure you're authenticated with the correct Google account")
        
    elif diagnosis_type == 'unsupported_operation':
        print("📊 Excel File in Google Sheets Detected")
        print("   This is exactly what our module was designed to fix!")
        print("   The error 'This operation is not supported' means you're trying")
        print("   to access an Excel file through the Google Sheets API.")
        print("   ")
        print("   Solutions:")
        print("   1. Convert the Excel file to a native Google Sheet:")
        print(f"      python cli.py --credentials \"client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json\" convert \"{file_id}\" --auto-convert")
        print("   ")
        print("   2. Use the enhanced google-to-csv.py with auto-conversion:")
        print("      # Modify your google-to-csv.py script to use:")
        print("      from example_usage import enhanced_extract_spreadsheet_id")
        print(f"      result = enhanced_extract_spreadsheet_id('{file_id}', auto_convert=True)")
        
    elif diagnosis_type == 'file_not_found':
        print("📄 File Not Found")
        print("   Solutions:")
        print("   1. Double-check the URL is correct")
        print("   2. Make sure the file hasn't been moved or deleted")
        print("   3. Check if you have access to the file")
        print("   4. Try accessing the file directly in your browser first")
        
    else:
        print("❓ General Troubleshooting")
        print("   Try these steps:")
        print("   1. Re-authenticate by deleting token_sheets.pickle and running google-to-csv.py")
        print("   2. Check that the Google Sheets API is enabled in your Google Cloud project")
        print("   3. Verify your credentials file is valid")
        print("   4. Make sure the file is accessible in your browser")

def main():
    """Main diagnostic function"""
    if len(sys.argv) < 2:
        print("Usage: python diagnose_spreadsheet.py <spreadsheet_url_or_id>")
        print("Example: python diagnose_spreadsheet.py \"https://docs.google.com/spreadsheets/d/1mgxguKnNThYH8PspEge6xS2xxPwdU2Qv/edit\"")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("🔧 Google Sheets Diagnostic Tool")
    print("=" * 70)
    print("This tool will help diagnose and fix issues with Google Sheets access.")
    
    # Step 1: Analyze URL
    url_analysis = analyze_url(url)
    
    if not url_analysis['analysis_success']:
        print(f"\n❌ Cannot proceed - URL analysis failed")
        sys.exit(1)
    
    file_id = url_analysis['file_id']
    
    # Step 2: Diagnose access issues
    diagnosis = diagnose_access_issue(file_id)
    
    # Step 3: Provide solutions
    provide_solutions(diagnosis, file_id)
    
    print(f"\n📋 Summary:")
    print("=" * 60)
    print(f"File ID: {file_id}")
    print(f"Diagnosis: {diagnosis['diagnosis']}")
    print(f"Recommendation: {diagnosis['recommendation']}")
    
    if diagnosis['diagnosis'] == 'unsupported_operation':
        print(f"\n🎯 This appears to be the exact issue our detection module solves!")
        print(f"The file is likely an Excel file being viewed through Google Sheets.")

if __name__ == "__main__":
    main()
