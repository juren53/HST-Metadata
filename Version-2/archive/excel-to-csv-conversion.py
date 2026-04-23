#!/usr/bin/env python3
import pandas as pd
import os
import sys
def process_excel_to_csv(excel_file_path, csv_file_path):
    """
    Process an Excel file and convert it directly to CSV:
    1. Read Excel file, skipping first 4 rows (including the "HST - DRUPAL FIELDS" row)
    2. Define essential columns we want to keep based on mapping
    3. Map the columns we care about
    4. Drop all other columns
    5. Arrange the columns in a logical order
    6. Properly handle numeric formatting
    7. Save directly to CSV
    
    Args:
        excel_file_path (str): Path to the input Excel file
        csv_file_path (str): Path to save the output CSV file
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Check if the Excel file exists
        if not os.path.exists(excel_file_path):
            print(f"Error: Excel file '{excel_file_path}' not found.")
            return False
        
        # 1. Define essential columns we want to keep based on mapping
        # 1. Define essential columns we want to keep based on mapping
        column_mapping = {
            'Senator Harry Truman Visits VFW Convention in Chicago': 'Headline',
            # Using a more flexible approach to find the Caption-Abstract column
            # by checking for columns that start with "Vice Presidential candidate"
            'Acme Newspictures': 'By-line',
            '8x10 inches': 'Physical Size',
            'Black-and-White': 'Color',
            '77-83': 'ObjectName',
            8: 'Month',
            23: 'Day',
            1944: 'Year'
        }
        # Print the column mappings for debugging
        print("Column mappings that will be applied:")
        for source, target in column_mapping.items():
            print(f"  {source} -> {target}")
        
        # Define additional columns to keep (without renaming)
        additional_columns = [
            'Keywords',
            'People Pictured'
        ]
        
        # Define Keywords to include
        keywords_to_include = [
            "Veterans", 
            "Chicago (Ill.)", 
            "Convention", 
            "VFW",
            "Politics",
            "Campaigns"
        ]
        
        # Define People Pictured to include
        people_to_include = [
            "Truman, Harry S., 1884-1972",
            "Van Antwerp, Eugene Ignatius, 1889-1962"
        ]
        
        # Read the Excel file directly, skipping the first 4 rows (documentation and mappings, including "HST - DRUPAL FIELDS" row)
        print(f"Reading Excel file: {excel_file_path}")
        print(f"DEBUG: Looking for these numeric fields as columns: 8, 23, 1944")
        df = pd.read_excel(excel_file_path, skiprows=4)
        
        # Check if the dataframe is empty
        if df.empty:
            print(f"Error: Excel file '{excel_file_path}' has no data after skipping first 4 rows.")
            return False
        
        # 2. Clean up column names by removing ".1", ".2", etc. suffixes
        cleaned_columns = {}
        for col in df.columns:
            # Check if column name ends with .1, .2, etc.
            if isinstance(col, str) and col.split('.')[-1].isdigit():
                base_name = '.'.join(col.split('.')[:-1])
                # Only rename if the base name doesn't already exist to avoid duplicates
                if base_name not in df.columns and base_name not in cleaned_columns.values():
                    print(f"Cleaning column name: {col} -> {base_name}")
                    cleaned_columns[col] = base_name
        
        # Apply the column name cleanup
        if cleaned_columns:
            df = df.rename(columns=cleaned_columns)
        
        # 3. Remove unnamed columns (columns with names that contain 'Unnamed')
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            print(f"Removing {len(unnamed_cols)} unnamed columns")
            df = df.drop(columns=unnamed_cols)
        
        # 4. Remove duplicate columns (keeping only the first occurrence)
        duplicated_cols = df.columns[df.columns.duplicated()]
        if len(duplicated_cols) > 0:
            print(f"Removing {len(duplicated_cols)} duplicate columns")
            df = df.loc[:, ~df.columns.duplicated()]
            
        # 5. Apply column mappings and keep only essential columns
        # Print available columns for debugging
        print("\nAvailable columns in Excel file:")
        for col in df.columns:
            print(f"  {col}")
            
        # Find Caption-Abstract column - looking for a column that starts with "Vice Presidential candidate"
        caption_cols = [col for col in df.columns if isinstance(col, str) and col.startswith("Vice Presidential candidate")]
        if caption_cols:
            caption_col = caption_cols[0]
            print(f"DEBUG: Found Caption-Abstract column: '{caption_col}'")
            print(f"DEBUG: Full Caption-Abstract text: '{caption_col}'")
            column_mapping[caption_col] = 'Caption-Abstract'
        else:
            print("WARNING: Could not find a column for Caption-Abstract")
            
        # Check which columns from our mapping exist in the dataframe
        existing_mapping_cols = [col for col in column_mapping.keys() if col in df.columns]
        existing_additional_cols = [col for col in additional_columns if col in df.columns]
        
        # Print which columns were found for debugging
        print("\nMapping columns found in Excel:")
        for col in existing_mapping_cols:
            print(f"  Found: {col} -> {column_mapping[col]}")
            
        print("\nAdditional columns found in Excel:")
        for col in existing_additional_cols:
            print(f"  Found: {col}")
        
        if not existing_mapping_cols and not existing_additional_cols:
            print("Error: None of the specified columns found in the Excel file.")
            return False
            
        # Apply mappings to columns we want to keep
        columns_to_rename = {col: column_mapping[col] for col in existing_mapping_cols}
        if columns_to_rename:
            print(f"Applying column mapping to {len(columns_to_rename)} columns")
            for source, target in columns_to_rename.items():
                print(f"  DEBUG: Mapping '{source}' -> '{target}'")
            df = df.rename(columns=columns_to_rename)
        
        # Create a list of columns in the new renamed dataframe that we want to keep
        columns_to_keep = [column_mapping[col] for col in existing_mapping_cols] + existing_additional_cols
        
        # Only keep the columns we're interested in
        print(f"Keeping only {len(columns_to_keep)} essential columns")
        df = df[columns_to_keep]
        
        # 6. Arrange columns in a logical order
        # 6. Arrange columns in a logical order
        # Define the logical order of columns (mapped columns first, then additional columns)
        logical_order = [
            'Headline',           # Senator Harry Truman Visits VFW Convention in Chicago
            'Caption-Abstract',   # Vice Presidential candidate...
            'By-line',            # Acme Newspictures
            'ObjectName',         # 77-83
            'Month', 'Day', 'Year',
            'Physical Size',      # 8x10 inches
            'Color',              # Black-and-White
            'Keywords',
            'People Pictured'
        ]
        # Filter the logical order to only include columns that exist in our dataframe
        # Filter the logical order to only include columns that exist in our dataframe
        ordered_columns = [col for col in logical_order if col in df.columns]
        
        # Reorder columns
        print("\nArranging columns in logical order:")
        for col in ordered_columns:
            print(f"  {col}")
            
        df = df[ordered_columns]
            
        # Remove rows that have less than 3 non-null values
        print("\nRemoving rows with less than 3 non-null values")
        initial_rows = len(df)
        df = df.dropna(thresh=3)  # Keep only rows with at least 3 non-null values
        rows_removed = initial_rows - len(df)
        print(f"  Removed {rows_removed} rows with fewer than 3 non-null values")
            
        # 5. Handle data types properly, especially for booleans and numbers
        for col in df.columns:
            # Check for boolean-like columns (contains only 0.0, 1.0, NaN)
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].dropna().isin([0.0, 1.0]).all():
                    print(f"Converting column '{col}' to boolean")
                    df[col] = df[col].map({1.0: True, 0.0: False}, na_action='ignore')
                else:
                    # For numeric columns with trailing zeros, convert to string and remove them
                    print(f"Cleaning numeric format for column '{col}'")
                    # Convert to string first to handle appropriate formatting
                    df[col] = df[col].apply(lambda x: str(int(x)) if pd.notnull(x) and x == int(x) else x)
        
        # 7. Add or update Keywords and People Pictured columns
        if 'Keywords' not in df.columns:
            print("Creating new Keywords column with predefined keywords")
            df['Keywords'] = ', '.join(keywords_to_include)
        else:
            print("Updating existing Keywords column with additional keywords")
            current_keywords = df['Keywords'].iloc[0] if not df['Keywords'].empty and not pd.isna(df['Keywords'].iloc[0]) else ""
            # Only add keywords that aren't already present
            new_keywords = [kw for kw in keywords_to_include if kw not in current_keywords]
            if new_keywords:
                if current_keywords:
                    df['Keywords'] = current_keywords + ', ' + ', '.join(new_keywords)
                else:
                    df['Keywords'] = ', '.join(new_keywords)
            print(f"  DEBUG: Final Keywords: {df['Keywords'].iloc[0] if not df['Keywords'].empty else ''}")
            
        if 'People Pictured' not in df.columns:
            print("Creating new People Pictured column with predefined people")
            df['People Pictured'] = ', '.join(people_to_include)
        else:
            print("Updating existing People Pictured column with additional people")
            current_people = df['People Pictured'].iloc[0] if not df['People Pictured'].empty and not pd.isna(df['People Pictured'].iloc[0]) else ""
            # Only add people that aren't already present
            new_people = [person for person in people_to_include if person not in current_people]
            if new_people:
                if current_people:
                    df['People Pictured'] = current_people + ', ' + ', '.join(new_people)
                else:
                    df['People Pictured'] = ', '.join(new_people)
            print(f"  DEBUG: Final People Pictured: {df['People Pictured'].iloc[0] if not df['People Pictured'].empty else ''}")
            
        # 8. Clean up empty rows at the end
        print("Cleaning up empty rows at the end")
        initial_rows = len(df)
        df = df.dropna(how='all')
        rows_removed = initial_rows - len(df)
        print(f"  Removed {rows_removed} empty rows")
        
        # Write directly to CSV
        print(f"Saving to CSV file: {csv_file_path}")
        print("\nDEBUG: Final columns and sample values:")
        for col in df.columns:
            sample_value = df[col].iloc[0] if not df.empty and not pd.isna(df[col].iloc[0]) else "N/A"
            # For Caption-Abstract, print the full text to verify it's captured correctly
            if col == 'Caption-Abstract':
                print(f"  {col} (FULL TEXT): {sample_value}")
            else:
                print(f"  {col}: {sample_value}")
        
        # Ensure columns are in the exact order specified
        final_column_order = [
            'Headline',
            'Caption-Abstract',
            'By-line',
            'ObjectName',
            'Month',
            'Day',
            'Year',
            'Physical Size',
            'Color',
            'Keywords',
            'People Pictured'
        ]
        
        # Only keep columns that exist in our dataframe
        final_columns = [col for col in final_column_order if col in df.columns]
        
        print("\nFinal column order:")
        for col in final_columns:
            print(f"  {col}")
            
        # Reorder columns to final order
        df = df[final_columns]
            
        df.to_csv(csv_file_path, index=False)
        
        print(f"Successfully processed and converted {excel_file_path} to {csv_file_path}")
        return True
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return False
if __name__ == "__main__":
    # Define input and output file paths
    excel_file = 'TestMetadataForJim.xlsx'
    csv_file = 'TestMetadataForJim.csv'
    
    print(f"Starting Excel to CSV processing...")
    success = process_excel_to_csv(excel_file, csv_file)
    
    if success:
        print("Excel processing and CSV conversion completed successfully.")
        sys.exit(0)
    else:
        print("Processing failed. See error messages above.")
        sys.exit(1)
