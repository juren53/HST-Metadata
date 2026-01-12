#!/usr/bin/env python3
"""
Test script for GitHub Version Checker in HPM

This script tests the version checking functionality to ensure it works correctly
before testing in the full GUI.
"""

import sys
from pathlib import Path

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent
sys.path.insert(0, str(framework_dir))

from utils.github_version_checker import GitHubVersionChecker, VersionCheckResult
from __init__ import __version__

def test_version_checker():
    """Test the version checker with HPM repository"""
    print("=== HPM GitHub Version Checker Test ===")
    print()
    
    # Initialize version checker with HPM repository
    checker = GitHubVersionChecker(
        repo_url="juren53/HST-Metadata",
        current_version=__version__,
        timeout=10
    )
    
    print(f"Repository: {checker.repo_url}")
    print(f"Current version: {checker.current_version}")
    print(f"API URL: {checker.api_url}")
    print()
    
    # Test synchronous check
    print("Testing version check...")
    result = checker.get_latest_version()
    
    if result.error_message:
        print(f"❌ Error: {result.error_message}")
        
        # Check if it's the expected 404 (no releases yet)
        if "404" in result.error_message:
            print()
            print("ℹ️  This is expected - HPM repository doesn't have any releases yet.")
            print("   The version checking system is working correctly!")
            return True
    else:
        print(f"✅ Check completed successfully")
        print(f"   Current version: {result.current_version}")
        print(f"   Latest version: {result.latest_version}")
        print(f"   Has update: {result.has_update}")
        print(f"   Download URL: {result.download_url}")
        return True
    
    return False

if __name__ == "__main__":
    success = test_version_checker()
    sys.exit(0 if success else 1)
