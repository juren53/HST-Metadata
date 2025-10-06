# G2C GUI Features Guide

## Overview
The G2C GUI application provides a user-friendly interface for converting Google Sheets data to CSV format with IPTC metadata mapping. This document outlines all the features and UI elements of the application.

## Top Section (URL Input)
### URL Input Field
- Large text input field for Google Sheets URL
- Placeholder text guides users
- Auto-validates URLs as you type
- Shows green checkmark ✅ when URL is valid

### Auto-detect Button
- Auto-detect from Clipboard" button
- Automatically finds Google Sheets URLs from clipboard
- Shows status message below input field

### Spreadsheet Name Display
- Shows the actual name of the loaded spreadsheet
- Updates when data is loaded
- Format: "📄 Spreadsheet: [Name]"

## Action Buttons
### Load Data Button
- "📊 Load Data" button
- Enabled only when URL is valid
- Initiates data fetching process

### Export Button
- Export to CSV (export.csv)"
- Enabled after data is successfully loaded
- Creates export.csv in the current directory

## Status & Messages Section
- Real-time feedback and status updates
- Uses Consolas font for better readability
- Shows:
  - Operation progress
  - Success/error messages
  - Tips and guidance
  - System status updates

## Right Side Panel
### IPTC Field Mapping Table
```
Google Sheet Field       IPTC Field
==================       ==========
Title                    Headline
Accession Number         ObjectName
Restrictions             CopyrightNotice
Scopenote                Caption-Abstract
Related Collection       Source
Source Photographer      By-line
Institutional Creator    By-lineTitle
```
- Shows field mappings in clear columnar format
- Uses monospace font for alignment

### Additional Meta-tags
```
Additional 'generated' meta-tags:

- Date Created     Compiled from
                  yyyy-mm-dd in spreadsheet

- Credit           Hard coded
```

## 👁️ Data Preview Section
- Full-width table showing loaded data
- Column headers show both:
  - Excel-style labels (A, B, C...)
  - Original column names
- Shows up to 100 rows
- All columns visible with horizontal scroll
- Alternating row colors for readability
- Same font (Consolas) as Status Messages

## 📊 Status Bar (Bottom)
- Left side: General application status
- Right side:
  - Version number (Ver 0.3)
  - Current local time (updates every second)
- Uses smaller, gray text for non-intrusiveness

## ⌨️ Keyboard Shortcuts
- Ctrl+Q: Exit application

## 🎨 Visual Features
- Maximized window by default
- Custom application icon
- Consistent fonts throughout:
  - Consolas for data and status
  - Standard system font for buttons
- Progress bar appears during operations
- Error messages shown in pop-up dialogs

## 🔄 Dynamic Updates
- Real-time URL validation
- Auto-detection of clipboard content
- Live timestamp updates
- Progress indicators during operations
- Auto-scroll for status messages

## Data Processing Features
1. **URL Handling**
   - Supports full Google Sheets URLs
   - Accepts direct spreadsheet IDs
   - Validates input format automatically

2. **Data Loading**
   - Fetches data directly from Google Sheets
   - Handles authentication automatically
   - Shows progress during loading
   - Detects and warns about Excel files

3. **CSV Export**
   - Maps fields according to IPTC standards
   - Generates properly formatted CSV
   - Includes all mapped fields
   - Adds generated meta-tags

## Error Handling
- Clear error messages in status window
- Pop-up dialogs for critical errors
- User-friendly guidance for common issues
- Excel file detection and warnings
- Authentication error handling

## Requirements
- Python 3.x
- PyQt5
- Google Sheets API access
- Internet connection for Google Sheets access
- Windows 11 (tested platform)
