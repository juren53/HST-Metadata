#!/usr/bin/env python3
"""
Excel to CSV Converter for HST Metadata

This script reads an Excel file containing HST metadata, removes the first 3 rows,
makes the row with "HST - DRUPAL FIELDS" the header row, renames specific columns
according to a predefined mapping, and exports the result to a CSV file.

Usage:
    python process_excel.py
"""

import pandas as pd
import os
import sys
import glob

def select_excel_file():
    """
    Lists all Excel files in the current directory and lets the user select one.
    
    Returns:
        str: The name of the selected Excel file
    """
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get the list of Excel files in the working directory
    excel_files = [file for file in os.listdir() if file.endswith('.xlsx') or file.endswith('.xls')]
    
    if not excel_files:
        print("No Excel files found in the current directory.")
        sys.exit(1)
    
    # Print the list of Excel files
    print("Excel Files in the Working Directory:")
    for i, file in enumerate(excel_files):
        print(f"{i + 1}. {file}")
    
    # Ask the user to select an Excel file
    try:
        selected_file_index = int(input("\nSelect an Excel file (enter the corresponding number): ")) - 1
        if selected_file_index < 0 or selected_file_index >= len(excel_files):
            print("Invalid selection. Please enter a valid number.")
            return select_excel_file()  # Recursive call to try again
        selected_file = excel_files[selected_file_index]
        print(f"\nSelected file: {selected_file}")
        return selected_file
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return select_excel_file()  # Recursive call to try again

def is_string_column(series):
    """
    Check if a pandas Series contains string data.
    
    Args:
        series: A pandas Series object
        
    Returns:
        bool: True if the series contains string data
    """
    return series.dtypes == 'object' or series.dtypes == 'string'

def process_excel_file(input_file, output_file="export.csv"):
    """
    Process the Excel file by removing rows and renaming headers.
    
    Args:
        input_file (str): Name of the input Excel file
        output_file (str): Name of the output CSV file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Print status message
        print(f"Reading Excel file: {input_file}...")
        
        # Read the Excel file into a pandas DataFrame - skip the first 3 rows
        df_raw = pd.read_excel(input_file)
        print(f"Original DataFrame shape: {df_raw.shape}")

        # Display the first few rows for debugging
        print("\nFirst 5 rows of the raw file:")
        for i in range(min(5, len(df_raw))):
            print(f"Row {i}: {df_raw.iloc[i].values}")

        # We want to skip the first 3 rows and use the 4th row as header
        # Read the excel file again but use skiprows to skip the first 3 rows
        # and header=0 to use the first row of the remaining data as header
        df = pd.read_excel(input_file, skiprows=3, header=0)
        print(f"\nDataFrame shape after skipping first 3 rows: {df.shape}")
        
        # Display column headers
        print("\nColumn headers after skipping first 3 rows:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        # Clean up NaN column names
        # Replace NaN column names with 'Column_X'
        new_columns = []
        for i, col in enumerate(df.columns):
            if pd.isna(col) or col == '' or col is None:
                new_columns.append(f'Column_{i}')
            else:
                new_columns.append(col)
        
        df.columns = new_columns
        
        print("\nColumn headers after cleanup:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        # Define a more flexible column mapping with multiple potential matches for each field
        # The first match found will be used
        column_map_options = {
            'Title': ['Title', 'record.title', 'title'],
            'ObjectName': [
                'ObjectName', 'Accession Number', 'Local Identifier', 'localIdentifier', 
                'Record ID', 'ID', 'Object ID', 'Identifier', 'Number'
            ],
            'Restrictions': ['Restrictions', 'Use Restriction Status', 'Copyright', 'Rights'],
            'Scopenote': ['Scopenote', 'Scope and Content Note', 'Description', 'Caption'],
            'Source': ['Related Collection', 'Source', 'Collection', 'Archive'],
            'By-line': ['Source Photographer', 'Photographer', 'Creator', 'Author', 'Artist'],
            'By-lineTitle': ['Institutional Creator', 'Creator Role', 'Organization']
        }
        
        # Initialize the results dictionary
        column_map = {key: None for key in column_map_options}
        
        print("\nLooking for column matches...")
        
        # First pass: Look for exact matches
        for target_field, possible_matches in column_map_options.items():
            for match_option in possible_matches:
                if match_option in df.columns:
                    column_map[target_field] = match_option
                    print(f"✓ Found exact match for '{target_field}': '{match_option}'")
                    break
        
        # Second pass: For columns not found, try partial matches
        for target_field, possible_matches in column_map_options.items():
            if column_map[target_field] is None:
                for match_option in possible_matches:
                    for col in df.columns:
                        if match_option.lower() in col.lower():
                            column_map[target_field] = col
                            print(f"✓ Found partial match for '{target_field}': '{col}'")
                            break
                    if column_map[target_field] is not None:
                        break
        
        # Special handling for ObjectName if still not found - prioritize Accession Number
        if column_map['ObjectName'] is None:
            # First, check for an exact Accession Number column
            if 'Accession Number' in df.columns:
                column_map['ObjectName'] = 'Accession Number'
                print(f"✓ Using 'Accession Number' as ObjectName")
            else:
                # Otherwise look for similar columns
                for col in df.columns:
                    if 'accession' in col.lower() or 'number' in col.lower():
                        column_map['ObjectName'] = col
                        print(f"✓ Using '{col}' as ObjectName (based on column name)")
                    
                    # Special handling: If we're using Accession Number for ObjectName,
                    # we need to ensure it's properly renamed in later steps
                    if 'accession' in col.lower():
                        print(f"   Note: Will map '{col}' → 'ObjectName' in final output")
                    break
        
        # Final attempt: Look for anything that could be an identifier column
        if column_map['ObjectName'] is None:
            for col in df.columns:
                if 'id' in col.lower() or 'identifier' in col.lower() or 'number' in col.lower():
                    column_map['ObjectName'] = col
                    print(f"✓ Using '{col}' as ObjectName (based on column name pattern)")
                    break
                    
        # For any remaining columns, scan the data for likely matches
        # This helps identify columns based on their content
        if column_map['ObjectName'] is None:
            row_check_limit = min(5, len(df))
            print("\nSearching data for potential identifier columns...")
            for i, col in enumerate(df.columns):
                # Skip columns we've already mapped
                if col in column_map.values():
                    continue
                    
                # Look for columns with short values that could be identifiers
                for j in range(row_check_limit):
                    try:
                        cell_value = str(df.iloc[j, i])
                        # Look for patterns that suggest an identifier
                        if (len(cell_value) < 15 and 
                            (('-' in cell_value) or 
                             any(c.isdigit() for c in cell_value))):
                            print(f"Possible identifier in column {i}: '{col}' with value '{cell_value}'")
                            if column_map['ObjectName'] is None:
                                column_map['ObjectName'] = col
                                print(f"✓ Using '{col}' as ObjectName (based on data pattern)")
                                break
                    except:
                        pass  # Skip any errors when examining cells
                
                if column_map['ObjectName'] is not None:
                    break
        # Print the column mapping results with detailed information
        print("\nFinal column mapping found:")
        for key, value in column_map.items():
            if value:
                # Get a sample value from the column for verification
                try:
                    sample_value = df.iloc[0][value]
                    sample_str = str(sample_value) if len(str(sample_value)) < 50 else str(sample_value)[:47] + "..."
                    print(f"  ✓ {key} → {value} (sample: {sample_str})")
                except:
                    print(f"  ✓ {key} → {value}")
            else:
                print(f"  ✗ {key} → Not found")
        
        # Define required columns (must have these for successful processing)
        required_columns = ['Title', 'ObjectName']
        
        # Check if we're missing any required columns
        missing_required = [key for key in required_columns if column_map.get(key) is None]
        missing_other = [key for key, value in column_map.items() 
                         if value is None and key not in required_columns]
        
        if missing_required:
            print("\nERROR: The following required columns were not found:")
            for col in missing_required:
                print(f"  - {col}")
            print("\nProcessing cannot continue without these columns.")
            print("Please check your Excel file structure or choose another file.")
            return False
        
        if missing_other:
            print("\nWARNING: Some optional columns were not found:")
            for col in missing_other:
                print(f"  - {col}")
            print("Processing will continue, but these fields will be empty in the output.")
            
        # Display sample data for columns we're using
        print("\nSample data from identified columns (first row):")
        first_row = df.iloc[0]
        for key, col_name in column_map.items():
            if col_name is not None:
                try:
                    value = first_row[col_name]
                    print(f"  {key} ({col_name}): {value}")
                except:
                    print(f"  {key} ({col_name}): <error accessing value>")
        
        # Create the target header mapping - map from actual column names to our target names
        header_mapping = {}
        # Define the mapping from our internal names to target output names
        target_mapping = {
            'Title': 'Headline',
            'ObjectName': 'ObjectName',  # Already named correctly
            'Restrictions': 'CopyrightNotice',
            'Scopenote': 'Caption-Abstract',
            'Source': 'Source',  # Already named correctly
            'By-line': 'By-line',  # Already named correctly
            'By-lineTitle': 'By-lineTitle',  # Already named correctly
            # Add fallbacks for specific column types
            'Accession Number': 'ObjectName',  # Map Accession Number to ObjectName as fallback
            'ID': 'ObjectName',  # Map ID to ObjectName as fallback
            'Record ID': 'ObjectName',  # Map Record ID to ObjectName as fallback
            'Local Identifier': 'ObjectName'  # Map Local Identifier to ObjectName as fallback
        }
        
        # Build the mapping from actual column names to target names
        # Build the mapping from actual column names to target names
        for internal_name, actual_col in column_map.items():
            if actual_col:  # Only add to mapping if we found the column
                new_name = target_mapping.get(internal_name, internal_name)
                header_mapping[actual_col] = new_name
        
        # Add any date columns we want to preserve
        date_columns = ['Month', 'Day', 'Year']
        for date_col in date_columns:
            if date_col in df.columns:
                header_mapping[date_col] = date_col  # Keep the same name
        print("\nFinal header mapping to be applied:")
        for old, new in header_mapping.items():
            print(f"  {old} → {new}")
        
        # Rename the columns according to the mapping
        df = df.rename(columns=header_mapping)
        
        # Create a list of columns to keep (both renamed and important original columns)
        renamed_columns = list(header_mapping.values())
        
        # Print the renamed columns
        print("\nColumns after renaming:")
        for i, col in enumerate(df.columns):
            if col in renamed_columns:
                print(f"  {i}: {col} (renamed)")
            else:
                print(f"  {i}: {col}")
        
        # Filter the dataframe to only include non-null rows in important columns
        # Get a sample of the data to verify it looks correct
        print("\nSample of the data (first 3 rows):")
        print(df.head(3))
        
        # Remove rows that have NaN in all renamed columns (initial filtering)
        important_columns = renamed_columns
        df_filtered = df.dropna(subset=important_columns, how='all')
        print(f"\nInitial filtered DataFrame shape: {df_filtered.shape}")
        
        # Export to CSV with UTF-8 encoding
        print(f"Exporting to CSV: {output_file}...")
        
        # Option 1: Export all columns
        # df.to_csv(output_file, index=False, encoding='utf-8')
        
        # Option 2: Export only the renamed columns and other essential columns
        # Determine which columns to keep
        columns_to_keep = []
        
        # First, add all the renamed columns
        for col in renamed_columns:
            if col in df_filtered.columns:
                columns_to_keep.append(col)
        
        # Add any other important columns that might not have been renamed
        # For example, we might want to keep date information, accession numbers, etc.
        other_important_columns = ['Month', 'Day', 'Year', 'Accession Number', 'ID', 'Record ID']
        for col in other_important_columns:
            if col in df_filtered.columns:
                columns_to_keep.append(col)
        
        # Remove duplicates from columns_to_keep while preserving order
        columns_to_keep = list(dict.fromkeys(columns_to_keep))
        
        print(f"\nExporting {len(columns_to_keep)} columns to CSV:")
        for col in columns_to_keep:
            print(f"  - {col}")
        # Create a new DataFrame with only the columns we want to keep
        # Create a new DataFrame with only the columns we want to keep
        try:
            export_df = df_filtered[columns_to_keep].copy()
        except KeyError as e:
            # Handle case where a column is missing
            missing_col = str(e).strip("'")
            print(f"\nERROR: Required column '{missing_col}' not found in the data")
            print("Available columns:", sorted(df_filtered.columns.tolist()))
            print("\nPossible solutions:")
            print("1. Choose a different Excel file with the required columns")
            print("2. Modify the script to use different column names for mapping")
            print("\nExport failed. Please check column mappings.")
            return False
        # Additional data cleaning and validation
        print("\nPerforming additional data cleaning and validation...")
        
        # 0. Print initial data quality statistics
        initial_row_count = len(export_df)
        print(f"Initial row count: {initial_row_count}")
        
        # Count rows with any data in key columns
        key_columns = {'Headline': 0, 'ObjectName': 0, 'Caption-Abstract': 0}
        for col in key_columns:
            if col in export_df.columns:
                key_columns[col] = export_df[col].notna().sum()
                print(f"Rows with {col}: {key_columns[col]}")
        
        # 1. Remove rows where essential fields are empty
        print("\nRemoving rows with missing essential fields...")
        essential_fields = ['Headline', 'ObjectName']
        essential_fields_present = [col for col in essential_fields if col in export_df.columns]
        
        if not essential_fields_present:
            print("Error: No essential fields found in the data")
            return False
            
        if essential_fields_present:
            original_row_count = len(export_df)
            # Use how='any' to remove rows where ANY of the essential fields are missing
            export_df = export_df.dropna(subset=essential_fields_present, how='any')
            removed_rows = original_row_count - len(export_df)
            print(f"Removed {removed_rows} rows where any of these fields were empty: {', '.join(essential_fields_present)}")
            print(f"Remaining rows: {len(export_df)}")
        
        # 2. Clean up whitespace in text fields
        # 2. Clean up whitespace in text fields
        print("\nCleaning text fields...")
        for col in export_df.columns:
            if is_string_column(export_df[col]):  # Only process string columns
                # Strip whitespace and handle NaN values
                export_df[col] = export_df[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
                # Replace empty strings with NaN
                export_df[col] = export_df[col].replace('', pd.NA)
        # 3. Convert date columns to integers where possible
        print("\nConverting date fields to integers...")
        date_columns = ['Month', 'Day', 'Year']
        for col in date_columns:
            if col in export_df.columns:
                # Convert to integer if possible, otherwise keep as is
                export_df[col] = pd.to_numeric(export_df[col], errors='coerce')
                # Convert NaN to None to avoid writing NaN strings to CSV
                export_df[col] = export_df[col].astype('Int64')
                print(f"Converted {col} to integer format")
        
        # 4. Sort by ObjectName to group related items together
        if 'ObjectName' in export_df.columns:
            export_df = export_df.sort_values('ObjectName')
            print("\nSorted data by ObjectName")

        # 5. Calculate data quality metrics
        total_rows = len(export_df)
        non_empty_counts = {}
        data_quality_scores = {}
        
        print("\nData quality assessment:")
        for col in export_df.columns:
            non_empty_count = export_df[col].notna().sum()
            non_empty_counts[col] = non_empty_count
            percentage = (non_empty_count / total_rows * 100) if total_rows > 0 else 0
            data_quality_scores[col] = percentage
            quality_text = "Poor" if percentage < 50 else "Fair" if percentage < 80 else "Good" if percentage < 95 else "Excellent"
            print(f"Column '{col}': {non_empty_count}/{total_rows} filled ({percentage:.1f}%) - {quality_text}")
        
        # 6. Add a data quality summary
        overall_quality = sum(data_quality_scores.values()) / len(data_quality_scores) if data_quality_scores else 0
        print(f"\nOverall data quality score: {overall_quality:.1f}%")
        print(f"Total rows with good data: {total_rows}")
        
        # Print sample of cleaned data
        print("\nSample of cleaned data (first 3 rows):")
        print(export_df.head(3).to_string())
        
        # Export to CSV with UTF-8 encoding
        try:
            # Define a function to properly format each value in the dataframe
            def format_value(val):
                if pd.isna(val) or pd.isnull(val) or isinstance(val, pd._libs.missing.NAType):
                    return ""
                if isinstance(val, (int, float)):
                    try:
                        if float(val).is_integer():
                            return str(int(val))
                    except:
                        pass
                return str(val)
            
            # Create a copy for formatting
            formatted_df = export_df.copy()
            
            print("\nFormatting data for CSV export...")
            
            # Apply formatting column by column instead of using map
            for col in formatted_df.columns:
                try:
                    # Handle different column types appropriately
                    if is_string_column(formatted_df[col]):
                        formatted_df[col] = formatted_df[col].apply(format_value)
                    elif formatted_df[col].dtype.name in ['int64', 'float64', 'Int64']:
                        formatted_df[col] = formatted_df[col].apply(format_value)
                    else:
                        # For other types, convert to string
                        formatted_df[col] = formatted_df[col].astype(str)
                        formatted_df[col] = formatted_df[col].apply(format_value)
                except Exception as e:
                    print(f"Warning: Could not format column '{col}': {str(e)}")
            
            # Special handling for date columns to ensure they're properly formatted as integers
            for col in ['Month', 'Day', 'Year']:
                if col in formatted_df.columns:
                    try:
                        # Ensure dates are properly formatted without decimal points
                        formatted_df[col] = formatted_df[col].apply(
                            lambda x: str(int(float(x))) if x != "" and not pd.isna(x) and not pd.isnull(x) else ""
                        )
                    except Exception as e:
                        print(f"Warning: Could not format date column '{col}': {str(e)}")
            
            # Export to CSV
            formatted_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\nSuccessfully exported {len(export_df)} rows to {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
        
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return False
    except Exception as e:
        print(f"Error processing the Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    # Let the user select an Excel file
    input_file = select_excel_file()
    
    # Check if the selected Excel file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found in the current directory.")
        sys.exit(1)
    
    # Process the selected Excel file
    success = process_excel_file(input_file)
    
    if success:
        print("\nProcessing completed successfully!")
        
        # Optionally, display the first few rows of the output file
        try:
            result_df = pd.read_csv("export.csv")
            print("\nFirst 5 rows of the output CSV file:")
            print(result_df.head())
        except Exception as e:
            print(f"Error reading the output file: {str(e)}")
    else:
        print("\nProcessing failed. Please check the error messages above.")

