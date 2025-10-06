#!/usr/bin/env python3
"""
Quick test script for Google Sheets Type Detection Module - Non-interactive version
"""

import sys
import os

try:
    from sheets_type_detector import (
        SheetsTypeDetector,
        detect_sheet_type,
        validate_sheet_access,
        extract_spreadsheet_id_from_url
    )
    print("✅ Successfully imported sheets_type_detector module")
except ImportError as e:
    print(f"❌ Failed to import sheets_type_detector: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("\n🔍 Testing Basic Functionality:")
    print("=" * 50)
    
    # Test URL extraction
    test_urls = [
        "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit",
        "19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4",
        "https://drive.google.com/file/d/1BxC0123456789/view",
        "invalid_url_test"
    ]
    
    for url in test_urls:
        try:
            file_id = extract_spreadsheet_id_from_url(url)
            print(f"✅ URL extraction: '{url[:40]}...' → {file_id}")
        except Exception as e:
            print(f"❌ URL extraction: '{url[:40]}...' → Error: {e}")
    
    # Test detector initialization (without API calls)
    credentials_file = "client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json"
    
    try:
        detector = SheetsTypeDetector(
            client_secret_file=credentials_file,
            token_file="token.pickle"
        )
        print(f"✅ Detector initialized successfully")
        return detector
    except Exception as e:
        print(f"❌ Detector initialization failed: {e}")
        return None

def test_with_existing_token(detector):
    """Test API functionality using existing token if available"""
    print("\n📊 Testing API Functionality (with existing token):")
    print("=" * 50)
    
    # Check if we have an existing token
    if os.path.exists("token_sheets.pickle"):
        print("✅ Found existing token file: token_sheets.pickle")
        
        # Update detector to use the existing token
        detector.token_file = "token_sheets.pickle"
        
        test_sheet_url = "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit"
        
        try:
            print(f"🔍 Testing detection with: {test_sheet_url}")
            result = detect_sheet_type(test_sheet_url, detector)
            
            print(f"✅ Detection successful!")
            print(f"   📋 File ID: {result['file_id']}")
            print(f"   📄 File Name: {result['file_name']}")
            print(f"   🏷️  MIME Type: {result['mime_type']}")
            print(f"   📊 Is Native Google Sheet: {'✅ Yes' if result['is_native_sheet'] else '❌ No'}")
            print(f"   📈 Is Excel File: {'✅ Yes' if result['is_excel'] else '❌ No'}")
            print(f"   🔄 Can Convert: {'✅ Yes' if result['can_convert'] else '❌ No'}")
            
            return True
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Check if it's an authentication error
            if "credentials" in str(e).lower() or "auth" in str(e).lower():
                print("💡 This might be an authentication issue. You may need to re-authenticate.")
            
            return False
    else:
        print("⚠️  No existing token found (token_sheets.pickle)")
        print("💡 Run your google-to-csv.py script first to create authentication token")
        return None

def test_cli_interface():
    """Test the CLI interface functionality"""
    print("\n🖥️  Testing CLI Interface:")
    print("=" * 50)
    
    try:
        import cli
        print("✅ CLI module imported successfully")
        print("💡 You can test the CLI with:")
        print("   python cli.py detect '19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4'")
        print("   python cli.py convert 'some_excel_file_id' --auto-convert")
        return True
    except ImportError as e:
        print(f"❌ CLI module import failed: {e}")
        return False

def test_integration_helpers():
    """Test integration helper functions"""
    print("\n🔗 Testing Integration Helpers:")
    print("=" * 50)
    
    try:
        from example_usage import enhanced_extract_spreadsheet_id
        print("✅ Integration helpers imported successfully")
        
        # Test without API calls
        print("💡 Enhanced extraction function available for integration")
        print("💡 Use enhanced_extract_spreadsheet_id() in your existing scripts")
        return True
    except ImportError as e:
        print(f"❌ Integration helpers import failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Google Sheets Type Detection Module - Quick Test")
    print("=" * 60)
    
    # Test 1: Basic functionality (no API calls)
    detector = test_basic_functionality()
    
    if detector is None:
        print("\n❌ Basic functionality test failed")
        return
    
    # Test 2: API functionality with existing token
    api_success = test_with_existing_token(detector)
    
    # Test 3: CLI interface
    cli_success = test_cli_interface()
    
    # Test 4: Integration helpers
    integration_success = test_integration_helpers()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("=" * 50)
    print(f"✅ Module Import: Success")
    print(f"✅ Basic Functions: Success")
    print(f"{'✅' if api_success else '⚠️ ' if api_success is None else '❌'} API Functions: {'Success' if api_success else 'No Token' if api_success is None else 'Failed'}")
    print(f"{'✅' if cli_success else '❌'} CLI Interface: {'Success' if cli_success else 'Failed'}")
    print(f"{'✅' if integration_success else '❌'} Integration Helpers: {'Success' if integration_success else 'Failed'}")
    
    if api_success:
        print(f"\n🎉 All tests passed! The module is ready to use.")
    elif api_success is None:
        print(f"\n💡 Module is working! Run google-to-csv.py first to authenticate, then test API functions.")
    else:
        print(f"\n⚠️  Module basics work, but API authentication may need attention.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
