#!/usr/bin/env python3
"""
Google Drive File Access Tool

This script allows you to access and download files from Google Drive,
including files in non-native Google formats like Microsoft Excel.
"""

import os
import sys
import json
import pickle
import re
import io
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Check if pandas is installed
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# === CONFIG ===
CLIENT_SECRET_FILE = 'client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token_drive.pickle'  # Using a different pickle file to avoid scope issues
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Common MIME types dictionary for user-friendly display
MIME_TYPES = {
    'application/vnd.google-apps.spreadsheet': 'Google Sheets',
    'application/vnd.google-apps.document': 'Google Docs',
    'application/vnd.google-apps.presentation': 'Google Slides',
    'application/vnd.google-apps.form': 'Google Forms',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Microsoft Excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Microsoft Word',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Microsoft PowerPoint',
    'application/pdf': 'PDF',
    'image/jpeg': 'JPEG Image',
    'image/png': 'PNG Image',
    'text/plain': 'Plain Text',
    'text/csv': 'CSV',
    'application/zip': 'ZIP Archive'
}

def extract_file_id_from_url(url):
    """Extract a Google Drive file ID from various URL formats."""
    # Match Google Drive file URLs
    file_pattern = r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)'
    file_match = re.search(file_pattern, url)
    if file_match:
        return file_match.group(1)
    
    # Match spreadsheet URLs
    sheet_pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)'
    sheet_match = re.search(sheet_pattern, url)
    if sheet_match:
        return sheet_match.group(1)
    
    # Match document URLs
    doc_pattern = r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)'
    doc_match = re.search(doc_pattern, url)
    if doc_match:
        return doc_match.group(1)
    
    # Match presentation URLs
    pres_pattern = r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)'
    pres_match = re.search(pres_pattern, url)
    if pres_match:
        return pres_match.group(1)
    
    # If it's not a URL but looks like a file ID, return it as is
    id_pattern = r'^[a-zA-Z0-9_-]{25,}$'
    if re.match(id_pattern, url):
        return url
    
    return None

def get_valid_file_id():
    """
    Prompts user for file ID or URL and validates it.
    Returns a valid file ID or None if cancelled.
    """
    print("\n=== Google Drive File Access ===")
    print("Please enter the Google Drive file URL or ID")
    print("Examples:")
    print("- Drive URL: https://drive.google.com/file/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890/view")
    print("- Docs URL: https://docs.google.com/spreadsheets/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890/edit")
    print("- File ID: 1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890")
    print("Enter 'q' to quit")
    
    while True:
        user_input = input("\nFile URL or ID: ").strip()
        
        if user_input.lower() == 'q':
            return None
            
        file_id = extract_file_id_from_url(user_input)
        
        if not file_id:
            print("Invalid URL or file ID format. Please try again.")
            continue
            
        # Ask if user wants to download the file
        download_prompt = input("\nWould you like to download this file? (y/n): ").lower()
        
        if download_prompt == 'y':
            success, file_path = download_file(service, file_id, file_metadata)
            
            # If file was downloaded and it's an Excel file, offer to load it into pandas
            if success and file_path and file_path.endswith(('.xlsx', '.xls', '.csv')):
                # Check if pandas is available
                if not PANDAS_AVAILABLE:
                    print("\nNote: To analyze this Excel file with pandas, install the required packages:")
                    print("pip install pandas numpy openpyxl")
                else:
                    analyze_prompt = input("\nWould you like to analyze this file with pandas? (y/n): ").lower()
                    if analyze_prompt == 'y':
                        analyze_excel_file(file_path)
y ~44 chars)")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                continue
                
        print(f"Using file ID: {file_id}")
        return file_id

def get_credentials():
    """Get valid user credentials from storage or run the OAuth flow."""
    credentials = None
    
    # Try to load credentials from the token pickle file
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            try:
                credentials = pickle.load(token)
                print("Loaded credentials from token file")
            except Exception as e:
                print(f"Error loading token file: {e}")
    
    # If no valid credentials available, run the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                print("Refreshed expired credentials")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                credentials = None
        
        # If still no valid credentials, run the flow
        if not credentials:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES)
                
                print("Please authenticate using your browser...")
                credentials = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open(TOKEN_PICKLE_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
                print("Saved new credentials to token file")
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                raise
    
    return credentials

def get_file_metadata(service, file_id):
    """Retrieve metadata for the specified file."""
    try:
        # Use fields parameter to specify which fields to retrieve
        file_metadata = service.files().get(
            fileId=file_id, 
            fields='id, name, mimeType, size, webViewLink, createdTime, modifiedTime, owners, sharingUser'
        ).execute()
        
        return file_metadata
    except HttpError as error:
        if 'not found' in str(error).lower():
            print(f"Error: File with ID '{file_id}' was not found.")
        elif 'permission' in str(error).lower():
            print(f"Error: You don't have permission to access file with ID '{file_id}'.")
        else:
            print(f"Error accessing file: {error}")
            
        print("\nTroubleshooting tips:")
        print("1. Verify the file ID is correct")
        print("2. Make sure you have at least 'Reader' access to the file")
        print("3. Try opening the file in your browser first:")
        print(f"   https://drive.google.com/file/d/{file_id}/view")
        
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_mime_type_description(mime_type):
    """Convert MIME type to a user-friendly description."""
    return MIME_TYPES.get(mime_type, mime_type)

def format_file_size(size_bytes):
    """Format file size in bytes to a human-readable format."""
    if size_bytes is None:
        return "Unknown size"
        
    # Convert to integer if it's a string
    if isinstance(size_bytes, str):
        try:
            size_bytes = int(size_bytes)
        except ValueError:
            return size_bytes  # Return as is if not convertible
    
    # Format the size
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_export_mime_type(google_mime_type):
    """Get the appropriate export MIME type for a Google Docs file."""
    export_map = {
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # Export as DOCX
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Export as XLSX
        'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # Export as PPTX
        'application/vnd.google-apps.drawing': 'application/pdf',  # Export as PDF
    }
    
    return export_map.get(google_mime_type, None)

def get_file_extension(mime_type):
    """Get the appropriate file extension for a MIME type."""
    extension_map = {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'application/pdf': '.pdf',
        'text/plain': '.txt',
        'text/csv': '.csv',
        'application/zip': '.zip'
    }
    
    return extension_map.get(mime_type, '')

def download_file(service, file_id, file_metadata):
    """Download the file to the local filesystem."""
    file_name = file_metadata.get('name', 'unknown_file')
    mime_type = file_metadata.get('mimeType', '')
    
    # If it's a Google Docs format, we need to export it
    if mime_type.startswith('application/vnd.google-apps'):
        export_mime_type = get_export_mime_type(mime_type)
        if export_mime_type:
            try:
                request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
                file_extension = get_file_extension(export_mime_type)
                download_path = f"{file_name}{file_extension}"
            except:
                print(f"Error: This Google {get_mime_type_description(mime_type)} cannot be exported.")
                return False, None
        else:
            print(f"Error: The file type {get_mime_type_description(mime_type)} cannot be downloaded directly.")
            return False, None
    else:
        # For non-Google formats, download directly
        request = service.files().get_media(fileId=file_id)
        download_path = file_name
    
    try:
        # Create a BytesIO object to hold the downloaded data
        file_data = io.BytesIO()
        
        # Create a downloader object
        downloader = MediaIoBaseDownload(file_data, request)
        
        # Download the file in chunks, showing progress
        done = False
        print(f"\nDownloading {file_name}:")
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  Progress: {int(status.progress() * 100)}%", end='\r')
        
        # Write the file to disk
        with open(download_path, 'wb') as f:
            f.write(file_data.getvalue())
        
        print(f"\nFile downloaded successfully to: {download_path}")
        return True, download_path
        
    except HttpError as error:
        print(f"Error downloading file: {error}")
        return False, None
    except Exception as e:
        print(f"Unexpected error during download: {e}")
        return False, None

def analyze_excel_file(file_path):
    """Load an Excel file into a pandas DataFrame and analyze it."""
    try:
        # Try to load the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:  # Excel file
            # Get list of sheet names
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names
            
            if len(sheet_names) > 1:
                print(f"\nThis Excel file contains {len(sheet_names)} sheets:")
                for i, sheet in enumerate(sheet_names, 1):
                    print(f"{i}. {sheet}")
                    
                while True:
                    sheet_choice = input("\nWhich sheet would you like to analyze? (enter number or 'all'): ")
                    if sheet_choice.lower() == 'all':
                        print("\nLoading all sheets into separate DataFrames...")
                        dfs = {sheet: pd.read_excel(file_path, sheet_name=sheet) for sheet in sheet_names}
                        analyze_multiple_sheets(dfs)
                        return
                    else:
                        try:
                            sheet_idx = int(sheet_choice) - 1
                            if 0 <= sheet_idx < len(sheet_names):
                                selected_sheet = sheet_names[sheet_idx]
                                print(f"\nLoading sheet: {selected_sheet}")
                                df = pd.read_excel(file_path, sheet_name=selected_sheet)
                                break
                            else:
                                print(f"Invalid choice. Please enter a number between 1 and {len(sheet_names)}")
                        except ValueError:
                            print("Invalid input. Please enter a number or 'all'")
            else:
                # Only one sheet, load it directly
                df = pd.read_excel(file_path)
        
        # Display basic info about the DataFrame
        display_dataframe_info(df)
        
        # Ask if user wants to see more detailed analysis
        detail_prompt = input("\nWould you like to see more detailed analysis? (y/n): ").lower()
        if detail_prompt == 'y':
            advanced_analysis(df)
        
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")

def display_dataframe_info(df, sheet_name=None):
    """Display basic information about a DataFrame."""
    if sheet_name:
        print(f"\n{'='*50}")
        print(f"SHEET: {sheet_name}")
        print(f"{'='*50}")
        
    # Basic info
    print(f"\nDataFrame Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Show columns
    print("\nColumns:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Show head
    print("\nFirst 5 rows:")
    print(df.head().to_string())
    
    # Data types
    print("\nData Types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("\nMissing Values:")
        for col, count in missing.items():
            if count > 0:
                print(f"  {col}: {count} missing values ({count/len(df):.1%})")

def analyze_multiple_sheets(dfs):
    """Analyze multiple sheets from an Excel file."""
    print(f"\nAnalyzing {len(dfs)} sheets:")
    
    # First, show summary of all sheets
    print("\nSummary of All Sheets:")
    for sheet_name, df in dfs.items():
        print(f"- {sheet_name}: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Ask which sheet to analyze in detail
    while True:
        sheet_choice = input("\nWhich sheet would you like to analyze in detail? (enter name or 'q' to quit): ")
        if sheet_choice.lower() == 'q':
            break
        elif sheet_choice in dfs:
            display_dataframe_info(dfs[sheet_choice], sheet_name=sheet_choice)
            
            # Ask if user wants to see more detailed analysis
            detail_prompt = input("\nWould you like to see more detailed analysis of this sheet? (y/n): ").lower()
            if detail_prompt == 'y':
                advanced_analysis(dfs[sheet_choice])
        else:
            print(f"Sheet '{sheet_choice}' not found. Available sheets: {', '.join(dfs.keys())}")

def advanced_analysis(df):
    """Perform more advanced analysis on a DataFrame."""
    print("\nAdvanced Analysis:")
    
    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        print("\nNumeric Columns Summary:")
        print(df[numeric_cols].describe().to_string())
    
    # Categorical columns summary
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if cat_cols:
        print("\nCategorical Columns Summary:")
        for col in cat_cols[:5]:  # Limit to first 5 categorical columns to avoid overwhelming output
            value_counts = df[col].value_counts()
            if len(value_counts) <= 10:
                print(f"\n{col} - Unique Values: {len(value_counts)}")
                print(value_counts.to_string())
            else:
                print(f"\n{col} - Unique Values: {len(value_counts)} (showing top 10)")
                print(value_counts.head(10).to_string())
    
    # Correlation matrix for numeric columns
    if len(numeric_cols) > 1:
        print("\nCorrelation Matrix (Pearson):")
        correlation = df[numeric_cols].corr()
        # Only show correlations > 0.5 and not 1.0 (self-correlation)
        strong_corr = (correlation.abs() > 0.5) & (correlation.abs() < 1.0)
        if strong_corr.any().any():
            print("Strong correlations (>0.5):")
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j and abs(correlation.iloc[i, j]) > 0.5:
                        print(f"  {col1} and {col2}: {correlation.iloc[i, j]:.2f}")
        else:
            print("No strong correlations found between numeric columns")

def main():
    try:
        # Get credentials
        credentials = get_credentials()
        if not credentials:
            print("Authentication failed. Unable to proceed.")
            sys.exit(1)
        
        # Build the Drive API service
        service = build('drive', 'v3', credentials=credentials)
        
        # Get a valid file ID
        file_id = get_valid_file_id()
        if not file_id:
            print("Operation cancelled by user.")
            sys.exit(0)
        
        # Get file metadata
        print("\nRetrieving file information...")
        file_metadata = get_file_metadata(service, file_id)
        
        if not file_metadata:
            print("Unable to retrieve file metadata. Please check the file ID and your permissions.")
            sys.exit(1)
        
        # Display file information
        name = file_metadata.get('name', 'Unknown')
        mime_type = file_metadata.get('mimeType', 'Unknown')
        size = file_metadata.get('size')
        created_time = file_metadata.get('createdTime', 'Unknown')
        modified_time = file_metadata.get('modifiedTime', 'Unknown')
        web_view_link = file_metadata.get('webViewLink', '')
        
        print("\n" + "="*50)
        print(f"FILE INFORMATION")
        print("="*50)
        print(f"Name: {name}")
        print(f"Type: {get_mime_type_description(mime_type)}")
        print(f"Size: {format_file_size(size)}")
        print(f"Created: {created_time}")
        print(f"Modified: {modified_time}")
        print(f"Web Link: {web_view_link}")
        print(f"File ID: {file_id}")
        print("-"*50)
        
        # Ask if user wants to download the file
        download_prompt = input("\nWould you like to download this file? (y/n): ").lower()
        if download_prompt == 'y':
            download_file(service, file_id, file_metadata)
        
    except HttpError as error:
        status_code = getattr(error, 'status', 'unknown')
        reason = getattr(error, 'reason', str(error))
        
        print(f"API Error (status {status_code}): {reason}")
        
        if "API has not been used in project" in str(error) or "is disabled" in str(error):
            print("\nThis error typically means the Google Drive API needs to be enabled:")
            print("1. Visit https://console.developers.google.com")

            print("1. Visit https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=562755451687")
            print("2. Click the 'Enable' button")
            print("3. Wait a few minutes for the change to propagate")
            print("4. Run this script again")
        
    except Exception as error:
        print(f"An unexpected error occurred: {str(error)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
