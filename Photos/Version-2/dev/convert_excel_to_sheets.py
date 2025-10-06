#!/usr/bin/env python3
"""
Convert Excel File to Google Sheets

This script specifically handles converting Excel files (XLSX) that are uploaded
to Google Drive but not yet converted to native Google Sheets format.
"""

import sys
import os

try:
    from sheets_type_detector import SheetsTypeDetector, extract_spreadsheet_id_from_url
    from sheets_converter import convert_spreadsheet_to_sheet
    print("✅ Conversion modules loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import conversion modules: {e}")
    sys.exit(1)

def convert_excel_file(url_or_id: str):
    """Convert an Excel file to Google Sheets format"""
    
    print("🔄 Excel to Google Sheets Converter")
    print("=" * 60)
    
    # Extract file ID
    try:
        file_id = extract_spreadsheet_id_from_url(url_or_id)
        print(f"📋 File ID: {file_id}")
    except Exception as e:
        print(f"❌ Error extracting file ID: {e}")
        return False
    
    # Initialize detector with your credentials
    credentials_file = "client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json"
    
    # Try with Drive-enabled token first, fall back to creating new one
    token_files = ["token_drive_sheets.pickle", "token_sheets.pickle"]
    detector = None
    
    for token_file in token_files:
        try:
            print(f"🔑 Trying authentication with: {token_file}")
            detector = SheetsTypeDetector(
                client_secret_file=credentials_file,
                token_file=token_file
            )
            
            # Test if we have Drive API access
            drive_service = detector._get_drive_service()
            drive_service.files().list(pageSize=1).execute()
            
            print("✅ Authentication successful with Drive API access")
            break
            
        except Exception as e:
            print(f"⚠️  {token_file} doesn't have Drive API access: {e}")
            detector = None
    
    if detector is None:
        print(f"\n🔑 Need to create new authentication with Drive API access...")
        print(f"   This is required to convert Excel files to Google Sheets.")
        
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            import pickle
            
            # Required scopes for conversion
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file'
            ]
            
            print(f"🌐 Opening browser for authentication...")
            print(f"   Please grant permissions for Google Sheets and Drive access.")
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save new token
            with open("token_drive_sheets.pickle", 'wb') as f:
                pickle.dump(creds, f)
            
            # Create detector with new token
            detector = SheetsTypeDetector(
                client_secret_file=credentials_file,
                token_file="token_drive_sheets.pickle"
            )
            
            print("✅ New authentication created successfully")
            
        except Exception as e:
            print(f"❌ Failed to create new authentication: {e}")
            return False
    
    # Attempt conversion
    print(f"\n🔄 Converting Excel file to Google Sheets...")
    print(f"   This is equivalent to using 'File > Save as Google Sheets' in the browser")
    
    try:
        result = convert_spreadsheet_to_sheet(file_id, detector)
        
        if result['success']:
            print(f"\n✅ Conversion Successful!")
            print(f"   📄 Original File ID: {result['original_file_id']}")
            print(f"   📊 New Google Sheet ID: {result['new_file_id']}")
            print(f"   📝 New File Name: {result['new_file_name']}")
            print(f"   🔗 New URL: {result['new_file_url']}")
            
            print(f"\n🎯 Ready to use with google-to-csv.py:")
            print(f"   python google-to-csv.py --sheet-url \"{result['new_file_url']}\"")
            
            return result['new_file_id']
        else:
            print(f"\n❌ Conversion Failed:")
            print(f"   Error: {result['error_message']}")
            
            # Provide specific help based on error
            if "already a native Google Sheet" in result['error_message']:
                print(f"\n💡 The file is already a Google Sheet. Try using it directly:")
                print(f"   python google-to-csv.py --sheet-url \"https://docs.google.com/spreadsheets/d/{file_id}/edit\"")
            elif "Permission denied" in result['error_message']:
                print(f"\n💡 Permission issue. Make sure:")
                print(f"   1. You own this file or have edit access")
                print(f"   2. You're authenticated with the correct Google account")
                print(f"   3. The file is accessible in your browser")
            elif "not supported for conversion" in result['error_message']:
                print(f"\n💡 File type issue. The file might not be an Excel file.")
                print(f"   Check the file type in Google Drive.")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Conversion failed with error: {e}")
        
        # Check for specific error patterns
        error_str = str(e).lower()
        if "permission" in error_str or "access" in error_str:
            print(f"\n💡 This appears to be a permission issue.")
            print(f"   Solutions:")
            print(f"   1. Make sure you own the file or have edit access")
            print(f"   2. Check if you're authenticated with the correct Google account")
            print(f"   3. Try accessing the file in your browser first")
        elif "not found" in error_str:
            print(f"\n💡 File not found. Check:")
            print(f"   1. The URL is correct")
            print(f"   2. The file hasn't been moved or deleted")
            print(f"   3. You have access to view the file")
        else:
            print(f"\n💡 General troubleshooting:")
            print(f"   1. Try re-authenticating (delete token_sheets.pickle)")
            print(f"   2. Make sure the Google Drive API is enabled")
            print(f"   3. Check your internet connection")
        
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_excel_to_sheets.py <excel_file_url_or_id>")
        print()
        print("Example:")
        print("python convert_excel_to_sheets.py \"https://docs.google.com/spreadsheets/d/1mgxguKnNThYH8PspEge6xS2xxPwdU2Qv/edit\"")
        print()
        print("This script converts Excel files (XLSX) uploaded to Google Drive")
        print("into native Google Sheets format, equivalent to using the")
        print("'File > Save as Google Sheets' option in the browser.")
        sys.exit(1)
    
    url_or_id = sys.argv[1]
    
    print("📊 Excel to Google Sheets Converter")
    print("=" * 70)
    print("This script converts Excel files uploaded to Google Drive")
    print("into native Google Sheets format.")
    print()
    
    success = convert_excel_file(url_or_id)
    
    if success:
        print(f"\n🎉 Success! Your Excel file has been converted to a Google Sheet.")
        print(f"You can now use it with your google-to-csv.py script.")
    else:
        print(f"\n❌ Conversion failed. See the error messages above for troubleshooting.")

if __name__ == "__main__":
    main()
