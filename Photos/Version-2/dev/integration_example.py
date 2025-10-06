"""
Integration example showing how to modify existing google-to-csv.py code
to work with both native Google Sheets and Excel files.
"""

import logging
from sheets_detector import GoogleSheetsDetector, ensure_compatible_url, SheetType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enhanced_google_to_csv(sheet_url, credentials, output_file="output.csv"):
    """
    Enhanced version of google-to-csv that handles both native Google Sheets
    and Excel files viewed in Google Sheets.
    
    Args:
        sheet_url: URL to Google Sheet or Excel file in Google Drive
        credentials: Google API credentials
        output_file: Output CSV file path
    """
    try:
        # Step 1: Detect and ensure we have a native Google Sheet URL
        logger.info("Detecting sheet type...")
        detector = GoogleSheetsDetector(credentials)
        sheet_type, metadata = detector.detect_sheet_type(sheet_url)
        
        logger.info(f"Detected sheet type: {sheet_type.value}")
        if metadata:
            logger.info(f"File name: {metadata.get('name')}")
            logger.info(f"MIME type: {metadata.get('mimeType')}")
        
        # Step 2: Ensure we have a compatible URL
        compatible_url, was_converted = detector.ensure_native_google_sheet(sheet_url)
        
        if was_converted:
            logger.info("Excel file was converted to native Google Sheet")
            logger.info(f"New URL: {compatible_url}")
        
        # Step 3: Proceed with your existing google-to-csv logic
        # Replace this section with your actual CSV conversion code
        
        # Example of how your existing code would be modified:
        file_id = detector.extract_file_id(compatible_url)
        
        # Validate access before proceeding
        if not detector.validate_sheet_access(file_id):
            raise PermissionError("No access to the specified sheet")
        
        # Your existing CSV conversion logic here
        # service = build('sheets', 'v4', credentials=credentials)
        # sheet = service.spreadsheets()
        # result = sheet.values().get(spreadsheetId=file_id, range='A1:Z1000').execute()
        # values = result.get('values', [])
        
        # Write to CSV
        # with open(output_file, 'w', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     for row in values:
        #         writer.writerow(row)
        
        logger.info(f"Successfully processed sheet and would save to: {output_file}")
        return compatible_url
        
    except Exception as e:
        logger.error(f"Error processing sheet: {e}")
        raise

def batch_process_sheets(sheet_urls, credentials, output_dir="./outputs/"):
    """
    Process multiple sheets, handling different types automatically.
    
    Args:
        sheet_urls: List of Google Sheet URLs
        credentials: Google API credentials  
        output_dir: Directory to save CSV files
    """
    results = []
    
    for i, url in enumerate(sheet_urls):
        try:
            logger.info(f"Processing sheet {i+1}/{len(sheet_urls)}")
            
            # Generate output filename
            detector = GoogleSheetsDetector(credentials)
            _, metadata = detector.detect_sheet_type(url)
            
            if metadata and metadata.get('name'):
                filename = f"{metadata['name']}.csv"
            else:
                filename = f"sheet_{i+1}.csv"
            
            output_path = f"{output_dir}/{filename}"
            
            # Process the sheet
            final_url = enhanced_google_to_csv(url, credentials, output_path)
            
            results.append({
                'original_url': url,
                'final_url': final_url,
                'output_file': output_path,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
            results.append({
                'original_url': url,
                'final_url': None,
                'output_file': None,
                'status': 'failed',
                'error': str(e)
            })
    
    return results

# Example of how to modify your existing main function
def main():
    """
    Example main function showing integration with existing code.
    """
    # Your existing credential loading code here
    # credentials = load_credentials()  # Your existing credential loading
    
    # Example URLs - mix of native sheets and Excel files
    test_urls = [
        "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit",
        "https://drive.google.com/file/d/1example_excel_file_id/view"
    ]
    
    # Process sheets with automatic type detection and conversion
    # results = batch_process_sheets(test_urls, credentials)
    
    # Print results
    # for result in results:
    #     print(f"URL: {result['original_url']}")
    #     print(f"Status: {result['status']}")
    #     if result['status'] == 'success':
    #         print(f"Output: {result['output_file']}")
    #     print("-" * 50)

if __name__ == "__main__":
    main()

# Quick integration helper for your existing code
def make_url_compatible(url, credentials):
    """
    Simple wrapper function to make any Google Sheets URL compatible
    with code that expects native Google Sheets.
    
    Usage in your existing code:
    
    # Before:
    # sheet_url = "https://drive.google.com/file/d/excel_file_id/view"
    # process_sheet(sheet_url)  # This would fail
    
    # After:
    # sheet_url = "https://drive.google.com/file/d/excel_file_id/view" 
    # compatible_url = make_url_compatible(sheet_url, credentials)
    # process_sheet(compatible_url)  # This works!
    """
    return ensure_compatible_url(url, credentials)

# Integration pattern for your HST-Metadata project
def hst_metadata_integration_example():
    """
    Example showing how to integrate with your HST-Metadata project.
    """
    # This is how you'd modify your existing google-to-csv.py:
    
    # 1. Add this import at the top of your file:
    # from sheets_detector import ensure_compatible_url
    
    # 2. Before processing the sheet URL, add this line:
    # sheet_url = ensure_compatible_url(original_url, credentials)
    
    # 3. Then proceed with your existing logic
    
    sample_integration = '''
    # In your existing google-to-csv.py file:
    
    def main():
        # Your existing code to get credentials and URL
        credentials = get_credentials()  # Your existing function
        sheet_url = get_sheet_url()     # Your existing function
        
        # NEW: Ensure compatibility
        try:
            sheet_url = ensure_compatible_url(sheet_url, credentials)
            print(f"Using sheet URL: {sheet_url}")
        except Exception as e:
            print(f"Error processing sheet URL: {e}")
            return
        
        # Continue with your existing CSV processing logic
        process_sheet_to_csv(sheet_url, credentials)
    '''
    
    print("Integration pattern:")
    print(sample_integration)

# Error handling patterns
class SheetProcessingError(Exception):
    """Custom exception for sheet processing errors."""
    pass

def robust_sheet_processor(url, credentials):
    """
    Robust sheet processor with comprehensive error handling.
    """
    try:
        detector = GoogleSheetsDetector(credentials)
        
        # Detect type
        sheet_type, metadata = detector.detect_sheet_type(url)
        
        if sheet_type == SheetType.UNKNOWN:
            raise SheetProcessingError("Could not determine sheet type")
        
        # Validate access
        file_id = detector.extract_file_id(url)
        if not detector.validate_sheet_access(file_id):
            raise SheetProcessingError("No access to the specified sheet")
        
        # Ensure compatibility
        compatible_url, was_converted = detector.ensure_native_google_sheet(url)
        
        return {
            'success': True,
            'original_url': url,
            'compatible_url': compatible_url,
            'was_converted': was_converted,
            'sheet_type': sheet_type.value,
            'metadata': metadata
        }
        
    except Exception as e:
        return {
            'success': False,
            'original_url': url,
            'error': str(e),
            'error_type': type(e).__name__
        }
