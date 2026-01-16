#!/usr/bin/env python3
"""
Excel Validation Module for HST Photo Metadata System

This module provides specialized validation functions for Excel files
used in the HST Photo Metadata system. It focuses on structure validation
and HPM-specific requirements.

Author: HPM Development Team
Version: 1.0.0
"""

import logging
from typing import Tuple, List, Dict, Any
import pandas as pd

# Configure module logger
logger = logging.getLogger(__name__)


class ExcelValidator:
    """Specialized validator for HPM Excel files."""

    # Required Row 3 mapping headers
    REQUIRED_MAPPING_HEADERS = [
        "Title",
        "Accession Number",
        "Restrictions",
        "Scopenote",
        "Related Collection",
        "Source Photographer",
        "Institutional Creator",
    ]

    # HPM IPTC field mapping (from g2c.py)
    HPM_IPTC_MAPPING = {
        "Title": "Headline",
        "Accession Number": "ObjectName",
        "Restrictions": "CopyrightNotice",
        "Scopenote": "Caption-Abstract",
        "Related Collection": "Source",
        "Source Photographer": "By-line",
        "Institutional Creator": "By-lineTitle",
    }

    def __init__(self):
        """Initialize ExcelValidator."""
        pass

    def validate_file_structure(
        self, excel_path: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Comprehensive validation of Excel file structure.

        Args:
            excel_path: Path to Excel file to validate

        Returns:
            Tuple of (is_valid: bool, message: str, details: dict)
        """
        details = {
            "file_exists": False,
            "file_extension": "",
            "row_count": 0,
            "column_count": 0,
            "row3_headers": [],
            "missing_headers": [],
            "validation_steps": [],
        }

        try:
            import os
            from pathlib import Path

            # Check file exists
            if not os.path.exists(excel_path):
                details["validation_steps"].append("File existence check: FAILED")
                return False, f"File does not exist: {excel_path}", details

            details["file_exists"] = True
            details["validation_steps"].append("File existence check: PASSED")

            # Check file extension
            excel_path_obj = Path(excel_path)
            extension = excel_path_obj.suffix.lower()
            details["file_extension"] = extension

            if extension not in [".xlsx", ".xls"]:
                details["validation_steps"].append("File extension check: FAILED")
                return (
                    False,
                    f"Invalid file extension: {extension}. Expected .xlsx or .xls",
                    details,
                )

            details["validation_steps"].append("File extension check: PASSED")

            # Read Excel file
            try:
                engine = "openpyxl" if extension == ".xlsx" else "xlrd"
                df = pd.read_excel(excel_path, nrows=10, engine=engine)
            except Exception as e:
                details["validation_steps"].append(
                    f"Excel file reading: FAILED - {str(e)}"
                )
                return False, f"Cannot read Excel file: {str(e)}", details

            details["row_count"] = len(df)
            details["column_count"] = len(df.columns)
            details["validation_steps"].append("Excel file reading: PASSED")

            # Validate row count
            if len(df) < 4:
                details["validation_steps"].append(
                    f"Row count check: FAILED - {len(df)} < 4"
                )
                return (
                    False,
                    (
                        f"Insufficient rows: {len(df)}. "
                        f"Expected at least 4 rows (headers, blank, mapping, data)."
                    ),
                    details,
                )

            details["validation_steps"].append("Row count check: PASSED")

            # Validate Row 3 structure
            row3_valid, row3_message, row3_details = self._validate_row3_structure(df)
            details.update(row3_details)

            if not row3_valid:
                details["validation_steps"].append(f"Row 3 structure check: FAILED")
                return False, row3_message, details

            details["validation_steps"].append("Row 3 structure check: PASSED")

            # Validate Row 2 is blank
            row2_valid, row2_message = self._validate_row2_blank(df)
            if not row2_valid:
                details["validation_steps"].append(f"Row 2 blank check: FAILED")
                return False, row2_message, details

            details["validation_steps"].append("Row 2 blank check: PASSED")

            # Validate data rows have content
            data_valid, data_message = self._validate_data_rows(df)
            if not data_valid:
                details["validation_steps"].append(f"Data rows validation: FAILED")
                return False, data_message, details

            details["validation_steps"].append("Data rows validation: PASSED")

            logger.info(f"Excel file validation successful: {excel_path}")
            return True, "Excel file structure is valid for HPM processing", details

        except Exception as e:
            details["validation_steps"].append(f"Unexpected error: FAILED - {str(e)}")
            logger.error(f"Unexpected validation error: {e}")
            return False, f"Unexpected validation error: {str(e)}", details

    def _validate_row3_structure(
        self, df: pd.DataFrame
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate Row 3 contains required mapping headers.

        Args:
            df: Pandas DataFrame with Excel data

        Returns:
            Tuple of (is_valid: bool, message: str, details: dict)
        """
        details = {"row3_headers": [], "missing_headers": []}

        try:
            # Get Row 3 headers (index 2)
            row3_headers = df.iloc[2].fillna("").astype(str).str.strip().tolist()
            details["row3_headers"] = row3_headers

            # Check for required headers (case-insensitive)
            missing_headers = []
            for required_header in self.REQUIRED_MAPPING_HEADERS:
                found = any(
                    required_header.lower() == header.lower() for header in row3_headers
                )
                if not found:
                    missing_headers.append(required_header)

            details["missing_headers"] = missing_headers

            if missing_headers:
                message = (
                    f"Missing required Row 3 headers: {', '.join(missing_headers)}\\n"
                    f"Found: {', '.join(h for h in row3_headers if h)}\\n"
                    f"Required: {', '.join(self.REQUIRED_MAPPING_HEADERS)}"
                )
                return False, message, details

            return True, "Row 3 headers validation passed", details

        except Exception as e:
            return False, f"Error validating Row 3: {str(e)}", details

    def _validate_row2_blank(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate Row 2 is blank as expected by HPM structure.

        Args:
            df: Pandas DataFrame with Excel data

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            if len(df) >= 2:
                row2_values = df.iloc[1].fillna("").astype(str).str.strip().tolist()
                non_empty_values = [val for val in row2_values if val.strip()]

                if non_empty_values:
                    return False, (
                        f"Row 2 should be blank for proper HPM structure. "
                        f"Found non-empty values: {', '.join(non_empty_values[:3])}"
                    )

            return True, "Row 2 is properly blank"

        except Exception as e:
            return False, f"Error validating Row 2: {str(e)}"

    def _validate_data_rows(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate that data rows contain some content.

        Args:
            df: Pandas DataFrame with Excel data

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            if len(df) >= 4:
                # Check first few data rows for content
                for i in range(3, min(6, len(df))):  # Check rows 4-6 (indices 3-5)
                    row_data = df.iloc[i].fillna("").astype(str).tolist()
                    has_content = any(val.strip() for val in row_data)

                    if has_content:
                        return True, "Data rows contain expected content"

            return False, "No data content found in expected data rows (Row 4+)"

        except Exception as e:
            return False, f"Error validating data rows: {str(e)}"

    def generate_validation_report(self, excel_path: str) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.

        Args:
            excel_path: Path to Excel file

        Returns:
            Detailed validation report dictionary
        """
        is_valid, message, details = self.validate_file_structure(excel_path)

        report = {
            "file_path": excel_path,
            "validation_timestamp": pd.Timestamp.now().isoformat(),
            "is_valid": is_valid,
            "summary_message": message,
            "details": details,
            "recommendations": self._generate_recommendations(details)
            if not is_valid
            else [],
        }

        return report

    def _generate_recommendations(self, details: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation failures."""
        recommendations = []

        # Check for missing headers
        if details.get("missing_headers"):
            missing = ", ".join(details["missing_headers"])
            recommendations.append(f"Add missing Row 3 headers: {missing}")

        # Check file extension issues
        if details.get("file_extension") and details["file_extension"] not in [
            ".xlsx",
            ".xls",
        ]:
            recommendations.append("Convert file to .xlsx or .xls format")

        # Check row count issues
        if details.get("row_count", 0) < 4:
            recommendations.append(
                "Add at least 4 rows: headers, blank row, mapping, and data"
            )

        # Check validation steps for common issues
        steps = details.get("validation_steps", [])
        for step in steps:
            if "Row 2 blank check: FAILED" in step:
                recommendations.append(
                    "Clear all content from Row 2 - it should be blank"
                )
            elif "Data rows validation: FAILED" in step:
                recommendations.append("Add metadata data starting from Row 4")

        return recommendations

    def check_required_columns(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Check if DataFrame contains required metadata columns.

        Args:
            df: Pandas DataFrame to check

        Returns:
            Tuple of (has_all_required: bool, missing_columns: list)
        """
        try:
            # Get Row 1 headers (data columns)
            if len(df) > 0:
                data_headers = df.iloc[0].fillna("").astype(str).str.strip().tolist()
            else:
                return False, ["No headers found"]

            # Check for common required HPM metadata columns
            common_required = [
                "Title",
                "Description",
                "Accession Number",
                "Date",
                "Photographer",
            ]
            missing_columns = []

            for required_col in common_required:
                found = any(
                    required_col.lower() in header.lower() for header in data_headers
                )
                if not found:
                    missing_columns.append(required_col)

            return len(missing_columns) == 0, missing_columns

        except Exception as e:
            logger.error(f"Error checking required columns: {e}")
            return False, ["Error checking columns: " + str(e)]


# Standalone functions for backward compatibility
def validate_hpm_excel_structure(excel_path: str) -> Tuple[bool, str]:
    """
    Standalone function to validate HPM Excel file structure.

    Args:
        excel_path: Path to Excel file

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    validator = ExcelValidator()
    is_valid, message, _ = validator.validate_file_structure(excel_path)
    return is_valid, message


def create_excel_validator() -> ExcelValidator:
    """Factory function to create ExcelValidator instance."""
    return ExcelValidator()


if __name__ == "__main__":
    # Example usage and testing
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python excel_validator.py <excel_path> [--report]")
        print("Options:")
        print("  --report  Generate detailed JSON report")
        sys.exit(1)

    excel_path = sys.argv[1]
    generate_report = "--report" in sys.argv

    validator = ExcelValidator()

    if generate_report:
        report = validator.generate_validation_report(excel_path)
        print(json.dumps(report, indent=2, default=str))
    else:
        is_valid, message, details = validator.validate_file_structure(excel_path)
        print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
        print(f"Message: {message}")
        print(
            f"Rows: {details.get('row_count', 0)}, Columns: {details.get('column_count', 0)}"
        )
        if details.get("missing_headers"):
            print(f"Missing Headers: {', '.join(details['missing_headers'])}")
