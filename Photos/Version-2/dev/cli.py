#!/usr/bin/env python3
"""
Command-Line Interface for Google Sheets Type Detection and Conversion

This CLI tool provides easy access to the sheets detection and conversion functionality.

Usage Examples:
    python cli.py detect "https://docs.google.com/spreadsheets/d/1BxC.../edit"
    python cli.py convert "1BxC..." --auto-convert
    python cli.py validate "1BxC..."
    python cli.py batch-convert urls.txt --folder-id "folder123"
"""

import argparse
import sys
import json
from typing import List, Optional

try:
    from . import (
        detect_sheet_type,
        convert_spreadsheet_to_sheet,
        validate_sheet_access,
        batch_convert_to_sheets,
        quick_detect_and_convert,
        create_conversion_folder,
        SheetsTypeDetector
    )
except ImportError:
    # If running as a script directly
    from sheets_type_detector import (
        detect_sheet_type,
        validate_sheet_access,
        SheetsTypeDetector
    )
    from sheets_converter import (
        convert_spreadsheet_to_sheet,
        batch_convert_to_sheets,
        create_conversion_folder
    )


def print_json_result(result: dict, indent: int = 2):
    """Print a result dictionary as formatted JSON."""
    print(json.dumps(result, indent=indent, default=str))


def print_detection_result(result: dict):
    """Print detection result in a human-readable format."""
    print(f"\n📊 Sheet Detection Results")
    print(f"{'='*50}")
    print(f"File ID: {result['file_id']}")
    print(f"File Name: {result['file_name']}")
    print(f"MIME Type: {result['mime_type']}")
    print(f"Is Native Google Sheet: {'✅ Yes' if result['is_native_sheet'] else '❌ No'}")
    print(f"Is Excel File: {'✅ Yes' if result['is_excel'] else '❌ No'}")
    print(f"Can Convert: {'✅ Yes' if result['can_convert'] else '❌ No'}")
    
    if result['is_native_sheet']:
        print(f"\n💡 This file is already a native Google Sheet and is ready to use.")
    elif result['is_excel']:
        print(f"\n💡 This Excel file can be converted to a native Google Sheet for better compatibility.")
    else:
        print(f"\n⚠️  This file type may not be fully compatible with Google Sheets operations.")


def print_conversion_result(result: dict):
    """Print conversion result in a human-readable format."""
    print(f"\n🔄 Conversion Results")
    print(f"{'='*50}")
    
    if result['success']:
        print(f"✅ Conversion Successful!")
        print(f"New File ID: {result['new_file_id']}")
        print(f"New File Name: {result['new_file_name']}")
        print(f"New File URL: {result['new_file_url']}")
        print(f"Original File ID: {result['original_file_id']}")
    else:
        print(f"❌ Conversion Failed!")
        print(f"Error: {result['error_message']}")


def print_validation_result(result: dict):
    """Print validation result in a human-readable format."""
    print(f"\n🔐 Access Validation Results")
    print(f"{'='*50}")
    
    if result['has_access']:
        print(f"✅ Access Granted")
        print(f"Access Level: {result['access_level']}")
        print(f"Can Read: {'✅ Yes' if result['can_read'] else '❌ No'}")
        print(f"Can Write: {'✅ Yes' if result['can_write'] else '❌ No' if result['can_write'] is not None else '❓ Unknown'}")
    else:
        print(f"❌ Access Denied")
        print(f"Error: {result['error_message']}")


def cmd_detect(args):
    """Handle the detect command."""
    try:
        detector = SheetsTypeDetector(
            client_secret_file=args.credentials,
            token_file=args.token
        )
        
        result = detect_sheet_type(args.url_or_id, detector)
        
        if args.json:
            print_json_result(result)
        else:
            print_detection_result(result)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_convert(args):
    """Handle the convert command."""
    try:
        detector = SheetsTypeDetector(
            client_secret_file=args.credentials,
            token_file=args.token
        )
        
        if args.auto_convert:
            # Use the quick detect and convert function
            result = quick_detect_and_convert(args.url_or_id, auto_convert=True)
            
            if args.json:
                print_json_result(result)
            else:
                print_detection_result(result['detection_result'])
                if result['conversion_attempted']:
                    print_conversion_result(result['conversion_result'])
                print(f"\n💡 Recommendation: {result['recommendation']}")
        else:
            # Just detect first
            detection_result = detect_sheet_type(args.url_or_id, detector)
            
            if args.json:
                print_json_result(detection_result)
            else:
                print_detection_result(detection_result)
                
                if detection_result['can_convert']:
                    print(f"\n💡 To convert this file, run the command again with --auto-convert flag")
                    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args):
    """Handle the validate command."""
    try:
        detector = SheetsTypeDetector(
            client_secret_file=args.credentials,
            token_file=args.token
        )
        
        result = validate_sheet_access(args.url_or_id, detector)
        
        if args.json:
            print_json_result(result)
        else:
            print_validation_result(result)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_batch_convert(args):
    """Handle the batch-convert command."""
    try:
        # Read URLs from file
        with open(args.input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("No URLs found in input file", file=sys.stderr)
            sys.exit(1)
            
        detector = SheetsTypeDetector(
            client_secret_file=args.credentials,
            token_file=args.token
        )
        
        result = batch_convert_to_sheets(
            urls,
            detector=detector,
            parent_folder_id=args.folder_id,
            delay_seconds=args.delay
        )
        
        if args.json:
            print_json_result(result)
        else:
            print(f"\n📦 Batch Conversion Results")
            print(f"{'='*50}")
            print(f"Total Files: {result['total_files']}")
            print(f"Successful: {result['successful_conversions']}")
            print(f"Failed: {result['failed_conversions']}")
            print(f"\n{result['summary']}")
            
    except FileNotFoundError:
        print(f"Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_create_folder(args):
    """Handle the create-folder command."""
    try:
        detector = SheetsTypeDetector(
            client_secret_file=args.credentials,
            token_file=args.token
        )
        
        result = create_conversion_folder(
            folder_name=args.name,
            parent_folder_id=args.parent_id,
            detector=detector
        )
        
        if args.json:
            print_json_result(result)
        else:
            if result['success']:
                print(f"✅ Folder created successfully!")
                print(f"Folder ID: {result['folder_id']}")
                print(f"Folder Name: {result['folder_name']}")
                print(f"Folder URL: {result['folder_url']}")
            else:
                print(f"❌ Failed to create folder: {result['error_message']}")
                
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Google Sheets Type Detection and Conversion CLI",
        epilog="""
Examples:
  # Detect sheet type
  python cli.py detect "https://docs.google.com/spreadsheets/d/1BxC.../edit"
  
  # Convert Excel to Google Sheets
  python cli.py convert "1BxC..." --auto-convert
  
  # Validate access permissions
  python cli.py validate "1BxC..."
  
  # Batch convert from file
  python cli.py batch-convert urls.txt --folder-id "folder123"
  
  # Create conversion folder
  python cli.py create-folder "My Converted Sheets"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument(
        '--credentials', '-c',
        default='credentials.json',
        help='Path to Google API credentials file (default: credentials.json)'
    )
    parser.add_argument(
        '--token', '-t',
        default='token.pickle',
        help='Path to store authentication token (default: token.pickle)'
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output results in JSON format'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Detect Google Sheets file type')
    detect_parser.add_argument('url_or_id', help='Google Sheets URL or file ID')
    detect_parser.set_defaults(func=cmd_detect)
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert Excel to Google Sheets')
    convert_parser.add_argument('url_or_id', help='Google Sheets URL or file ID')
    convert_parser.add_argument(
        '--auto-convert', '-a',
        action='store_true',
        help='Automatically convert Excel files to Google Sheets'
    )
    convert_parser.set_defaults(func=cmd_convert)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate access to Google Sheets file')
    validate_parser.add_argument('url_or_id', help='Google Sheets URL or file ID')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Batch convert command
    batch_parser = subparsers.add_parser('batch-convert', help='Convert multiple files from a list')
    batch_parser.add_argument('input_file', help='Text file containing URLs/IDs (one per line)')
    batch_parser.add_argument(
        '--folder-id', '-f',
        help='Google Drive folder ID to store converted files'
    )
    batch_parser.add_argument(
        '--delay', '-d',
        type=float,
        default=1.0,
        help='Delay between conversions in seconds (default: 1.0)'
    )
    batch_parser.set_defaults(func=cmd_batch_convert)
    
    # Create folder command
    folder_parser = subparsers.add_parser('create-folder', help='Create a folder for converted sheets')
    folder_parser.add_argument('name', help='Name for the new folder')
    folder_parser.add_argument(
        '--parent-id', '-p',
        help='Parent folder ID (default: root)'
    )
    folder_parser.set_defaults(func=cmd_create_folder)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    args.func(args)


if __name__ == '__main__':
    main()
