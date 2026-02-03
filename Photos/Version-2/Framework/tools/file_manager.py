#!/usr/bin/env python3
"""
Excel File Manager for HST Photo Metadata System

This module handles Excel file operations for the HPM system including:
- Copying Excel spreadsheets to standardized input locations
- Validating Excel file structure for HPM compatibility
- Managing file naming conflicts and organization
- Providing comprehensive error handling and reporting

Author: HPM Development Team
Version: 1.0.0
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Tuple, Optional, List
import pandas as pd

# Configure module logger
logger = logging.getLogger(__name__)


class FileManager:
    """Manages Excel file operations for HPM system."""

    def __init__(self, project_data_dir: str):
        """
        Initialize FileManager with project directory.

        Args:
            project_data_dir: Path to the project data directory
        """
        self.project_data_dir = Path(project_data_dir)
        self.spreadsheet_dir = self.project_data_dir / "input" / "spreadsheet"
        self._ensure_directory_structure()

    def _ensure_directory_structure(self) -> None:
        """Ensure required directory structure exists."""
        try:
            self.spreadsheet_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(
                f"Ensured spreadsheet directory exists: {self.spreadsheet_dir}"
            )
        except Exception as e:
            logger.error(f"Failed to create directory structure: {e}")
            raise

    def copy_excel_to_input(self, source_path: str) -> Tuple[bool, str, str]:
        """
        Copy Excel spreadsheet to input/spreadsheet/ directory.

        Args:
            source_path: Path to the source Excel file

        Returns:
            Tuple of (success: bool, message: str, target_path: str)

        Example:
            success, message, target_path = file_manager.copy_excel_to_input("/path/to/file.xlsx")
        """
        try:
            source_path = Path(source_path)

            # Validate source file exists and is readable
            if not source_path.exists():
                return False, f"Source file does not exist: {source_path}", ""

            if not source_path.is_file():
                return False, f"Source path is not a file: {source_path}", ""

            # Validate file extension
            if source_path.suffix.lower() not in [".xlsx", ".xls"]:
                return (
                    False,
                    f"Invalid file extension. Expected .xlsx or .xls, got {source_path.suffix}",
                    "",
                )

            # Generate target path with conflict resolution
            target_path = self._generate_unique_target_path(source_path)

            # Copy file
            shutil.copy2(source_path, target_path)

            # Verify copy was successful
            if not target_path.exists():
                return False, f"File copy verification failed: {target_path}", ""

            logger.info(
                f"Successfully copied Excel file from {source_path} to {target_path}"
            )
            return True, f"Successfully copied to: {target_path}", str(target_path)

        except PermissionError:
            return (
                False,
                "Permission denied when copying file. Check file permissions.",
                "",
            )
        except shutil.SameFileError:
            return (
                False,
                "Source and target files are the same. Cannot copy to same location.",
                "",
            )
        except Exception as e:
            logger.error(f"Unexpected error copying file: {e}")
            return False, f"Unexpected error copying file: {str(e)}", ""

    def _generate_unique_target_path(self, source_path: Path) -> Path:
        """
        Generate a unique target path in the spreadsheet directory.

        Args:
            source_path: Original source file path

        Returns:
            Unique target path for the copied file
        """
        base_name = source_path.stem
        extension = source_path.suffix.lower()

        target_path = self.spreadsheet_dir / f"{base_name}{extension}"
        counter = 1

        # Keep incrementing until we find an unused filename
        while target_path.exists():
            new_name = f"{base_name}_{counter}{extension}"
            target_path = self.spreadsheet_dir / new_name
            counter += 1

        return target_path

    def validate_hpm_excel_structure(self, excel_path: str) -> Tuple[bool, str]:
        """
        Comprehensive validation of Excel file for HPM project requirements.

        Args:
            excel_path: Path to the Excel file to validate

        Returns:
            Tuple of (is_valid: bool, message: str)

        Validates:
        - File can be read by pandas
        - File has minimum required rows (at least 4 rows)
        - Row 3 contains all required HPM mapping headers
        - Basic data structure compatibility
        """
        try:
            excel_path = Path(excel_path)

            # Check file exists and has correct extension
            if not excel_path.exists():
                return False, f"Excel file does not exist: {excel_path}"

            if excel_path.suffix.lower() not in [".xlsx", ".xls"]:
                return (
                    False,
                    f"Invalid file extension. Expected .xlsx or .xls, got {excel_path.suffix}",
                )

            # Try to read the Excel file
            try:
                # Read first 10 rows to validate structure without loading entire file
                df = pd.read_excel(
                    excel_path,
                    nrows=10,
                    engine="openpyxl"
                    if excel_path.suffix.lower() == ".xlsx"
                    else "xlrd",
                )
            except Exception as e:
                return False, f"Cannot read Excel file: {str(e)}"

            # Check minimum required rows
            if len(df) < 4:
                return (
                    False,
                    f"Excel file has insufficient rows. Expected at least 4 rows, found {len(df)}. Required: Row 1 (headers), Row 2 (batch title), Row 3 (mapping), Row 4+ (data)",
                )

            # Validate Row 3 mapping headers (index 2)
            required_mapping_headers = [
                "Title",
                "Accession Number",
                "Restrictions",
                "Scopenote",
                "Related Collection",
                "Source Photographer",
                "Institutional Creator",
            ]

            try:
                # Get Row 3 headers and clean them
                row3_headers = df.iloc[2].fillna("").astype(str).str.strip().tolist()

                # Check for required headers (case-insensitive)
                missing_headers = []
                for required_header in required_mapping_headers:
                    if not any(
                        required_header.lower() == header.lower()
                        for header in row3_headers
                    ):
                        missing_headers.append(required_header)

                if missing_headers:
                    return False, (
                        f"Missing required Row 3 headers: {', '.join(missing_headers)}\\n"
                        f"Found headers: {', '.join(row3_headers)}\\n"
                        f"Required headers: {', '.join(required_mapping_headers)}"
                    )

            except Exception as e:
                return False, f"Error validating Row 3 structure: {str(e)}"

            # Basic data validation on first few data rows
            try:
                if len(df) >= 4:
                    # Check if data rows have some content
                    first_data_row = df.iloc[3].fillna("").astype(str).tolist()
                    if not any(val.strip() for val in first_data_row):
                        return (
                            False,
                            "No data found in Row 4. Expected metadata data starting from Row 4.",
                        )
            except Exception:
                pass  # This is not critical, so we don't fail on this validation

            logger.info(f"Excel file structure validation passed: {excel_path}")
            return True, "Excel file structure is valid for HPM processing"

        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            return False, f"Unexpected validation error: {str(e)}"

    def get_copied_files_list(self) -> List[str]:
        """
        Get list of Excel files copied to the spreadsheet directory.

        Returns:
            List of file paths (relative to spreadsheet directory)
        """
        try:
            if not self.spreadsheet_dir.exists():
                return []

            excel_files = []
            for file_path in self.spreadsheet_dir.glob("*.xlsx"):
                excel_files.append(file_path.name)

            for file_path in self.spreadsheet_dir.glob("*.xls"):
                excel_files.append(file_path.name)

            return sorted(excel_files)

        except Exception as e:
            logger.error(f"Error listing Excel files: {e}")
            return []

    def remove_copied_file(self, filename: str) -> Tuple[bool, str]:
        """
        Remove a copied Excel file from the spreadsheet directory.

        Args:
            filename: Name of the file to remove

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            file_path = self.spreadsheet_dir / filename

            if not file_path.exists():
                return False, f"File does not exist: {filename}"

            os.remove(file_path)
            logger.info(f"Removed Excel file: {file_path}")
            return True, f"Successfully removed: {filename}"

        except Exception as e:
            logger.error(f"Error removing file {filename}: {e}")
            return False, f"Error removing file: {str(e)}"

    def get_latest_file_info(self) -> Optional[dict]:
        """
        Get information about the most recently copied Excel file.

        Returns:
            Dictionary with file info or None if no files found
        """
        try:
            excel_files = list(self.spreadsheet_dir.glob("*.xlsx")) + list(
                self.spreadsheet_dir.glob("*.xls")
            )

            if not excel_files:
                return None

            # Sort by modification time to get the latest
            latest_file = max(excel_files, key=lambda f: f.stat().st_mtime)

            return {
                "name": latest_file.name,
                "path": str(latest_file),
                "size": latest_file.stat().st_size,
                "modified": latest_file.stat().st_mtime,
            }

        except Exception as e:
            logger.error(f"Error getting latest file info: {e}")
            return None


def create_file_manager(project_data_dir: str) -> FileManager:
    """
    Factory function to create FileManager instance.

    Args:
        project_data_dir: Path to the project data directory

    Returns:
        FileManager instance
    """
    return FileManager(project_data_dir)


# Standalone functions for backward compatibility
def copy_excel_to_input(
    source_path: str, project_data_dir: str
) -> Tuple[bool, str, str]:
    """
    Standalone function to copy Excel file to input directory.

    Args:
        source_path: Path to source Excel file
        project_data_dir: Project data directory

    Returns:
        Tuple of (success: bool, message: str, target_path: str)
    """
    manager = FileManager(project_data_dir)
    return manager.copy_excel_to_input(source_path)


def validate_hpm_excel_structure(excel_path: str) -> Tuple[bool, str]:
    """
    Standalone function to validate Excel file structure.

    Args:
        excel_path: Path to Excel file

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    manager = FileManager("")  # Directory not needed for validation
    return manager.validate_hpm_excel_structure(excel_path)


if __name__ == "__main__":
    # Example usage and testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python file_manager.py <command> [args]")
        print("Commands:")
        print("  validate <excel_path>     - Validate Excel file structure")
        print("  copy <source_path> <data_dir> - Copy Excel file to input directory")
        sys.exit(1)

    command = sys.argv[1]

    if command == "validate":
        if len(sys.argv) < 3:
            print("Usage: python file_manager.py validate <excel_path>")
            sys.exit(1)

        excel_path = sys.argv[2]
        is_valid, message = validate_hpm_excel_structure(excel_path)
        print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
        print(f"Message: {message}")

    elif command == "copy":
        if len(sys.argv) < 4:
            print("Usage: python file_manager.py copy <source_path> <data_dir>")
            sys.exit(1)

        source_path = sys.argv[2]
        data_dir = sys.argv[3]
        success, message, target_path = copy_excel_to_input(source_path, data_dir)
        print(f"Copy: {'SUCCESS' if success else 'FAILED'}")
        print(f"Message: {message}")
        if success:
            print(f"Target: {target_path}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
