#!/usr/bin/env python3
"""
Excel to CSV Converter with IPTC Mapping

This script converts Excel spreadsheets to CSV format with IPTC metadata mapping:
1. Read Excel files from standardized input location
2. Map data to IPTC metadata fields using specialized mapping logic
3. Export the mapped data to CSV format

Features:
- Excel file reading with proper structure validation
- Enhanced error handling with specific solutions
- Support for both .xlsx and .xls Excel formats
- Specialized IPTC metadata field mapping
- ISO date formatting
- Detailed data validation and reporting
- File copying and management for HPM projects

Usage:
    python g2c.py [--excel-file PATH] [--export-csv [FILENAME]]

Options:
    --excel-file, -f           Path to the Excel file (default: input/spreadsheet/metadata.xlsx)
    --export-csv, -e [FILENAME] Export data to CSV file (default: export.csv)
"""

import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class NonStandardDateRecord:
    """Record tracking a non-standard date found during CSV export."""
    row_num: int
    object_name: str
    date_value: str
    date_type: str  # "partial" or "placeholder"
    source: str     # "productionDate", "coverageStartDate", or "fallback"
    reason: str = ""  # Why the date is non-standard (for placeholder: "no date data", "invalid: ...")


@dataclass
class CSVExportResult:
    """Result of CSV export operation including non-standard date tracking."""
    success: bool
    production_count: int = 0
    coverage_count: int = 0
    nonstandard_dates: List[NonStandardDateRecord] = field(default_factory=list)

# === CONFIG ===
# Default Excel file path for HPM projects
DEFAULT_EXCEL_PATH = "input/spreadsheet/metadata.xlsx"

# === TARGET EXCEL FILE ===
# Default Excel file to use if none provided via command line


def read_excel_file(excel_path=DEFAULT_EXCEL_PATH):
    """
    Read Excel file from standardized location and return pandas DataFrame with same structure as Google Sheets.

    Args:
        excel_path: Path to the Excel file to read

    Returns:
        pandas.DataFrame: Data from the Excel file with proper formatting

    Raises:
        Exception: If file cannot be read or doesn't exist
    """
    try:
        excel_path = Path(excel_path)

        # Check if file exists
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        # Determine the appropriate engine based on file extension
        engine = "openpyxl" if excel_path.suffix.lower() == ".xlsx" else "xlrd"

        print(f"Reading Excel file: {excel_path}")
        print(f"Using engine: {engine}")

        # Read the Excel file
        df = pd.read_excel(excel_path, engine=engine)

        if df.empty:
            raise ValueError("Excel file is empty or has no readable data")

        print(
            f"Successfully read Excel file with {len(df)} rows and {len(df.columns)} columns"
        )

        return df

    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise


def print_dataframe_summary(df):
    """
    Print a summary of the DataFrame including shape, columns, and first few rows.

    Args:
        df: pandas DataFrame to summarize
    """
    if df is None:
        print("No DataFrame to summarize.")
        return

    print("\n=== DataFrame Summary ===")
    print(f"Shape: {df.shape} (rows, columns)")
    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")

    print("\nFirst 5 rows:")
    print(df.head())

    # Additional summary info
    print("\nData types:")
    print(df.dtypes)


def print_first_10_rows(df):
    """
    Print the first 10 rows of the DataFrame to the console with all columns visible.

    Args:
        df: pandas DataFrame to print
    """
    if df is None:
        print("No DataFrame to print.")
        return

    print("\n=== First 10 Rows (All Columns) ===")
    try:
        # Use option_context to temporarily override display settings
        with pd.option_context(
            "display.max_columns",
            None,
            "display.width",
            1000,
            "display.max_rows",
            10,
            "display.max_colwidth",
            100,
        ):
            print(df.head(10))
    except Exception as e:
        print(f"Warning: Could not display full data preview: {e}")
        print("Displaying simplified view:")
        print(df.head(10).to_string(max_cols=10, max_rows=10))


def clean_encoding_artifacts(text):
    """
    Clean common UTF-8 encoding artifacts that appear when UTF-8 text is
    misinterpreted as Windows-1252 or ISO-8859-1.

    Args:
        text: String that may contain encoding artifacts

    Returns:
        str: Cleaned text with artifacts removed
    """
    if not isinstance(text, str) or not text:
        return text

    # Common UTF-8 to Windows-1252 misinterpretation artifacts
    # These are the byte sequences that result from double-encoding
    artifacts = {
        "Ã±": "ñ",  # Spanish ñ
        "Ã¡": "á",  # Spanish á
        "Ã©": "é",  # Spanish é
        "Ã­": "í",  # Spanish í
        "Ã³": "ó",  # Spanish ó
        "Ãº": "ú",  # Spanish ú
        "Ã¼": "ü",  # German ü
        "Ã¤": "ä",  # German ä
        "Ã¶": "ö",  # German ö
        "Ã ": "à",  # French à
        "Ã¨": "è",  # French è
        "Ã§": "ç",  # French ç
        "Ã¢": "â",  # French â
        "Ã™": "Ù",  # Capital U with grave
        "Â": "",  # Often appears as stray character
        "â€™": "'",  # Right single quotation mark
        "â€œ": '"',  # Left double quotation mark
        "â€\u009d": '"',  # Right double quotation mark
        "â€“": "–",  # En dash
        "â€”": "—",  # Em dash
        "â€¦": "...",  # Horizontal ellipsis
    }

    # Apply artifact replacements
    cleaned_text = text
    for artifact, replacement in artifacts.items():
        cleaned_text = cleaned_text.replace(artifact, replacement)

    # Remove other common non-printable artifacts
    # Remove null bytes and other control characters except newlines and tabs
    cleaned_text = "".join(
        char for char in cleaned_text if ord(char) >= 32 or char in "\n\t"
    )

    return cleaned_text


def clean_dataframe_encoding(df):
    """
    Clean encoding artifacts from all string columns in a DataFrame.

    Args:
        df: pandas DataFrame to clean

    Returns:
        pandas.DataFrame: DataFrame with cleaned text
    """
    if df is None or df.empty:
        return df

    df_cleaned = df.copy()

    for column in df_cleaned.columns:
        # Check if column contains string data
        if df_cleaned[column].dtype == "object":
            # Apply cleaning to each cell in the column
            df_cleaned[column] = (
                df_cleaned[column]
                .astype(str)
                .apply(lambda x: clean_encoding_artifacts(x) if x != "nan" else x)
            )

    return df_cleaned


def export_to_csv(df, output_file="export.csv"):
    """
    Export DataFrame to CSV with mapped column names and cleaned encoding.

    Args:
        df: pandas DataFrame to export
        output_file: name of the output CSV file

    Returns:
        CSVExportResult: Result object with success status and non-standard date tracking
    """
    if df is None or df.empty:
        print("Error: No data to export.")
        return CSVExportResult(success=False)

    try:
        print(f"\n=== Exporting Data to CSV: {output_file} ===")

        # Define the row 3 content to export header mapping
        row3_mapping = {
            "Title": "Headline",
            "Accession Number": "ObjectName",
            "Restrictions": "CopyrightNotice",
            "Scopenote": "Caption-Abstract",
            "Related Collection": "Source",
            "Source Photographer": "By-line",
            "Institutional Creator": "By-lineTitle",
        }

        # Create a mapping from column names to export headers based on row 3 content
        # Row 3 is at index 2 (0-based indexing)
        row3_index = 2
        column_to_export_header = {}

        # Only proceed if we have enough rows
        if len(df) <= row3_index:
            print(
                f"Error: DataFrame has only {len(df)} rows, but we need at least {row3_index + 1} rows."
            )
            return False

        # Find which columns have the values we're looking for in row 3
        print("\nDebug - Row 3 cell values:")
        for col in df.columns:
            cell_value = (
                str(df.loc[row3_index, col]).strip()
                if pd.notna(df.loc[row3_index, col])
                else ""
            )
            print(f"Column '{col}' contains: '{cell_value}'")
            # Case-insensitive matching for robustness
            if cell_value in row3_mapping:
                column_to_export_header[col] = row3_mapping[cell_value]
                print(f"Matched '{cell_value}' to '{row3_mapping[cell_value]}'")
            # Handle any variations in 'Related Collection' text
            elif cell_value and (
                "related collection" in cell_value.lower()
                or "related" in cell_value.lower()
                and "collection" in cell_value.lower()
            ):
                print(f"Found potential 'Related Collection' match: '{cell_value}'")
                column_to_export_header[col] = "Source"
                print(f"Mapping '{cell_value}' to 'Source'")

        # Report which row 3 values we couldn't find
        found_values = [
            val for col, val in df.iloc[row3_index].items() if val in row3_mapping
        ]
        missing_values = [val for val in row3_mapping.keys() if val not in found_values]

        if missing_values:
            print(
                f"Warning: The following row 3 values were not found in the data: {', '.join(missing_values)}"
            )
            print(
                "Available row 3 values:",
                ", ".join([str(val) for val in df.iloc[row3_index] if pd.notna(val)]),
            )
            print("Continuing with available mappings...")

        # Track non-standard dates for reporting
        nonstandard_dates: List[NonStandardDateRecord] = []

        # Clean encoding artifacts from the original DataFrame before processing
        print("\nCleaning encoding artifacts...")
        df_cleaned = clean_dataframe_encoding(df)

        # Create new DataFrame with mapped columns
        new_df = pd.DataFrame()
        renamed_columns = []

        for src_col, dst_col in column_to_export_header.items():
            # Copy the column data from cleaned DataFrame
            new_df[dst_col] = df_cleaned[src_col]
            renamed_columns.append(
                f"'{src_col}' (row 3: '{df.loc[row3_index, src_col]}') -> '{dst_col}'"
            )
            print(
                f"Mapped: '{src_col}' (row 3: '{df.loc[row3_index, src_col]}') -> '{dst_col}'"
            )

        # Add DateCreated column in ISO format (YYYY-MM-DD)
        # Primary source: productionDateMonth, productionDateDay, productionDateYear
        # Fallback source: coverageStartDateMonth, coverageStartDateDay, coverageStartDateYear
        try:
            # Initialize an empty date column the same length as the DataFrame
            new_df["DateCreated"] = ""

            production_cols = ["productionDateMonth", "productionDateDay", "productionDateYear"]
            coverage_cols = ["coverageStartDateMonth", "coverageStartDateDay", "coverageStartDateYear"]

            has_production_cols = all(col in df_cleaned.columns for col in production_cols)
            has_coverage_cols = all(col in df_cleaned.columns for col in coverage_cols)

            if has_production_cols:
                print("Creating 'DateCreated' column from productionDate columns...")
            elif has_coverage_cols:
                print("Creating 'DateCreated' column from coverageStartDate columns (productionDate not available)...")
            else:
                print("Warning: Neither productionDate nor coverageStartDate columns found.")

            # Helper function to extract and validate date from columns
            # Supports partial dates: missing components become "00" (e.g., "1947-00-00" for year-only)
            # Returns tuple: (date_string, is_partial, reject_reason)
            #   reject_reason is "" on success, or a description of why the date was rejected
            def get_date_from_columns(idx, month_col, day_col, year_col):
                """Extract and validate date components, return tuple (ISO date string, is_partial, reject_reason).

                Supports partial dates where missing components are represented as "00".
                Returns ("", False, reason) if date is missing or invalid.
                is_partial is True if the date has any "00" components (year, month, or day).
                """
                try:
                    month_str = (
                        str(df_cleaned.loc[idx, month_col]).strip()
                        if df_cleaned.loc[idx, month_col] is not None
                        else ""
                    )
                    day_str = (
                        str(df_cleaned.loc[idx, day_col]).strip()
                        if df_cleaned.loc[idx, day_col] is not None
                        else ""
                    )
                    year_str = (
                        str(df_cleaned.loc[idx, year_col]).strip()
                        if df_cleaned.loc[idx, year_col] is not None
                        else ""
                    )

                    # Replace 'nan', 'None', or 'NaN' strings with empty string
                    month_str = "" if month_str.lower() in ["nan", "none", "null"] else month_str
                    day_str = "" if day_str.lower() in ["nan", "none", "null"] else day_str
                    year_str = "" if year_str.lower() in ["nan", "none", "null"] else year_str

                    # Helper to format raw values for reject reason
                    def raw_values_str():
                        parts = []
                        parts.append(f"M={month_str}" if month_str else "M=")
                        parts.append(f"D={day_str}" if day_str else "D=")
                        parts.append(f"Y={year_str}" if year_str else "Y=")
                        return " ".join(parts)

                    # Helper to safely convert string to int, handling float strings (e.g., "1975.0" from Excel)
                    def safe_int(s):
                        """Convert string to int, handling float strings. Returns None if invalid."""
                        if not s:
                            return 0
                        try:
                            # Try direct int conversion first
                            return int(s)
                        except ValueError:
                            try:
                                # Handle float strings like "1975.0"
                                return int(float(s))
                            except (ValueError, TypeError):
                                return None

                    # Extract numeric values, returning rejection reason if any component is invalid
                    year_int = safe_int(year_str)
                    if year_int is None:
                        return ("", False, f"invalid date ({raw_values_str()})")

                    month_int = safe_int(month_str)
                    if month_int is None:
                        return ("", False, f"invalid date ({raw_values_str()})")

                    day_int = safe_int(day_str)
                    if day_int is None:
                        return ("", False, f"invalid date ({raw_values_str()})")

                    # If no components present at all, return empty string
                    if year_int == 0 and month_int == 0 and day_int == 0:
                        return ("", False, "no date data")

                    # Apply range validation only to present (non-zero) components
                    if year_int != 0 and year_int <= 0:
                        return ("", False, f"invalid date ({raw_values_str()})")
                    if month_int != 0 and not (1 <= month_int <= 12):
                        return ("", False, f"invalid date ({raw_values_str()})")
                    if day_int != 0 and not (1 <= day_int <= 31):
                        return ("", False, f"invalid date ({raw_values_str()})")

                    # Check if this is a partial date (any component is 0/missing)
                    is_partial = (year_int == 0 or month_int == 0 or day_int == 0)

                    # Format with zero-padded components
                    return (f"{year_int:04d}-{month_int:02d}-{day_int:02d}", is_partial, "")
                except Exception:
                    pass
                return ("", False, "no date data")

            # Skip the first 3 rows which contain header information
            # Start processing from index 3 (4th row) onwards
            production_count = 0
            coverage_count = 0

            # Find ObjectName column for tracking non-standard dates
            object_name_col = None
            for col, export_col in column_to_export_header.items():
                if export_col == "ObjectName":
                    object_name_col = col
                    break

            for idx in range(3, len(df_cleaned)):
                date_value = ""
                date_source = ""
                is_partial = False
                prod_reason = ""
                cov_reason = ""

                # Get ObjectName for this row (for non-standard date reporting)
                object_name = ""
                if object_name_col and pd.notna(df_cleaned.loc[idx, object_name_col]):
                    object_name = str(df_cleaned.loc[idx, object_name_col]).strip()

                # Try productionDate columns first
                if has_production_cols:
                    date_value, is_partial, prod_reason = get_date_from_columns(
                        idx,
                        "productionDateMonth",
                        "productionDateDay",
                        "productionDateYear"
                    )
                    if date_value:
                        production_count += 1
                        date_source = "productionDate"

                # If still empty, try coverageStartDate columns as fallback
                if not date_value and has_coverage_cols:
                    date_value, is_partial, cov_reason = get_date_from_columns(
                        idx,
                        "coverageStartDateMonth",
                        "coverageStartDateDay",
                        "coverageStartDateYear"
                    )
                    if date_value:
                        coverage_count += 1
                        date_source = "coverageStartDate"

                # If still no date from either source, use placeholder
                if not date_value:
                    date_value = "0000-00-00"
                    date_source = "fallback"

                new_df.loc[idx, "DateCreated"] = date_value

                # Track non-standard dates (partial or placeholder)
                # Since idx starts at 3 and represents Excel row, display as idx + 1 for user-friendly numbering
                row_num = idx + 1  # Convert to 1-based row number
                if date_value == "0000-00-00":
                    # Build reason from rejection reasons of both sources
                    # Use the most informative reason (prefer invalid over no data)
                    reason = ""
                    if prod_reason and prod_reason != "no date data":
                        reason = f"productionDate: {prod_reason}"
                    if cov_reason and cov_reason != "no date data":
                        if reason:
                            reason += f"; coverageStartDate: {cov_reason}"
                        else:
                            reason = f"coverageStartDate: {cov_reason}"
                    if not reason:
                        reason = "no date data"

                    nonstandard_dates.append(NonStandardDateRecord(
                        row_num=row_num,
                        object_name=object_name,
                        date_value=date_value,
                        date_type="placeholder",
                        source=date_source,
                        reason=reason
                    ))
                elif is_partial:
                    nonstandard_dates.append(NonStandardDateRecord(
                        row_num=row_num,
                        object_name=object_name,
                        date_value=date_value,
                        date_type="partial",
                        source=date_source
                    ))

            print(f"Added 'DateCreated' column with ISO formatted dates (YYYY-MM-DD)")
            if production_count > 0:
                print(f"  - {production_count} dates from productionDate columns")
            if coverage_count > 0:
                print(f"  - {coverage_count} dates from coverageStartDate columns (fallback)")

        except Exception as e:
            print(f"Error creating 'DateCreated' column: {str(e)}")

        # Verify we have data to export
        if new_df.empty:
            print("Error: No columns were successfully mapped!")
            return CSVExportResult(success=False)

        print(f"\nSuccessfully mapped {len(renamed_columns)} columns:")
        for mapping in renamed_columns:
            print(f"  {mapping}")

        # Export to CSV with UTF-8 encoding
        print(f"\nExporting to '{output_file}' with UTF-8 encoding...")
        new_df.to_csv(output_file, index=False, encoding="utf-8")

        print(f"Conversion completed successfully. Output saved to '{output_file}'")
        print(f"Rows processed: {len(new_df)}")

        # Report non-standard dates summary
        if nonstandard_dates:
            partial_count = sum(1 for d in nonstandard_dates if d.date_type == "partial")
            placeholder_count = sum(1 for d in nonstandard_dates if d.date_type == "placeholder")
            print(f"Non-standard dates found: {len(nonstandard_dates)} total ({partial_count} partial, {placeholder_count} placeholder)")

        return CSVExportResult(
            success=True,
            production_count=production_count,
            coverage_count=coverage_count,
            nonstandard_dates=nonstandard_dates
        )

    except Exception as e:
        print(f"Error during CSV export: {str(e)}")
        return CSVExportResult(success=False)


def main():
    """Main function to execute the script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Convert Excel spreadsheets to CSV with IPTC metadata mapping for HPM system.",
        epilog="""
Examples:
  # Use default Excel file
  python g2c.py
  
  # Specify Excel file
  python g2c.py --excel-file "/path/to/metadata.xlsx"
  
  # Export to CSV with custom filename
  python g2c.py --excel-file "metadata.xlsx" --export-csv custom_output.csv
""",
    )

    # Add arguments
    parser.add_argument(
        "--excel-file",
        "-f",
        default=DEFAULT_EXCEL_PATH,
        help="Path to the Excel file (default: input/spreadsheet/metadata.xlsx)",
    )

    parser.add_argument(
        "--export-csv",
        "-e",
        nargs="?",
        const="export.csv",
        help="Export data to CSV file (default filename: export.csv)",
    )

    # Parse arguments
    args = parser.parse_args()

    print("Excel to CSV Converter with IPTC Mapping")
    print("=" * 60)
    print("Converting Excel spreadsheets for HPM processing")
    print()

    # Read Excel file
    try:
        excel_path = args.excel_file
        print(f"Reading Excel file: {excel_path}")
        df = read_excel_file(excel_path)

    except FileNotFoundError:
        print(f"\nERROR: Excel file not found: {excel_path}")
        print("Please ensure the Excel file exists at the specified path.")
        print(f"Default location: {DEFAULT_EXCEL_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Error reading Excel file: {e}")
        print(
            "Please check the file format and ensure it's a valid .xlsx or .xls file."
        )
        sys.exit(1)

    if df is not None:
        print("\nSUCCESS: Data loaded successfully!")
        print_dataframe_summary(df)
        print_first_10_rows(df)

        # Export to CSV if requested
        if args.export_csv:
            output_file = args.export_csv
            result = export_to_csv(df, output_file)
            if not result.success:
                print(f"Warning: CSV export failed")
            elif result.nonstandard_dates:
                # Print detailed non-standard dates report for CLI
                print("\n" + "=" * 50)
                print("NON-STANDARD DATES REPORT")
                print("=" * 50)

                partial_dates = [d for d in result.nonstandard_dates if d.date_type == "partial"]
                placeholder_dates = [d for d in result.nonstandard_dates if d.date_type == "placeholder"]

                if partial_dates:
                    print(f"\nPartial Dates ({len(partial_dates)}):")
                    for d in partial_dates:
                        print(f"  Row {d.row_num}: {d.object_name} - \"{d.date_value}\" (from {d.source})")

                if placeholder_dates:
                    print(f"\nPlaceholder Dates ({len(placeholder_dates)}):")
                    for d in placeholder_dates:
                        print(f"  Row {d.row_num}: {d.object_name} - \"{d.date_value}\" [{d.reason}]")

        # Show success message
        print(f"\nSUCCESS: Excel file processed successfully.")
        print(f"Original file remains unchanged")
        print(f"Data ready for HPM processing")

    else:
        print("\nERROR: Failed to load data from the Excel file.")
        print("Please check the file format and ensure it contains valid data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
