#!/usr/bin/env python3
"""
Fix Authentication for Google Drive API

This script helps fix authentication issues by ensuring the correct scopes
are granted for both Google Sheets and Google Drive APIs.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Required scopes for both Sheets and Drive operations
REQUIRED_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',      # For reading/writing sheets
    'https://www.googleapis.com/auth/drive',             # For file operations (convert, copy, etc.)
    'https://www.googleapis.com/auth/drive.file'         # For managing files created by the app
]

def check_current_token():
    """Check what scopes the current token has"""
    print("🔍 Checking Current Authentication:")
    print("=" * 50)
    
    token_files = ['token_sheets.pickle', 'token.pickle']
    
    for token_file in token_files:
        if os.path.exists(token_file):
            print(f"📄 Found token file: {token_file}")
            
            try:
                with open(token_file, 'rb') as f:
                    creds = pickle.load(f)
                
                if hasattr(creds, 'scopes') and creds.scopes:
                    print(f"   Current scopes:")
                    for scope in creds.scopes:
                        print(f"   - {scope}")
                    
                    # Check if we have the required scopes
                    missing_scopes = []
                    for required_scope in REQUIRED_SCOPES:
                        if required_scope not in creds.scopes:
                            missing_scopes.append(required_scope)
                    
                    if missing_scopes:
                        print(f"   ❌ Missing required scopes:")
                        for scope in missing_scopes:
                            print(f"   - {scope}")
                        return False, token_file
                    else:
                        print(f"   ✅ All required scopes present")
                        return True, token_file
                else:
                    print(f"   ⚠️  No scope information available in token")
                    return False, token_file
                    
            except Exception as e:
                print(f"   ❌ Error reading token: {e}")
        else:
            print(f"📄 Token file not found: {token_file}")
    
    return False, None

def create_new_token():
    """Create a new token with the correct scopes"""
    print("\n🔑 Creating New Authentication Token:")
    print("=" * 50)
    
    credentials_file = "client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json"
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        return False
    
    try:
        # Create flow with required scopes
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, 
            REQUIRED_SCOPES
        )
        
        print("🌐 Opening browser for authentication...")
        print("   Please authorize the application with the following scopes:")
        for scope in REQUIRED_SCOPES:
            scope_name = scope.split('/')[-1]
            print(f"   - {scope_name}: {scope}")
        
        # Run the OAuth flow
        creds = flow.run_local_server(port=0)
        
        # Save the new token
        new_token_file = 'token_drive_sheets.pickle'
        with open(new_token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ New token saved as: {new_token_file}")
        print(f"   This token has all required scopes for conversion operations")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_new_authentication():
    """Test the new authentication by trying to access Google Drive"""
    print("\n🧪 Testing New Authentication:")
    print("=" * 50)
    
    try:
        from sheets_type_detector import SheetsTypeDetector
        
        # Try with the new token
        detector = SheetsTypeDetector(
            client_secret_file="client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json",
            token_file="token_drive_sheets.pickle"
        )
        
        # Test Drive API access
        drive_service = detector._get_drive_service()
        
        # Try a simple Drive API call
        results = drive_service.files().list(pageSize=1, fields="files(id,name)").execute()
        
        print("✅ Google Drive API access confirmed")
        print("✅ Ready for Excel to Google Sheets conversion")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Google Authentication Scope Fixer")
    print("=" * 60)
    print("This script ensures you have the correct authentication scopes")
    print("for converting Excel files to Google Sheets.")
    print()
    
    # Step 1: Check current token
    has_scopes, token_file = check_current_token()
    
    if has_scopes:
        print(f"\n✅ Current authentication is sufficient!")
        print(f"   Your token has all required scopes.")
        print(f"   The conversion issue might be due to file permissions.")
        print(f"\n💡 Try these solutions:")
        print(f"   1. Make sure you own the Excel file")
        print(f"   2. Check that the file is accessible in your browser")
        print(f"   3. Verify you're authenticated with the correct Google account")
        return
    
    # Step 2: Create new token with correct scopes
    print(f"\n⚠️  Authentication needs to be updated with additional scopes.")
    print(f"   Current token only has Google Sheets access.")
    print(f"   We need Google Drive access to convert Excel files.")
    
    input("\nPress Enter to start the re-authentication process...")
    
    success = create_new_token()
    
    if not success:
        print(f"\n❌ Failed to create new authentication token")
        return
    
    # Step 3: Test the new authentication
    test_success = test_new_authentication()
    
    if test_success:
        print(f"\n🎉 Authentication Successfully Fixed!")
        print(f"=" * 60)
        print(f"You can now try converting your Excel file:")
        print(f"python convert_excel_to_sheets.py \"your_excel_url_here\"")
        print(f"\nThe script will now use the token: token_drive_sheets.pickle")
    else:
        print(f"\n❌ Authentication test failed")
        print(f"   Please check your Google Cloud project settings")

if __name__ == "__main__":
    main()
