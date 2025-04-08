#!/usr/bin/env python3
# Excel to CSV Conversion Script
# This script processes TestMetadataForJim.xlsx by:
# 1. Removing the first 3 rows
# 2. Renaming specified columns
# 3. Exporting to CSV with UTF-8 encoding

import pandas as pd
import os
import sys

def analyze_excel_structure(input_file):
    """Analyze the structure of the Excel file and print debugging information."""
    print("\n=== EXCEL FILE STRUCTURE ANALYSIS ===")
    
    # Read the Excel file without skipping rows
    print(f"Reading file '{input_file}' for analysis...")
    df_debug = pd.read_excel(input_file)
    
    # Print shape information
    print(f"File shape: {df_debug.shape} (rows × columns)")
    
    # Print the first 5 rows to understand structure
    print("\nFirst 5 rows of the Excel file:")
    print(df_debug.head(5).to_string())
    
    # Print all column names
    print("\nColumn names in the file:")
    for i, col in enumerate(df_debug.columns):
        print(f"  Column {i}: {col} (Type: {type(col).__name__})")
    
    # Check for potential header rows
    print("\nExamining potential header rows:")
    for i in range(min(5, len(df_debug))):
        row_content = ' '.join([str(x) for x in df_debug.iloc[i].tolist()])
        print(f"  Row {i}: {row_content[:100]}{'...' if len(row_content) > 100 else ''}")
        if "HST" in row_content and "DRUPAL" in row_content:
            print(f"  --> Potential header row found at index {i}")
    
    print("=== END OF ANALYSIS ===\n")
    return df_debug

def convert_excel_to_csv():
    # Define input and output file paths
    input_file = "Existing Truman Photos Export - 12-7-2023.xlsx"
    output_file = "export.csv"
    
    # Verify input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    try:
        # Step 1: Read Excel file - no skiprows parameter needed
        print(f"Reading file '{input_file}'...")
        df = pd.read_excel(input_file)
        
        # Add debugging information
        print("\nDataFrame columns after loading (exact names):")
        for col in df.columns:
            print(f"  '{col}'")
        
        print("\nFirst row of data:")
        if len(df) > 0:
            print(df.iloc[0].to_string())
        else:
            print("No data rows found")
        
        # Drop any NaN columns and rows with all NaN
        df = df.dropna(axis=1, how='all')
        
        # Print information about loaded data
        print(f"\nDataFrame shape after dropping empty columns: {df.shape} rows × {len(df.columns)} columns")
        if df.empty:
            print("Error: DataFrame is empty after loading!")
            return False
        
        # Step 2: Define direct column mappings based on file analysis
        print("Setting up column mappings...")
        
        # These mappings are based on our file analysis
        # These mappings are based on our file analysis
        direct_mapping = {
            'title': 'Headline',
            'localIdentifier': 'ObjectName',
            'useRestriction.status': 'CopyrightNotice',
            'scopeAndContentNote': 'Caption-Abstract', 
            'physicalOccurrences.0.mediaOccurrences.0.specificMediaType': 'Source',
            'contributors.0.heading': 'By-line',
            'physicalOccurrences.0.copyStatus': 'By-lineTitle'
        }
        # Check for missing columns
        missing_columns = [col for col in direct_mapping.keys() if col not in df.columns]
        if missing_columns:
            print(f"Warning: The following columns were not found in the file: {', '.join(missing_columns)}")
            print("Available columns:", ', '.join(df.columns.tolist()))
            proceed = input("Continue anyway with available columns? (y/n): ")
            if proceed.lower() != 'y':
                return False
        
        # Step 3: Apply renaming only for columns that exist and create new DataFrame with only those columns
        new_df = pd.DataFrame()
        renamed_columns = []
        
        for src_col, dst_col in direct_mapping.items():
            if src_col in df.columns:
                new_df[dst_col] = df[src_col]
                renamed_columns.append(f"'{src_col}' -> '{dst_col}'")
                print(f"Mapped: '{src_col}' -> '{dst_col}'")
            else:
                print(f"Skipped: '{src_col}' (not found in source data)")
        
        # Verify we have data to export
        if new_df.empty:
            print("Error: No columns were successfully mapped!")
            return False
            
        print(f"\nSuccessfully mapped {len(renamed_columns)} columns:")
        for mapping in renamed_columns:
            print(f"  {mapping}")
        
        # Step 4: Export to CSV with UTF-8 encoding
        print(f"\nExporting to '{output_file}' with UTF-8 encoding...")
        new_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"Conversion completed successfully. Output saved to '{output_file}'")
        print(f"Rows processed: {len(new_df)}")
        return True
    
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

if __name__ == "__main__":
    print("Excel to CSV Conversion Tool")
    print("----------------------------")
    # Check if analysis is requested
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--analyze":
        print("Running file structure analysis...")
        analyze_excel_structure("Existing Truman Photos Export - 12-7-2023.xlsx")
        sys.exit(0)
    else:
        success = convert_excel_to_csv()
        sys.exit(0 if success else 1)

