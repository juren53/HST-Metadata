#!/usr/bin/env python3
"""
Analyze CSV file for non-UTF-8 characters and report their locations
Ver 0.4.2  - added character descriptions to output using Unicode names
"""

import sys
import csv
import re
import os
import unicodedata
from datetime import datetime

VERSION = "0.4.2"

# Simple logger to capture output for writing to a report file as well as console
_report_lines = []

def out(line: str = ""):
    print(line)
    _report_lines.append(line)

def is_ascii_printable(char):
    """Check if character is printable ASCII"""
    return 32 <= ord(char) <= 126

def get_character_description(char):
    """Get a human-readable description of a Unicode character"""
    try:
        # Get the official Unicode name
        unicode_name = unicodedata.name(char, None)
        
        if unicode_name:
            # Convert the Unicode name to a more readable format
            description = unicode_name.lower().replace('_', ' ').title()
            return f"{description}"
        else:
            # Fallback for characters without official names
            code_point = ord(char)
            if code_point <= 127:
                return "ASCII control character"
            elif code_point <= 255:
                return "Extended ASCII character"
            else:
                return "Unicode character"
    except Exception:
        return "Unknown character"

def find_non_utf8_chars(text):
    """Find non-standard UTF-8 characters in text"""
    suspicious_chars = []
    
    for i, char in enumerate(text):
        # Look for common mojibake patterns
        if char in ['À', 'Ã', 'â', '€', '™', 'š', 'œ', 'ž', 'Ÿ', '¡', '¢', '£', '¤', '¥', '¦', '§', '¨', '©', 'ª', '«', '¬', '®', '¯', '°', '±', '²', '³', '´', 'µ', '¶', '·', '¸', '¹', 'º', '»', '¼', '½', '¾', '¿']:
            suspicious_chars.append((i, char, ord(char)))
        # Look for high-bit characters that might be mojibake
        elif ord(char) > 127 and ord(char) < 256:
            suspicious_chars.append((i, char, ord(char)))
        # Look for unusual Unicode characters that might be encoding issues
        elif ord(char) > 8000:  # Arbitrary threshold for "unusual" Unicode
            suspicious_chars.append((i, char, ord(char)))
    
    return suspicious_chars

def highlight_suspicious_chars(text, suspicious_chars):
    """Highlight suspicious characters with visual markers"""
    if not suspicious_chars:
        return text
    
    # Use simple text highlighting that works in all terminals
    # Using < and > brackets to make suspicious characters stand out
    HIGHLIGHT_START = '<'
    HIGHLIGHT_END = '>'
    
    # Create a list of characters with highlighting
    highlighted = list(text)
    
    # Sort suspicious chars by position in reverse order to avoid index shifting
    suspicious_positions = sorted([pos for pos, char, code in suspicious_chars], reverse=True)
    
    # Add highlighting around each suspicious character
    for pos in suspicious_positions:
        if pos < len(highlighted):
            highlighted[pos] = f"{HIGHLIGHT_START}{highlighted[pos]}{HIGHLIGHT_END}"
    
    return ''.join(highlighted)

def get_object_name_from_line(line, objectname_column_index):
    """Extract ObjectName from a CSV line"""
    try:
        # Use csv.reader to properly parse the CSV line
        csv_reader = csv.reader([line])
        row = next(csv_reader)
        
        if objectname_column_index is not None and objectname_column_index < len(row):
            return row[objectname_column_index]
        return "N/A"
    except Exception:
        return "Parse Error"

def find_objectname_column(header_line):
    """Find the column index for ObjectName in the header"""
    try:
        csv_reader = csv.reader([header_line])
        headers = next(csv_reader)
        
        # Look for ObjectName column (case insensitive)
        for i, header in enumerate(headers):
            if header.lower().strip() == 'objectname':
                return i
        return None
    except Exception:
        return None

def _collect_issues(lines, objectname_column_index):
    """Collect issues and compute total suspicious characters before printing."""
    issues = []  # list of tuples: (line_num, object_name, highlighted_line, suspicious_chars)
    total_special = 0
    for line_num, line in enumerate(lines, 1):
        line = line.rstrip('\n\r')  # Remove line endings
        suspicious_chars = find_non_utf8_chars(line)
        if suspicious_chars:
            object_name = get_object_name_from_line(line, objectname_column_index)
            highlighted_line = highlight_suspicious_chars(line, suspicious_chars)
            issues.append((line_num, object_name, highlighted_line, suspicious_chars))
            total_special += len(suspicious_chars)
    return issues, total_special

def _print_report_header(filename, total_special):
    out(f"Analyze UTF-8 Report - Version {VERSION}")
    out("=" * 50)
    out(f"Analyzing file: {filename}")
    out(f"Total 'special characters' found: {total_special}")
    out()

def _print_report_footer(filename, total_special):
    out()
    out("=" * 50)
    out("SUMMARY")
    out("=" * 50)
    out(f"Analyze UTF-8 Report - Version {VERSION}")
    out(f"Analyzing file: {filename}")
    out(f"Total 'special characters' found: {total_special}")
    out("=" * 50)

def analyze_csv_file(filename):
    """Analyze CSV file for encoding issues"""
    issues_found = False
    objectname_column_index = None
    
    try:
        # Try to read as UTF-8 first
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()
        
        # Find ObjectName column from header (first line)
        if lines:
            header_line = lines[0].rstrip('\n\r')
            objectname_column_index = find_objectname_column(header_line)
        
        # Collect issues and totals before printing header
        issues, total_special = _collect_issues(lines, objectname_column_index)
        _print_report_header(filename, total_special)
        out(f"Successfully read {len(lines)} lines as UTF-8")
        if objectname_column_index is not None:
            out(f"Found ObjectName column at index {objectname_column_index}")
        else:
            out("ObjectName column not found - will show 'N/A' for ObjectName")
        out()
        
        if issues:
            issues_found = True
            for line_num, object_name, highlighted_line, suspicious_chars in issues:
                out(f"Line {line_num}: Found {len(suspicious_chars)} suspicious character(s)")
                out(f"ObjectName: {object_name}")
                out(f"Content: {highlighted_line}")
                out("Suspicious characters:")
                for pos, char, code in suspicious_chars:
                    description = get_character_description(char)
                    out(f"  Position {pos}: '{char}' (Unicode: U+{code:04X}, Decimal: {code}) - {description}")
                out("-" * 40)
        else:
            out("[OK] No suspicious encoding issues found!")
        
        # Print summary footer
        _print_report_footer(filename, total_special)
    
    except UnicodeDecodeError as e:
        out(f"[ERROR] UTF-8 decoding error: {e}")
        out("Attempting to read with different encodings...")
        
        # Try common encodings
        encodings_to_try = ['latin1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                with open(filename, 'r', encoding=encoding, errors='replace') as file:
                    lines = file.readlines()
                
                # Find ObjectName column from header (first line)
                if lines:
                    header_line = lines[0].rstrip('\n\r')
                    objectname_column_index = find_objectname_column(header_line)
                
                # Collect issues and totals before printing header
                issues, total_special = _collect_issues(lines, objectname_column_index)
                _print_report_header(filename, total_special)
                out(f"[OK] Successfully read with {encoding} encoding")
                if objectname_column_index is not None:
                    out(f"Found ObjectName column at index {objectname_column_index}")
                else:
                    out("ObjectName column not found - will show 'N/A' for ObjectName")
                out()
                
                if issues:
                    issues_found = True
                    for line_num, object_name, highlighted_line, suspicious_chars in issues:
                        out(f"Line {line_num}: Found {len(suspicious_chars)} suspicious character(s)")
                        out(f"ObjectName: {object_name}")
                        out(f"Content: {highlighted_line}")
                        out("Suspicious characters:")
                        for pos, char, code in suspicious_chars:
                            description = get_character_description(char)
                            out(f"  Position {pos}: '{char}' (Unicode: U+{code:04X}, Decimal: {code}) - {description}")
                        out("-" * 40)
                else:
                    out("[OK] No suspicious encoding issues found!")
                
                # Print summary footer
                _print_report_footer(filename, total_special)
                break
            except Exception as e:
                out(f"[ERROR] Failed with {encoding}: {e}")
                continue
    
    except FileNotFoundError:
        out(f"[ERROR] File not found: {filename}")
    except Exception as e:
        out(f"[ERROR] Error reading file: {e}")

    # Write the report to a timestamped file next to the input CSV
    try:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = os.path.dirname(os.path.abspath(filename)) or "."
        report_path = os.path.join(base_dir, f"REPORT_UTF8-{ts}.txt")
        with open(report_path, "w", encoding="utf-8") as fp:
            fp.write("\n".join(_report_lines) + "\n")
        out(f"Report saved to: {report_path}")
    except Exception as e:
        out(f"[ERROR] Failed to write report file: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "export.csv"
    
    analyze_csv_file(filename)

if __name__ == "__main__":
    main()
