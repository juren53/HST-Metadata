#!/usr/bin/env python3
"""
GitHub Version Checker Module

A standalone module for checking GitHub repository releases and comparing versions.
Designed to be reusable across different PyQt5/PyQt6/PySide applications.

Author: SysMon Project
Created: 2026-01-01
"""

import json
import threading
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from typing import Optional, Dict, Any, Callable
import re


class VersionCheckResult:
    """Data class for version check results"""
    def __init__(self):
        self.has_update = False
        self.current_version = ""
        self.latest_version = ""
        self.download_url = ""
        self.release_notes = ""
        self.published_date = ""
        self.error_message = ""
        self.is_newer = False


class GitHubVersionChecker:
    """
    Standalone GitHub version checking module
    
    Features:
    - Async version checking with callbacks
    - Semantic version comparison
    - Robust error handling
    - Configurable repositories
    - Minimal dependencies (urllib only)
    """
    
    def __init__(self, repo_url: str, current_version: str, timeout: int = 10):
        """
        Initialize version checker
        
        Args:
            repo_url: GitHub repository URL (e.g., 'owner/repo' or full URL)
            current_version: Current application version (e.g., '0.2.18d')
            timeout: Network request timeout in seconds
        """
        self.repo_url = self._normalize_repo_url(repo_url)
        self.current_version = current_version
        self.timeout = timeout
        self.api_url = f"https://api.github.com/repos/{self.repo_url}/releases/latest"
        
    def _normalize_repo_url(self, repo_url: str) -> str:
        """Convert various GitHub URL formats to 'owner/repo' format"""
        if "/" not in repo_url:
            raise ValueError("Invalid repository URL format")
            
        # Extract owner/repo from various GitHub URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'^([^/]+)/([^/]+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return f"{match.group(1)}/{match.group(2)}"
        
        raise ValueError(f"Unable to parse repository URL: {repo_url}")
    
    def get_latest_version(self) -> VersionCheckResult:
        """
        Synchronous version check with blocking I/O
        
        Returns:
            VersionCheckResult object with check results
        """
        result = VersionCheckResult()
        result.current_version = self.current_version
        
        try:
            with urlopen(self.api_url, timeout=self.timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Parse response
                    latest_version = data.get('tag_name', '').lstrip('v')
                    download_url = data.get('html_url', '')
                    release_notes = data.get('body', '')
                    published_date = data.get('published_at', '')
                    
                    result.latest_version = latest_version
                    result.download_url = download_url
                    result.release_notes = release_notes
                    result.published_date = published_date
                    
                    # Compare versions
                    comparison = self.compare_versions(self.current_version, latest_version)
                    result.is_newer = comparison < 0  # current < latest
                    result.has_update = result.is_newer
                    
                else:
                    result.error_message = f"GitHub API returned status {response.status}"
                    
        except (URLError, HTTPError) as e:
            result.error_message = f"Network error: {str(e)}"
        except json.JSONDecodeError as e:
            result.error_message = f"Invalid JSON response: {str(e)}"
        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)}"
        
        return result
    
    def check_for_updates(self, callback: Callable[[VersionCheckResult], None]) -> None:
        """
        Asynchronous version check with callback
        
        Args:
            callback: Function to call with VersionCheckResult when complete
        """
        def background_check():
            result = self.get_latest_version()
            if callback:
                callback(result)
        
        # Run in background thread
        thread = threading.Thread(target=background_check, daemon=True)
        thread.start()
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two semantic version strings
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        def normalize_version(v: str) -> tuple:
            # Remove 'v' prefix and split
            v = v.lstrip('v')
            
            # Extract numeric parts first
            numeric_parts = []
            for part in re.split(r'[^\d]+', v):
                if part.isdigit():
                    numeric_parts.append(int(part))
            
            # Pad to 3 parts (major.minor.patch)
            while len(numeric_parts) < 3:
                numeric_parts.append(0)
            
            # Check for prerelease suffixes
            prerelease_type = None
            prerelease_rank = 0
            
            # Look for suffix patterns
            if re.search(r'[a-zA-Z]$', v):
                last_char = v[-1].lower()
                if last_char == 'a':
                    prerelease_type = 'alpha'
                    prerelease_rank = 0
                elif last_char == 'b':
                    prerelease_type = 'beta'
                    prerelease_rank = 1
                elif last_char == 'c' and 'rc' in v.lower():
                    prerelease_type = 'rc'
                    prerelease_rank = 2
            
            return (numeric_parts, prerelease_type, prerelease_rank)
        
        v1_norm = normalize_version(version1)
        v2_norm = normalize_version(version2)
        
        # Compare numeric parts first
        for i in range(3):
            if v1_norm[0][i] < v2_norm[0][i]:
                return -1
            elif v1_norm[0][i] > v2_norm[0][i]:
                return 1
        
        # If numeric parts are equal, compare prerelease
        if v1_norm[1] and not v2_norm[1]:
            return -1  # prerelease < release
        elif not v1_norm[1] and v2_norm[1]:
            return 1   # release > prerelease
        elif v1_norm[1] and v2_norm[1]:
            if v1_norm[2] < v2_norm[2]:
                return -1
            elif v1_norm[2] > v2_norm[2]:
                return 1
        
        return 0  # versions are equal


def test_version_checker():
    """Test the version checker with SysMon repository"""
    print("=== GitHub Version Checker Test ===")
    
    # Test with current SysMon version
    checker = GitHubVersionChecker(
        repo_url="juren53/system-monitor",
        current_version="0.2.18d",
        timeout=10
    )
    
    print(f"Checking repository: {checker.repo_url}")
    print(f"Current version: {checker.current_version}")
    print(f"API URL: {checker.api_url}")
    print()
    
    # Test synchronous check
    print("1. Testing synchronous version check...")
    start_time = time.time()
    result = checker.get_latest_version()
    elapsed = time.time() - start_time
    
    if result.error_message:
        print(f"❌ Error: {result.error_message}")
    else:
        print(f"✅ Check completed in {elapsed:.2f} seconds")
        print(f"   Current version: {result.current_version}")
        print(f"   Latest version: {result.latest_version}")
        print(f"   Has update: {result.has_update}")
        print(f"   Is newer: {result.is_newer}")
        print(f"   Download URL: {result.download_url}")
        print(f"   Published: {result.published_date}")
    
    print()
    
    # Test version comparison
    print("2. Testing version comparison...")
    test_versions = [
        ("0.2.18d", "0.2.18d", 0),
        ("0.2.18", "0.2.19", -1),
        ("0.2.19", "0.2.18", 1),
        ("0.2.18a", "0.2.18", -1),
        ("0.2.18", "0.2.18a", 1),
        ("0.2.18b", "0.2.18a", 1),
    ]
    
    for v1, v2, expected in test_versions:
        actual = checker.compare_versions(v1, v2)
        status = "✅" if actual == expected else "❌"
        print(f"   {status} compare('{v1}', '{v2}') = {actual} (expected {expected})")
    
    print()
    
    # Test asynchronous check
    print("3. Testing asynchronous version check...")
    
    def async_callback(result: VersionCheckResult):
        if result.error_message:
            print(f"❌ Async check failed: {result.error_message}")
        else:
            print(f"✅ Async check completed")
            print(f"   Latest version: {result.latest_version}")
            print(f"   Has update: {result.has_update}")
    
    checker.check_for_updates(async_callback)
    print("   Async check started... (waiting for callback)")
    
    # Wait for async completion
    time.sleep(5)
    print()


if __name__ == "__main__":
    test_version_checker()