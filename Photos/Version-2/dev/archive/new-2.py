import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe

def read_google_sheet(sheet_url):
    """
    Read data from a Google Sheet and return it as a DataFrame.
    
    Args:
        sheet_url (str): The URL of the Google Sheet.
    
    Returns:
        DataFrame: The data from the Google Sheet.
    """
    # Use gspread to access the Google Sheet
    try:
        # Try using service account credentials first
        gc = gspread.service_account()
    except (FileNotFoundError, ValueError, ImportError):
        try:
            # Fall back to OAuth if service account fails
            gc = gspread.oauth()
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    sheet = gc.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)  # Get the first worksheet
    df = get_as_dataframe(worksheet)  # Get the data as a DataFrame
    return df

def process_google_sheet(sheet_url, output_file="export.csv"):
    """
    Process the Google Sheet by reading it and exporting to CSV.
    
    Args:
        sheet_url (str): The URL of the Google Sheet.
        output_file (str): Name of the output CSV file.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Read the Google Sheet into a DataFrame
        df = read_google_sheet(sheet_url)
        print(f"DataFrame shape: {df.shape}")
        
        # Continue with the processing logic similar to process_excel_file
        # (e.g., renaming columns, filtering, exporting to CSV)
        
        # Example: Export to CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Successfully exported data to {output_file}")
        return True
    except Exception as e:
        print(f"Error processing the Google Sheet: {str(e)}")
        return False

if __name__ == "__main__":
    # URL of the Google Sheet
    google_sheet_url = "https://docs.google.com/spreadsheets/d/1cmU-o4UwtyaoSx6MzqIskURjcBsOJ0Qz/edit?gid=1396259650"
    
    # Process the Google Sheet
    success = process_google_sheet(google_sheet_url)
    
    if success:
        print("\nProcessing completed successfully!")
    else:
        print("\nProcessing failed. Please check the error messages above.")