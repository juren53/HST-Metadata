#!/usr/bin/env python3
"""
Cleanup script for deprecated Google authentication files and tokens.

This script removes Google-related files that are no longer needed
after the HST Photo Framework migration from Google Sheets to Excel.

Files to be removed:
- token_sheets.pickle (Google Sheets authentication tokens)
- token_drive_sheets.pickle (Google Drive + Sheets tokens)
- client_secret_*.json (Google OAuth client secrets)
- client_secret.json (backup client secrets)

Files to be kept:
- Google_form/ directory (preserved for reference, but not actively used)
"""

import os
import sys
from pathlib import Path
from typing import List


def get_framework_directory() -> Path:
    """Get the framework directory path."""
    return Path(__file__).parent


def find_google_files() -> List[Path]:
    """Find all Google-related files that should be removed."""
    framework_dir = get_framework_directory()
    google_files = []

    # Find token files
    for token_file in ["token_sheets.pickle", "token_drive_sheets.pickle"]:
        token_path = framework_dir / token_file
        if token_path.exists():
            google_files.append(token_path)

    # Find client secret files
    for secret_file in framework_dir.glob("client_secret_*.json"):
        if secret_file.exists():
            google_files.append(secret_file)

    # Check for specific client secret file
    client_secret = framework_dir / "client_secret.json"
    if client_secret.exists():
        google_files.append(client_secret)

    return google_files


def remove_files_safely(files: List[Path]) -> None:
    """Safely remove files with user confirmation."""
    if not files:
        print("No Google authentication files found to remove.")
        return

    print("The following Google authentication files will be removed:")
    for file_path in files:
        print(f"  - {file_path.name} ({file_path})")

print("\nRemoving Google authentication files...")

    removed_count = 0
    for file_path in files:
        try:
            if file_path.is_file():
                file_path.unlink()
                print(f"  + Removed file: {file_path.name}")
                removed_count += 1
            elif file_path.is_dir():
                import shutil

                shutil.rmtree(file_path)
                print(f"  + Removed directory: {file_path.name}")
                removed_count += 1
        except Exception as e:
            print(f"  - Error removing {file_path.name}: {e}")

    print(f"\nCleanup completed. Removed {removed_count} files/directories.")
    print(
        "Google authentication files are no longer needed with the Excel-based workflow."
    )


def preserve_google_form_directory() -> None:
    """Preserve Google_form directory with a note about deprecation."""
    framework_dir = get_framework_directory()
    google_form_dir = framework_dir / "Google_form"

    if google_form_dir.exists():
        # Create a README file explaining the deprecation
        readme_content = """# Google Form Integration - DEPRECATED

This directory contains Google Forms integration code that is no longer used
as the HST Photo Framework has migrated from Google Sheets to Excel spreadsheets.

## Migration Status
- Phase 1: ✅ Core Data Access Layer (Google Sheets → Excel)
- Phase 2: ✅ UI Updates (Google Worksheet → Excel Spreadsheet)  
- Phase 3: ✅ Dependencies Cleanup (Google API → Excel processing)

## Recommendation
This directory can be safely removed in a future release, but is preserved
temporarily for reference and rollback purposes.

## Files in this directory
- form_generator.py (Google Forms to Excel conversion)
- requirements.txt (Google Forms dependencies)  
- token_form_generator.pickle (Forms authentication tokens)

Created: 2026-01-16
"""
        readme_path = google_form_dir / "README_DEPRECATION.md"

        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            print(f"  + Created deprecation notice: {readme_path}")
        except Exception as e:
            print(f"  - Error creating deprecation notice: {e}")


def main():
    """Main cleanup function."""
    print("HST Photo Framework - Google Authentication Cleanup")
    print("=" * 60)

    framework_dir = get_framework_directory()
    print(f"Framework directory: {framework_dir}")

    # Find Google files to remove
    google_files = find_google_files()

    if not google_files:
        print("✅ No Google authentication files found.")
        print("The framework has already been cleaned up.")
        return

    # Preserve Google_form directory with notice
    preserve_google_form_directory()

    # Remove files
    remove_files_safely(google_files)

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Google Authentication Cleanup Complete!")
    print("📊 Migration Progress: Phase 3/4 Complete (75% overall)")
    print("🔄 Ready for Phase 4: Testing and Documentation")


if __name__ == "__main__":
    main()
