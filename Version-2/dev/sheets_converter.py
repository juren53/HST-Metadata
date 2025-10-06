#!/usr/bin/env python3
"""
Google Sheets Conversion Module

This module provides functions to convert Excel files to native Google Sheets
and perform other utility operations related to Google Sheets management.
"""

import os
import time
from typing import Optional, Dict, Any, List
from googleapiclient.errors import HttpError
try:
    from .sheets_type_detector import SheetsTypeDetector, detect_sheet_type
except ImportError:
    from sheets_type_detector import SheetsTypeDetector, detect_sheet_type


def convert_spreadsheet_to_sheet(url_or_id: str, 
                                detector: Optional[SheetsTypeDetector] = None,
                                new_name: Optional[str] = None,
                                parent_folder_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert an Excel file to a native Google Sheet.
    
    This function creates a copy of an Excel file in Google Drive and converts
    it to a native Google Sheet format. The original file remains unchanged.
    
    Args:
        url_or_id: Google Drive URL or file ID of the Excel file
        detector: SheetsTypeDetector instance (creates new one if None)
        new_name: Name for the new Google Sheet (optional)
        parent_folder_id: ID of folder to place the converted sheet (optional)
        
    Returns:
        Dict containing:
        - success: Boolean indicating if conversion succeeded
        - new_file_id: ID of the newly created Google Sheet
        - new_file_name: Name of the new Google Sheet
        - new_file_url: URL to access the new Google Sheet
        - original_file_id: ID of the original Excel file
        - error_message: Error message if conversion failed
        
    Raises:
        ValueError: If the file is not an Excel file or already a Google Sheet
        PermissionError: If insufficient permissions to access or convert the file
        Exception: If the conversion process fails
        
    Example:
        >>> result = convert_spreadsheet_to_sheet('1BxC...')
        >>> if result['success']:
        ...     print(f"Converted to: {result['new_file_url']}")
    """
    if detector is None:
        detector = SheetsTypeDetector()
    
    try:
        # First, detect the current file type
        file_info = detect_sheet_type(url_or_id, detector)
        
        if file_info['is_native_sheet']:
            return {
                'success': False,
                'new_file_id': None,
                'new_file_name': None,
                'new_file_url': None,
                'original_file_id': file_info['file_id'],
                'error_message': 'File is already a native Google Sheet'
            }
        
        if not file_info['is_excel']:
            return {
                'success': False,
                'new_file_id': None,
                'new_file_name': None,
                'new_file_url': None,
                'original_file_id': file_info['file_id'],
                'error_message': f"File type not supported for conversion: {file_info['mime_type']}"
            }
        
        # Prepare the new file name
        original_name = file_info['file_name']
        if new_name is None:
            # Remove file extension and add "- Google Sheets" suffix
            base_name = os.path.splitext(original_name)[0]
            new_name = f"{base_name} - Google Sheets"
        
        # Set up the copy request
        drive_service = detector._get_drive_service()
        copy_body = {
            'name': new_name,
            'mimeType': SheetsTypeDetector.NATIVE_SHEET_MIME
        }
        
        # Add parent folder if specified
        if parent_folder_id:
            copy_body['parents'] = [parent_folder_id]
        
        # Perform the conversion by copying the file with new MIME type
        print(f"Converting '{original_name}' to Google Sheets format...")
        copied_file = drive_service.files().copy(
            fileId=file_info['file_id'],
            body=copy_body,
            fields='id,name,mimeType,webViewLink'
        ).execute()
        
        new_file_id = copied_file['id']
        new_file_name = copied_file['name']
        new_file_url = copied_file.get('webViewLink', f"https://docs.google.com/spreadsheets/d/{new_file_id}/edit")
        
        print(f"Conversion successful! New file ID: {new_file_id}")
        
        return {
            'success': True,
            'new_file_id': new_file_id,
            'new_file_name': new_file_name,
            'new_file_url': new_file_url,
            'original_file_id': file_info['file_id'],
            'error_message': None
        }
        
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_reason = error_details.get('reason', 'unknown')
        
        if e.resp.status == 403:
            error_message = f"Permission denied: Unable to convert file. Check sharing permissions."
        elif e.resp.status == 404:
            error_message = f"File not found: {url_or_id}"
        else:
            error_message = f"Google Drive API error ({e.resp.status}): {error_reason}"
        
        return {
            'success': False,
            'new_file_id': None,
            'new_file_name': None,
            'new_file_url': None,
            'original_file_id': None,
            'error_message': error_message
        }
    
    except Exception as e:
        return {
            'success': False,
            'new_file_id': None,
            'new_file_name': None,
            'new_file_url': None,
            'original_file_id': None,
            'error_message': f"Conversion failed: {str(e)}"
        }


def batch_convert_to_sheets(file_urls_or_ids: List[str],
                           detector: Optional[SheetsTypeDetector] = None,
                           parent_folder_id: Optional[str] = None,
                           delay_seconds: float = 1.0) -> Dict[str, Any]:
    """
    Convert multiple Excel files to native Google Sheets in batch.
    
    Args:
        file_urls_or_ids: List of Google Drive URLs or file IDs
        detector: SheetsTypeDetector instance (creates new one if None)
        parent_folder_id: ID of folder to place converted sheets (optional)
        delay_seconds: Delay between conversions to avoid rate limiting
        
    Returns:
        Dict containing:
        - total_files: Total number of files processed
        - successful_conversions: Number of successful conversions
        - failed_conversions: Number of failed conversions
        - results: List of individual conversion results
        - summary: Summary of the batch operation
        
    Example:
        >>> urls = ['1BxC...', '2DxE...', '3FxG...']
        >>> result = batch_convert_to_sheets(urls)
        >>> print(f"Converted {result['successful_conversions']} out of {result['total_files']} files")
    """
    if detector is None:
        detector = SheetsTypeDetector()
    
    results = []
    successful_conversions = 0
    failed_conversions = 0
    
    print(f"Starting batch conversion of {len(file_urls_or_ids)} files...")
    
    for i, url_or_id in enumerate(file_urls_or_ids, 1):
        print(f"\nProcessing file {i}/{len(file_urls_or_ids)}: {url_or_id}")
        
        try:
            result = convert_spreadsheet_to_sheet(
                url_or_id, 
                detector=detector,
                parent_folder_id=parent_folder_id
            )
            
            results.append({
                'input': url_or_id,
                'result': result
            })
            
            if result['success']:
                successful_conversions += 1
                print(f"✓ Converted: {result['new_file_name']}")
            else:
                failed_conversions += 1
                print(f"✗ Failed: {result['error_message']}")
                
        except Exception as e:
            failed_conversions += 1
            error_result = {
                'success': False,
                'error_message': f"Unexpected error: {str(e)}"
            }
            results.append({
                'input': url_or_id,
                'result': error_result
            })
            print(f"✗ Failed: {str(e)}")
        
        # Add delay to avoid rate limiting (except for the last item)
        if i < len(file_urls_or_ids) and delay_seconds > 0:
            time.sleep(delay_seconds)
    
    summary = f"Batch conversion completed: {successful_conversions} successful, {failed_conversions} failed"
    print(f"\n{summary}")
    
    return {
        'total_files': len(file_urls_or_ids),
        'successful_conversions': successful_conversions,
        'failed_conversions': failed_conversions,
        'results': results,
        'summary': summary
    }


def get_sheet_url_from_id(file_id: str) -> str:
    """
    Generate a Google Sheets URL from a file ID.
    
    Args:
        file_id: Google Drive file ID
        
    Returns:
        str: Complete Google Sheets URL
        
    Example:
        >>> url = get_sheet_url_from_id('1BxC...')
        >>> print(url)  # https://docs.google.com/spreadsheets/d/1BxC.../edit
    """
    return f"https://docs.google.com/spreadsheets/d/{file_id}/edit"


def create_conversion_folder(folder_name: str = "Converted Google Sheets",
                           parent_folder_id: Optional[str] = None,
                           detector: Optional[SheetsTypeDetector] = None) -> Dict[str, Any]:
    """
    Create a folder in Google Drive to store converted sheets.
    
    Args:
        folder_name: Name for the new folder
        parent_folder_id: ID of parent folder (None for root)
        detector: SheetsTypeDetector instance (creates new one if None)
        
    Returns:
        Dict containing:
        - success: Boolean indicating if folder creation succeeded
        - folder_id: ID of the created folder
        - folder_name: Name of the created folder
        - folder_url: URL to view the folder
        - error_message: Error message if creation failed
        
    Example:
        >>> result = create_conversion_folder("My Converted Sheets")
        >>> if result['success']:
        ...     print(f"Folder created: {result['folder_url']}")
    """
    if detector is None:
        detector = SheetsTypeDetector()
    
    try:
        drive_service = detector._get_drive_service()
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
        
        folder = drive_service.files().create(
            body=folder_metadata,
            fields='id,name,webViewLink'
        ).execute()
        
        return {
            'success': True,
            'folder_id': folder['id'],
            'folder_name': folder['name'],
            'folder_url': folder.get('webViewLink', f"https://drive.google.com/drive/folders/{folder['id']}"),
            'error_message': None
        }
        
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_reason = error_details.get('reason', 'unknown')
        
        return {
            'success': False,
            'folder_id': None,
            'folder_name': None,
            'folder_url': None,
            'error_message': f"Failed to create folder: {error_reason}"
        }
    
    except Exception as e:
        return {
            'success': False,
            'folder_id': None,
            'folder_name': None,
            'folder_url': None,
            'error_message': f"Unexpected error: {str(e)}"
        }


def list_files_in_folder(folder_id: str,
                        detector: Optional[SheetsTypeDetector] = None,
                        file_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    List files in a Google Drive folder, optionally filtered by type.
    
    Args:
        folder_id: ID of the Google Drive folder
        detector: SheetsTypeDetector instance (creates new one if None)
        file_types: List of MIME types to filter by (optional)
        
    Returns:
        Dict containing:
        - success: Boolean indicating if listing succeeded
        - files: List of file information dictionaries
        - total_count: Total number of files found
        - error_message: Error message if listing failed
        
    Example:
        >>> excel_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        >>> result = list_files_in_folder('folder_id', file_types=excel_types)
        >>> print(f"Found {len(result['files'])} Excel files")
    """
    if detector is None:
        detector = SheetsTypeDetector()
    
    try:
        drive_service = detector._get_drive_service()
        
        # Build query
        query = f"'{folder_id}' in parents and trashed=false"
        
        if file_types:
            mime_conditions = " or ".join([f"mimeType='{mime}'" for mime in file_types])
            query += f" and ({mime_conditions})"
        
        # Get files
        results = drive_service.files().list(
            q=query,
            fields="files(id,name,mimeType,webViewLink,createdTime,modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        
        return {
            'success': True,
            'files': files,
            'total_count': len(files),
            'error_message': None
        }
        
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_reason = error_details.get('reason', 'unknown')
        
        return {
            'success': False,
            'files': [],
            'total_count': 0,
            'error_message': f"Failed to list files: {error_reason}"
        }
    
    except Exception as e:
        return {
            'success': False,
            'files': [],
            'total_count': 0,
            'error_message': f"Unexpected error: {str(e)}"
        }
