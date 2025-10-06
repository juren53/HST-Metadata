#!/usr/bin/env python3
"""
Test script for Google Sheets Type Detection Module
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

def test_url_extraction():
    """Test URL extraction functionality"""
    print("\n🔍 Testing URL Extraction:")
    print("=" * 50)
    
    test_urls = [
        "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit",
        "19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4",
        "https://drive.google.com/file/d/1BxC0123456789/view"
    ]
    
    for url in test_urls:
        try:
            file_id = extract_spreadsheet_id_from_url(url)
            print(f"✅ '{url[:50]}...' → {file_id}")
        except Exception as e:
            print(f"❌ '{url[:50]}...' → Error: {e}")

def test_detector_initialization():
    """Test detector initialization"""
    print("\n🔧 Testing Detector Initialization:")
    print("=" * 50)
    
    # Use the existing credentials file
    credentials_file = "client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json"
    
    try:
        detector = SheetsTypeDetector(
            client_secret_file=credentials_file,
            token_file="token.pickle"
        )
        print(f"✅ Detector initialized with credentials: {credentials_file}")
        return detector
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return None

def test_sheet_detection(detector):
    """Test sheet type detection with a known Google Sheet"""
    print("\n📊 Testing Sheet Detection:")
    print("=" * 50)
    
    # Using the default spreadsheet ID from your google-to-csv.py
    test_sheet_url = "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit"
    
    try:
        print(f"Testing with URL: {test_sheet_url}")
        result = detect_sheet_type(test_sheet_url, detector)
        
        print(f"✅ Detection successful!")
        print(f"   File ID: {result['file_id']}")
        print(f"   File Name: {result['file_name']}")
        print(f"   MIME Type: {result['mime_type']}")
        print(f"   Is Native Google Sheet: {result['is_native_sheet']}")
        print(f"   Is Excel File: {result['is_excel']}")
        print(f"   Can Convert: {result['can_convert']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Detection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return None

def test_access_validation(detector):
    """Test access validation"""
    print("\n🔐 Testing Access Validation:")
    print("=" * 50)
    
    test_sheet_url = "https://docs.google.com/spreadsheets/d/19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4/edit"
    
    try:
        result = validate_sheet_access(test_sheet_url, detector)
        
        print(f"✅ Access validation completed!")
        print(f"   Has Access: {result['has_access']}")
        print(f"   Access Level: {result['access_level']}")
        print(f"   Can Read: {result['can_read']}")
        print(f"   Can Write: {result['can_write']}")
        
        if result['error_message']:
            print(f"   Error: {result['error_message']}")
            
    except Exception as e:
        print(f"❌ Access validation failed: {e}")

def main():
    """Main test function"""
    print("🚀 Google Sheets Type Detection Module - Test Suite")
    print("=" * 60)
    
    # Test 1: URL Extraction (no API calls)
    test_url_extraction()
    
    # Test 2: Detector Initialization
    detector = test_detector_initialization()
    
    if detector is None:
        print("\n❌ Cannot proceed with API tests - detector initialization failed")
        print("💡 Make sure you have valid Google API credentials")
        return
    
    # Test 3: Sheet Detection (requires API access)
    print("\n⚠️  The following tests require Google API access and authentication...")
    input("Press Enter to continue with API tests (this may open a browser for authentication)...")
    
    detection_result = test_sheet_detection(detector)
    
    # Test 4: Access Validation (requires API access)
    if detection_result:
        test_access_validation(detector)
    
    print("\n🎉 Test suite completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
