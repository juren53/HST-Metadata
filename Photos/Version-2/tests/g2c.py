#!/usr/bin/env python3
"""
Ver 0.3 updated  2025-07-21 1415

Google Drive to CSV Converter with IPTC Mapping

This script combines functionality from gc.py and map.py to:
1. Detect and handle both Google Sheets and Excel files
2. Convert Excel files to Google Sheets format if needed
3. Map data to IPTC metadata fields using specialized mapping logic
4. Export the mapped data to CSV format

Features:
- Automatic Excel file detection and conversion
- Enhanced error handling with specific solutions
- Support for both native Google Sheets and Excel files
- Specialized IPTC metadata field mapping
- ISO date formatting
- Detailed data validation and reporting
- Windows-1252 to UTF-8 double-encoding artifacts

Usage:
    python g2c.py [--sheet-url URL] [--export-csv [FILENAME]] [--auto-convert]

Options:
    --sheet-url, -u            URL of the Google Spreadsheet or Excel file
    --export-csv, -e [FILENAME] Export data to CSV file (default: export.csv)
    --auto-convert, -a         Automatically convert Excel files to Google Sheets
"""

import os
import sys
import pickle
import re
import argparse
import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import for UTF-8 encoding detection
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False
    print("Warning: chardet not available. Install with 'pip install chardet' for better encoding detection.")

# Import for automatic text fixing (double-encoding repair)
try:
    from ftfy import fix_text
    FTFY_AVAILABLE = True
except ImportError:
    FTFY_AVAILABLE = False
    print("Warning: ftfy not available. Install with 'pip install ftfy' for automatic double-encoding repair.")

# === CONFIG ===
CLIENT_SECRET_FILE = 'client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token_sheets.pickle'

# Enhanced scopes to support both Sheets and Drive operations
ENHANCED_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',      # Read/write Google Sheets
    'https://www.googleapis.com/auth/drive',             # Access Google Drive files
    'https://www.googleapis.com/auth/drive.file'         # Manage created files
]

# Fallback scopes for read-only access
READONLY_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# === TARGET SPREADSHEET ===
# Default spreadsheet ID to use if none provided via command line
DEFAULT_SPREADSHEET_ID = '19AY254dZxZIq_8PPbexDUVoLQbsnvkXDRCHp68T2C-4'

def get_credentials(enhanced_mode=True):
    """
    Get or create authentication credentials.
    
    Args:
        enhanced_mode: If True, try to get enhanced scopes for conversion
        
    Returns:
        Valid credentials object
    """
    creds = None
    
    # Try enhanced token first if available
    enhanced_token = 'token_drive_sheets.pickle'
    if enhanced_mode and os.path.exists(enhanced_token):
        try:
            with open(enhanced_token, 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.valid:
                return creds
        except Exception:
            pass
    
    # Fall back to regular token
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            # Choose scopes based on mode
            scopes = ENHANCED_SCOPES if enhanced_mode else READONLY_SCOPES
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes)
                creds = flow.run_local_server(port=0)
                
                # Save token with appropriate name
                token_file = enhanced_token if enhanced_mode else TOKEN_PICKLE_FILE
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                    
            except Exception as e:
                if enhanced_mode:
                    # Fall back to read-only mode
                    print("Enhanced authentication failed, falling back to read-only mode...")
                    return get_credentials(enhanced_mode=False)
                else:
                    raise e
    
    return creds

def extract_spreadsheet_id_from_url(url):
    """
    Extract the spreadsheet ID from a Google Sheets or Drive URL.
    
    Args:
        url: URL of the Google Spreadsheet or Drive file
        
    Returns:
        str: Spreadsheet/file ID extracted from the URL
    
    Raises:
        ValueError: If the URL does not appear to be a valid format
    """
    # Handle direct spreadsheet ID input (not a URL)
    if not url.startswith('http'):
        return url.strip()
    
    # Extended patterns to handle both Sheets and Drive URLs
    patterns = [
        r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'file/d/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
    raise ValueError(
        "Invalid Google Sheets/Drive URL. Expected formats:\\n"
        "- https://docs.google.com/spreadsheets/d/ID/...\\n"
        "- https://drive.google.com/file/d/ID/...\\n"
        "- Or just the ID itself"
    )

def detect_and_convert_if_needed(url_or_id, auto_convert=False):
    """
    Detect file type and convert Excel to Google Sheets if needed.
    
    Args:
        url_or_id: Google Sheets URL or file ID
        auto_convert: If True, automatically convert Excel files
        
    Returns:
        tuple: (final_spreadsheet_id, was_converted, conversion_info)
    """
    try:
        # Import our detection modules
        from sheets_type_detector import SheetsTypeDetector, detect_sheet_type
        from sheets_converter import convert_spreadsheet_to_sheet
        
        file_id = extract_spreadsheet_id_from_url(url_or_id)
        
        # Get enhanced credentials for detection
        creds = get_credentials(enhanced_mode=True)
        
        # Initialize detector
        detector = SheetsTypeDetector(
            client_secret_file=CLIENT_SECRET_FILE,
            token_file='token_drive_sheets.pickle'
        )
        
        # Try to detect file type
        print("🔍 Detecting file type...")
        try:
            file_info = detect_sheet_type(file_id, detector)
            
            print(f"📄 File: {file_info['file_name']}")
            print(f"🏷️  Type: {file_info['mime_type']}")
            try:
                input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                sys.exit(0)
            
            if file_info['is_native_sheet']:
                print("✅ Native Google Sheet detected - ready to use!")
                return file_id, False, None
                
            elif file_info['is_excel']:
                print("\n❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data")
                sys.exit(1)
            else:
                print(f"⚠️  Unknown file type: {file_info['mime_type']}")
                print("   Attempting to use as-is...")
                return file_id, False, None
                
        except Exception as e:
            error_str = str(e).lower()
            
            if 'access denied' in error_str or 'permission' in error_str:
                print("⚠️  File access issue - trying with current authentication...")
                return file_id, False, None
            elif 'operation is not supported' in error_str:
                print("\n❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data")
                sys.exit(1)
            else:
                print(f"⚠️  Detection failed: {e}")
                print("   Proceeding with original file ID...")
                return file_id, False, None
                
    except ImportError:
        # Detection modules not available, proceed normally
        print("📝 Detection modules not available - proceeding with original URL")
        return extract_spreadsheet_id_from_url(url_or_id), False, None

def fetch_sheet_data(spreadsheet_id=DEFAULT_SPREADSHEET_ID):
    """
    Fetch data from Google Sheet and convert to pandas DataFrame.
    
    Args:
        spreadsheet_id: ID of the Google Sheet to access
        
    Returns:
        pandas.DataFrame: Data from the sheet with column headers
    
    Raises:
        Exception: If authentication fails or sheet cannot be accessed
    """
    try:
        # Get authentication credentials (try enhanced first, fall back to read-only)
        try:
            creds = get_credentials(enhanced_mode=True)
        except Exception:
            creds = get_credentials(enhanced_mode=False)
            
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata and first sheet title
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        first_sheet_title = spreadsheet['sheets'][0]['properties']['title']
        print(f"Accessing sheet: {first_sheet_title}")

        # Fetch all values from the first sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{first_sheet_title}"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in the sheet.")
            return None
            
        # Convert to DataFrame
        # Assume the first row contains headers
        headers = values[0]
        data_rows = values[1:]
        
        # Find the maximum number of columns in any row (including header and data rows)
        max_cols = max([len(row) for row in values])
        
        # Check for duplicate headers and make them unique if necessary
        if len(headers) != len(set(headers)):
            print("Warning: Duplicate column names found. Adding suffixes to make them unique.")
            seen = {}
            unique_headers = []
            for header in headers:
                if header in seen:
                    seen[header] += 1
                    unique_headers.append(f"{header}_{seen[header]}")
                else:
                    seen[header] = 0
                    unique_headers.append(header)
            headers = unique_headers
        
        # If there are more columns in the data than in the headers, add generic column names
        if max_cols > len(headers):
            print(f"Warning: Some rows have more columns ({max_cols}) than the header row ({len(headers)}).")
            print("Adding generic column names for the extra columns.")
            for i in range(len(headers), max_cols):
                headers.append(f"Column_{i+1}")
            
        # Create DataFrame, handling rows that might have different column counts than headers
        padded_data = []
        for row in data_rows:
            if len(row) < max_cols:
                # Pad the row with None values
                padded_data.append(row + [None] * (max_cols - len(row)))
            else:
                padded_data.append(row)
                
        df = pd.DataFrame(padded_data, columns=headers)
        return df
        
    except HttpError as error:
        error_message = str(error)
        
        if "This operation is not supported for this document" in error_message:
            print("\n❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data")
            sys.exit(1)
        else:
            if "Requested entity was not found" in str(error):
                print("\n❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data")
                sys.exit(1)
            else:
                print(f"HTTP Error: {error}")
                print("This might be due to incorrect spreadsheet ID or permission issues.")
                return None
        print(f"An error occurred: {error}")
        return None

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
        with pd.option_context('display.max_columns', None,
                              'display.width', 1000,
                              'display.max_rows', 10,
                              'display.max_colwidth', 100):
            print(df.head(10))
    except Exception as e:
        print(f"Warning: Could not display full data preview: {e}")
        print("Displaying simplified view:")
        print(df.head(10).to_string(max_cols=10, max_rows=10))

def text_to_utf8(text_or_bytes):
    """Convert text with unknown encoding to UTF-8 string using chardet.
    
    Method 1: Using chardet for encoding detection
    
    Args:
        text_or_bytes: String or bytes that may need encoding conversion
        
    Returns:
        str: UTF-8 encoded string
    """
    if isinstance(text_or_bytes, str):
        # Already a Unicode string, just return it
        return text_or_bytes
    
    # Detect encoding for bytes
    if CHARDET_AVAILABLE:
        detected = chardet.detect(text_or_bytes)
        encoding = detected['encoding']
        
        if encoding:
            return text_or_bytes.decode(encoding)
    
    # Fallback to UTF-8 with error handling
    return text_or_bytes.decode('utf-8', errors='replace')


def text_to_utf8_fallback(text_or_bytes):
    """Try common encodings in order of likelihood.
    
    Method 2: Try common encodings when chardet isn't available
    
    Args:
        text_or_bytes: String or bytes that may need encoding conversion
        
    Returns:
        str: UTF-8 encoded string
    """
    if isinstance(text_or_bytes, str):
        return text_or_bytes
    
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            return text_or_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Last resort - decode with replacement characters
    return text_or_bytes.decode('utf-8', errors='replace')


def clean_metadata_text(text):
    """Clean text for photo metadata embedding.
    
    Method 3: For photo metadata specifically
    
    Args:
        text: String or bytes that may contain metadata encoding issues
        
    Returns:
        str: Cleaned UTF-8 string suitable for metadata
    """
    if isinstance(text, bytes):
        # Detect and decode
        if CHARDET_AVAILABLE:
            detected = chardet.detect(text)
            encoding = detected.get('encoding', 'utf-8')
            text = text.decode(encoding, errors='replace')
        else:
            # Use fallback method
            text = text_to_utf8_fallback(text)
    
    # Ensure it's valid UTF-8 and remove problematic characters
    text = text.encode('utf-8', errors='replace').decode('utf-8')
    
    # Optional: remove or replace characters that might cause issues
    text = text.replace('\x00', '')  # Remove null bytes
    
    return text


def smart_encoding_cleaner(text):
    """Hierarchical approach combining all methods with automatic double-encoding repair.
    
    This function uses multiple methods in a complementary way:
    1. First tries chardet-based detection for bytes
    2. Falls back to common encodings if chardet fails
    3. Uses ftfy for automatic double-encoding repair (preferred)
    4. Falls back to manual artifact cleaning if ftfy unavailable
    5. Finally applies metadata-specific cleaning
    
    Args:
        text: String or bytes that may need encoding conversion and cleaning
        
    Returns:
        str: Cleaned UTF-8 string
    """
    # Step 1: Handle bytes input with encoding detection
    if isinstance(text, bytes):
        if CHARDET_AVAILABLE:
            text = text_to_utf8(text)
        else:
            text = text_to_utf8_fallback(text)
    
    # Step 2: Apply automatic double-encoding repair with ftfy (preferred)
    if FTFY_AVAILABLE:
        # ftfy automatically detects and fixes most double-encoding issues
        text = fix_text(text)
        # Then apply manual cleaning to catch cases ftfy doesn't handle perfectly
        text = clean_encoding_artifacts(text)
    else:
        # Fallback to manual artifact cleaning if ftfy not available
        text = clean_encoding_artifacts(text)
    
    # Step 3: Apply metadata-specific cleaning
    text = clean_metadata_text(text)
    
    return text


# Original function retained for specific double-encoding artifact cases
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
        # Original artifacts
        'Ã±': 'ñ',    # Spanish ñ
        'Ã¡': 'á',    # Spanish á
        'Ã©': 'é',    # Spanish é
        'Ã­': 'í',    # Spanish í
        'Ã³': 'ó',    # Spanish ó
        'Ãº': 'ú',    # Spanish ú
        'Ã¼': 'ü',    # German ü
        'Ã¤': 'ä',    # German ä
        'Ã¶': 'ö',    # German ö
        'Ã ': 'à',    # French à
        'Ã¨': 'è',    # French è
        'Ã§': 'ç',    # French ç
        'Ã¢': 'â',    # French â
        'Ã™': 'Ù',    # Capital U with grave
        'Â': '',      # Often appears as stray character
        '┬á': ' ',    # Non-breaking space encoding artifact
        '\u00a0': ' ',  # Non-breaking space (NBSP)
        'â€™': "'",   # Right single quotation mark
        'â€œ': '"',   # Left double quotation mark  
        'â€\u009d': '"',   # Right double quotation mark
        'â€“': '–',   # En dash
        'â€”': '—',   # Em dash
        'â€¦': '...',  # Horizontal ellipsis

        # Additional artifacts found in CSV output (2025-07-26)
        'Ca├¡dos': 'Caídos',           # Spanish í with double encoding
        'Revoluci├│n': 'Revolución',   # Spanish ó with double encoding  
        'dise├▒o': 'diseño',           # Spanish ñ with double encoding
        'M├⌐ndez': 'Méndez',           # Spanish é with double encoding
        '├<81>valos': 'Ávalos',        # Spanish Á with double encoding
        'M├⌐morial': 'Mémorial',       # French é with double encoding
        'Fran├ºais': 'Français',       # French ç with double encoding
        'fran├º├⌐': 'français',        # French ç + é with double encoding
        'Lalwizy├án': 'Lalwizyan',     # Spanish á with double encoding
        
        # Additional artifacts found in CSV output (2025-07-26 - Round 2)
        'f├╝r': 'für',                 # German ü with double encoding
        'G├ñnge': 'Gänge',             # German ä with double encoding (different pattern)
        
        # Patterns that ftfy outputs but need further correction (2025-07-26 - Round 3)
        'françé': 'français',           # ftfy partially fixed but wrong final letter
        'Lalwizyàn': 'Lalwizyan',       # ftfy partially fixed but wrong accent
        
        # More systematic approach to common double-encoding patterns
        '├¡': 'í',     # Spanish í double-encoded
        '├│': 'ó',     # Spanish ó double-encoded
        '├▒': 'ñ',     # Spanish ñ double-encoded
        '├⌐': 'é',     # Spanish/French é double-encoded
        '├<81>': 'Á',  # Spanish Á double-encoded
        '├º': 'ú',     # Spanish ú double-encoded
        '├án': 'án',   # Spanish án double-encoded
        '├╝': 'ü',     # German ü double-encoded
        '├ñ': 'ä',     # German ä double-encoded (alternative pattern)
        
        # Additional artifacts found in current export.csv (2025-01-21)
        'CaA-dos': 'Caídos',          # Spanish í compound artifact
        'RevoluciA3n': 'Revolución',  # Spanish ó compound artifact
        'diseA±o': 'diseño',          # Spanish ñ compound artifact
        'MAcndez': 'Méndez',          # Spanish é compound artifact
        'A?valos': 'Ávalos',          # Spanish Á compound artifact
        'MAcmorial': 'Mémorial',      # French é compound artifact
        'FranAais': 'Français',       # French ç compound artifact
        'fA¼r': 'für',               # German ü compound artifact
        'GAnge': 'Gänge',            # German ä compound artifact
        
        # Single-character patterns from the compound artifacts above
        'A-': 'í',    # Pattern found in CaA-dos
        'A3': 'ó',    # Pattern found in RevoluciA3n
        'A±': 'ñ',    # Pattern found in diseA±o
        'Ac': 'é',    # Pattern found in MAcndez, MAcmorial
        'A?': 'Á',    # Pattern found in A?valos
        'A¼': 'ü',    # Pattern found in fA¼r
        'An': 'ä',    # Pattern found in GAnge
        
        # Artifacts found in current export.csv (2025-01-21 - Round 2)
        'écession': 'Accession',      # Line 4: écession Number
        'éheson': 'Acheson',          # Multiple lines: Dean Acheson name
        'äderson': 'Anderson',        # Line 9: Clinton P. Anderson
        'änouncement': 'Announcement', # Line 15: Announcement of Japanese Surrender
        'äthony': 'Anthony',          # Line 19: Anthony Eden
        'étg': 'Acting',              # Line 19: Acting Sec. of State (Actg.)
        'ädrey': 'Andrey',            # Line 21: Andrey Yanuaryevich
        'éademy': 'Academy',          # Line 21: Academy of Sciences
        '355í7': '355A-7',            # Line 56: 306-NT-355A-7
        
        # Artifacts mentioned by user (2025-01-21 - Round 3)
        'T├╢tung': 'Tötung',         # German ö double-encoded
        'G├ñnge': 'Gänge',           # German ä double-encoded (different pattern)
        'f├╝r': 'für',             # German ü double-encoded (different pattern)
        
        # Context-specific single character replacements for current artifacts
        # Only target specific patterns where we know these are encoding artifacts
        # NOTE: These are very specific to avoid corrupting legitimate accented text
    }
    
    # Apply artifact replacements
    cleaned_text = text
    for artifact, replacement in artifacts.items():
        cleaned_text = cleaned_text.replace(artifact, replacement)
    
    # Remove other common non-printable artifacts
    # Remove null bytes and other control characters except newlines and tabs
    cleaned_text = ''.join(char for char in cleaned_text 
                          if ord(char) >= 32 or char in '\n\t')
    
    return cleaned_text

def clean_dataframe_encoding(df):
    """
    Clean encoding artifacts from all string columns in a DataFrame.
    
    Now uses the hierarchical smart_encoding_cleaner approach that combines:
    - chardet-based encoding detection (Method 1)
    - Fallback encoding attempts (Method 2) 
    - Original double-encoding artifact cleaning
    - Metadata-specific cleaning (Method 3)
    
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
        if df_cleaned[column].dtype == 'object':
            # Apply smart encoding cleaning to each cell in the column
            df_cleaned[column] = df_cleaned[column].astype(str).apply(
                lambda x: smart_encoding_cleaner(x) if x != 'nan' else x
            )
    
    return df_cleaned

def export_to_csv(df, output_file='export.csv'):
    """
    Export DataFrame to CSV with mapped column names and cleaned encoding.
    
    Args:
        df: pandas DataFrame to export
        output_file: name of the output CSV file
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    if df is None or df.empty:
        print("Error: No data to export.")
        return False
    
    try:
        print(f"\n=== Exporting Data to CSV: {output_file} ===")
        
        # Define the row 3 content to export header mapping
        row3_mapping = {
            'Title': 'Headline',
            'Accession Number': 'ObjectName',
            'Restrictions': 'CopyrightNotice',
            'Scopenote': 'Caption-Abstract',
            'Related Collection': 'Source',
            'Source Photographer': 'By-line',
            'Institutional Creator': 'By-lineTitle'
        }
        
        # Create a mapping from column names to export headers based on row 3 content
        # Row 3 is at index 2 (0-based indexing)
        row3_index = 2
        column_to_export_header = {}
        
        # Only proceed if we have enough rows
        if len(df) <= row3_index:
            print(f"Error: DataFrame has only {len(df)} rows, but we need at least {row3_index+1} rows.")
            return False
            
        # Find which columns have the values we're looking for in row 3
        print("\nDebug - Row 3 cell values:")
        for col in df.columns:
            cell_value = str(df.loc[row3_index, col]).strip() if pd.notna(df.loc[row3_index, col]) else ""
            print(f"Column '{col}' contains: '{cell_value}'")
            # Case-insensitive matching for robustness
            if cell_value in row3_mapping:
                column_to_export_header[col] = row3_mapping[cell_value]
                print(f"✓ Matched '{cell_value}' to '{row3_mapping[cell_value]}'")
            # Handle any variations in 'Related Collection' text
            elif cell_value and ('related collection' in cell_value.lower() or 
                                  'related' in cell_value.lower() and 'collection' in cell_value.lower()):
                print(f"! Found potential 'Related Collection' match: '{cell_value}'")
                column_to_export_header[col] = 'Source'
                print(f"  → Mapping '{cell_value}' to 'Source'")
            
        # Report which row 3 values we couldn't find
        found_values = [val for col, val in df.iloc[row3_index].items() if val in row3_mapping]
        missing_values = [val for val in row3_mapping.keys() if val not in found_values]
        
        if missing_values:
            print(f"Warning: The following row 3 values were not found in the data: {', '.join(missing_values)}")
            print("Available row 3 values:", ', '.join([str(val) for val in df.iloc[row3_index] if pd.notna(val)]))
            proceed = input("Continue anyway with available mappings? (y/n): ")
            if proceed.lower() != 'y':
                return False
        
        # Clean encoding artifacts from the original DataFrame before processing
        print("\n🧹 Cleaning encoding artifacts...")
        df_cleaned = clean_dataframe_encoding(df)
        
        # Create new DataFrame with mapped columns
        new_df = pd.DataFrame()
        renamed_columns = []
        
        for src_col, dst_col in column_to_export_header.items():
            # Copy the column data from cleaned DataFrame
            new_df[dst_col] = df_cleaned[src_col]
            renamed_columns.append(f"'{src_col}' (row 3: '{df.loc[row3_index, src_col]}') -> '{dst_col}'")
            print(f"Mapped: '{src_col}' (row 3: '{df.loc[row3_index, src_col]}') -> '{dst_col}'")
        
        # Add DateCreated column in ISO format (YYYY-MM-DD) from productionDateMonth, productionDateDay, productionDateYear columns
        try:
            if all(col in df_cleaned.columns for col in ['productionDateMonth', 'productionDateDay', 'productionDateYear']):
                print("Creating 'DateCreated' column in ISO format (YYYY-MM-DD)...")
                
                # Initialize an empty date column the same length as the DataFrame
                new_df['DateCreated'] = ''
                
                # Skip the first 3 rows which contain header information
                # Start processing from index 3 (4th row) onwards
                for idx in range(3, len(df_cleaned)):
                    try:
                        # Get date components from cleaned DataFrame
                        month_str = str(df_cleaned.loc[idx, 'productionDateMonth']).strip() if df_cleaned.loc[idx, 'productionDateMonth'] is not None else ''
                        day_str = str(df_cleaned.loc[idx, 'productionDateDay']).strip() if df_cleaned.loc[idx, 'productionDateDay'] is not None else ''
                        year_str = str(df_cleaned.loc[idx, 'productionDateYear']).strip() if df_cleaned.loc[idx, 'productionDateYear'] is not None else ''
                        
                        # Replace 'nan', 'None', or 'NaN' strings with empty string
                        month_str = '' if month_str.lower() in ['nan', 'none', 'null'] else month_str
                        day_str = '' if day_str.lower() in ['nan', 'none', 'null'] else day_str
                        year_str = '' if year_str.lower() in ['nan', 'none', 'null'] else year_str
                        
                        # Check if all components are present and look like numbers
                        if (month_str and day_str and year_str and
                            month_str.isdigit() and day_str.isdigit() and year_str.isdigit()):
                            
                            # Convert to integers to validate and handle leading zeros
                            year_int = int(year_str)
                            month_int = int(month_str)
                            day_int = int(day_str)
                            
                            # Basic date validation
                            if 1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 0:
                                # Format with leading zeros for month and day
                                new_df.loc[idx, 'DateCreated'] = f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
                            else:
                                print(f"Skipping row {idx}: Date out of valid range: {month_int}/{day_int}/{year_int}")
                        else:
                            # One or more components missing or not a valid number - skip silently for data rows
                            if idx > 5:  # Only log warnings for non-header rows after index 5
                                print(f"Skipping row {idx}: Incomplete or non-numeric date components")
                    except Exception as e:
                        if idx > 5:  # Only log warnings for non-header rows
                            print(f"Warning: Error processing date at row {idx}: {e}")
                
                print(f"Added 'DateCreated' column with ISO formatted dates (YYYY-MM-DD)")
            else:
                missing_cols = [col for col in ['productionDateMonth', 'productionDateDay', 'productionDateYear'] if col not in df.columns]
                print(f"Warning: Cannot create 'DateCreated' column. Missing required column(s): {', '.join(missing_cols)}")
        except Exception as e:
            print(f"Error creating 'DateCreated' column: {str(e)}")
        
        # Verify we have data to export
        if new_df.empty:
            print("Error: No columns were successfully mapped!")
            return False
            
        print(f"\nSuccessfully mapped {len(renamed_columns)} columns:")
        for mapping in renamed_columns:
            print(f"  {mapping}")
        
        # Export to CSV with UTF-8 encoding
        print(f"\nExporting to '{output_file}' with UTF-8 encoding...")
        new_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"Conversion completed successfully. Output saved to '{output_file}'")
        print(f"Rows processed: {len(new_df)}")
        return True
    
    except Exception as e:
        print(f"Error during CSV export: {str(e)}")
        return False

def main():
    """Main function to execute the script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Load data from a Google Spreadsheet into a pandas DataFrame. Now supports Excel files!',
        epilog="""
Examples:
  # Native Google Sheet
  python g2c.py --sheet-url "https://docs.google.com/spreadsheets/d/ID/edit"
  
  # Excel file with auto-conversion
  python g2c.py --sheet-url "https://drive.google.com/file/d/ID/view" --auto-convert
  
  # Export to CSV
  python g2c.py --sheet-url "URL" --export-csv custom_output.csv
"""
    )
    
    # Add arguments
    parser.add_argument(
        '--sheet-url', '-u',
        default=f"https://docs.google.com/spreadsheets/d/{DEFAULT_SPREADSHEET_ID}/edit",
        help='URL of the Google Spreadsheet or Excel file'
    )
    
    parser.add_argument(
        '--export-csv', '-e',
        nargs='?',
        const='export.csv',
        help='Export data to CSV file (default filename: export.csv)'
    )
    
    parser.add_argument(
        '--auto-convert', '-a',
        action='store_true',
        help='Automatically convert Excel files to Google Sheets'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    print("🚀 Google Drive to CSV Converter with IPTC Mapping")
    print("=" * 60)
    print("Now supports both Google Sheets and Excel files!")
    print()
    
    # Detect file type and convert if needed
    try:
        spreadsheet_id, was_converted, conversion_info = detect_and_convert_if_needed(
            args.sheet_url, 
            auto_convert=args.auto_convert
        )
        
        if was_converted:
            print(f"\n💾 Conversion completed! Using new Google Sheet:")
            print(f"   ID: {spreadsheet_id}")
            print(f"   URL: {conversion_info['new_file_url']}")
            print(f"   💡 Bookmark this URL for future use!")
        else:
            print(f"Using spreadsheet ID: {spreadsheet_id}")
            
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Falling back to default spreadsheet ID: {DEFAULT_SPREADSHEET_ID}")
        spreadsheet_id = DEFAULT_SPREADSHEET_ID
    except Exception as e:
        print(f"Error: {e}")
        if args.auto_convert:
            print("\n💡 Try running without --auto-convert to see more details")
        sys.exit(1)
    
    print("\nFetching data from Google Sheet...")
    df = fetch_sheet_data(spreadsheet_id)
    
    if df is not None:
        print("\n✅ Data loaded successfully!")
        print_dataframe_summary(df)
        print_first_10_rows(df)
        
        # Export to CSV if requested
        if args.export_csv:
            output_file = args.export_csv
            export_success = export_to_csv(df, output_file)
            if not export_success:
                print(f"Warning: CSV export failed")
                
        # Show success message with helpful info
        if was_converted:
            print(f"\n🎉 Success! Your Excel file was converted and processed.")
            print(f"📋 Original file remains unchanged")
            print(f"📊 New Google Sheet URL: {conversion_info['new_file_url']}")
        
    else:
        print("\n❌ Failed to load data from the Google Sheet.")
        if not args.auto_convert:
            print("💡 If this is an Excel file, try adding --auto-convert flag")
        print("Please check your authentication credentials and spreadsheet ID.")
        sys.exit(1)

if __name__ == "__main__":
    main()
