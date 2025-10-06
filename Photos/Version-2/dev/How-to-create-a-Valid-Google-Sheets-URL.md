# How to Create a Valid Google Sheets URL for Anonymous Access

## Overview

This guide explains how to create valid Google Sheets URLs that work with the `google-to-csv.py` program, which produces `export.csv` files for the HSTL Photo-tagging System.

## URL Formats

### Standard Google Sheets URL Format
```
https://docs.google.com/spreadsheets/d/{spreadsheetId}/edit#gid={sheetId}
```

### Anonymous Access URL Format (CSV Export)
```
https://docs.google.com/spreadsheets/d/{spreadsheetId}/export?format=csv&gid={sheetId}
```

### Shareable URL Format (For Browser Viewing)
```
https://docs.google.com/spreadsheets/d/{spreadsheetId}/edit?usp=sharing
```

> **Note**: If you don't include the `gid` parameter, it will default to the first sheet.

## Example: Converting a Standard URL to Anonymous Access URL

### Original URL
```
https://docs.google.com/spreadsheets/d/1S6sdJRmG8uEPxYAFDtg1rLpbGaML6j5ZilEJG_HWrUs/edit#gid=0
```

### URL for Anonymous Access (CSV Export)
```
https://docs.google.com/spreadsheets/d/1S6sdJRmG8uEPxYAFDtg1rLpbGaML6j5ZilEJG_HWrUs/export?format=csv&gid=0
```

## Troubleshooting

### Example of Invalid URL
If you receive a URL like this (from an email or elsewhere):
```
https://docs.google.com/spreadsheets/d/1th1xgbZcboeWd4HxMqjN6eLSoW8IDpZ0/edit?gid=1418369420#gid=1418369420
```

You might encounter errors like:
```
Using spreadsheet ID: 1th1xgbZcboeWd4HxMqjN6eLSoW8IDpZ0
Fetching data from Google Sheet...
HTTP Error: <HttpError 400 when requesting https://sheets.googleapis.com/v4/spreadsheets/1th1xgbZcboeWd4HxMqjN6eLSoW8IDpZ0?alt=json returned "This operation is not supported for this document">
```

### Solution
Create a proper Google Sheet by:
1. Opening the document
2. Using "Save as Google Sheet" from the File menu
3. Using the new URL provided after saving

### Example of Valid URL (After "Save as Google Sheet")
```
https://docs.google.com/spreadsheets/d/1sJLOViobf9Q4h261VjupvQplwGcl6N9ZkLBACG618/edit?gid=1418369420
```

### Successful Result
When using a valid URL, you should see:
```
Exporting to 'export.csv' with UTF-8 encoding...
Conversion completed successfully. Output saved to 'export.csv'
Rows processed: {xxx}
```
