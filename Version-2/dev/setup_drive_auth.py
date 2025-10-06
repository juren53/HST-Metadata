#!/usr/bin/env python3
"""
Setup Authentication for Excel to Google Sheets Conversion

This script creates the proper authentication token with Google Drive API access.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# Required scopes for Excel conversion
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',      # Read/write Google Sheets
    'https://www.googleapis.com/auth/drive',             # Access Google Drive files
    'https://www.googleapis.com/auth/drive.file'         # Manage created files
]

def main():
    """Create authentication token with proper scopes"""
    print("🔑 Setting Up Authentication for Excel Conversion")
    print("=" * 60)
    print("This will create a new authentication token with the necessary")
    print("permissions to convert Excel files to Google Sheets.")
    print()
    
    credentials_file = "client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json"
    
    if not os.path.exists(credentials_file):
        print(f"❌ Error: Credentials file not found")
        print(f"   Expected: {credentials_file}")
        return
    
    print("🌐 Required Permissions:")
    print("   - Google Sheets: Read and write spreadsheets")
    print("   - Google Drive: View and manage files")
    print("   - File Management: Create and modify files")
    print()
    
    try:
        # Create authentication flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        
        print("🚀 Starting authentication process...")
        print("   A browser window will open for you to authorize the application.")
        print("   Please grant all requested permissions.")
        print()
        
        # Run OAuth flow
        creds = flow.run_local_server(port=0)
        
        # Save token
        token_file = 'token_drive_sheets.pickle'
        with open(token_file, 'wb') as f:
            pickle.dump(creds, f)
        
        print("✅ Authentication successful!")
        print(f"   Token saved as: {token_file}")
        print()
        
        # Test the authentication
        print("🧪 Testing Drive API access...")
        try:
            from googleapiclient.discovery import build
            
            drive_service = build('drive', 'v3', credentials=creds)
            results = drive_service.files().list(pageSize=1).execute()
            
            print("✅ Google Drive API access confirmed")
            print()
            
            print("🎉 Setup Complete!")
            print("=" * 60)
            print("You can now convert your Excel file:")
            print()
            print("1. Update the converter to use the new token:")
            print("   Edit convert_excel_to_sheets.py and change:")
            print("   token_file=\"token_sheets.pickle\"")
            print("   to:")
            print("   token_file=\"token_drive_sheets.pickle\"")
            print()
            print("2. Run the conversion:")
            print("   python convert_excel_to_sheets.py \"your_excel_url\"")
            
        except Exception as e:
            print(f"⚠️  Drive API test failed: {e}")
            print("   But authentication was successful - you can still try the conversion")
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("   Please check your Google Cloud Console settings")

if __name__ == "__main__":
    main()
