# Google Sheets to Pandas DataFrame Loader

This script allows you to load data from a Google Spreadsheet directly into a pandas DataFrame. It provides multiple methods to access spreadsheet data, handles authentication with Google's APIs, and includes fallback mechanisms for different types of spreadsheets.

## Overview

The `load_sheet_to_pandas.py` script is designed to:

- Connect to Google Sheets using OAuth authentication
- Read data from any accessible Google Spreadsheet
- Convert the data into a pandas DataFrame
- Provide robust error handling and fallback methods if standard access fails
- Support various Google Sheets URL formats and access patterns

## Requirements

### Python Packages

- pandas
- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- requests

Install the required packages:

```bash
pip install pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

### Google Credentials

The script requires a Google OAuth client secret file to authenticate with Google's APIs:

1. The default client secret file is named `client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json` and should be in the same directory as the script
2. The first time you run the script, it will open a browser window for authentication
3. After authentication, a token file (`token_sheets.pickle`) will be created to store your credentials for future use

## Basic Usage

### Simple Example

To load a Google Spreadsheet into a pandas DataFrame:

```bash
python load_sheet_to_pandas.py --url "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
```

### Test Mode

To verify that authentication and API access are working correctly:

```bash
python load_sheet_to_pandas.py --test
```

### Using a Specific Sheet

To access a specific sheet by name:

```bash
python load_sheet_to_pandas.py --url "YOUR_SPREADSHEET_URL" --sheet "Sheet1"
```

## Command Line Options

| Option | Short Flag | Description |
|--------|------------|-------------|
| `--url` | `-u` | URL of the Google Spreadsheet (default: the URL from the original task) |
| `--sheet` | `-s` | Specific sheet name to access within the spreadsheet |
| `--drive-first` | `-d` | Use Drive API first instead of Sheets API |
| `--open-browser` | `-o` | Attempt to open the spreadsheet URL in a browser |
| `--test` | `-t` | Run in test mode using a known public spreadsheet |
| `--direct` | | Try direct access method for public spreadsheets |
| `--regenerate-token` | `-r` | Force regeneration of the OAuth token |

## Troubleshooting

### Common Issues and Solutions

#### Authentication Issues

- **Error**: "Failed to get credentials" or OAuth-related errors
  - **Solution**: Use the `--regenerate-token` flag to create a new authentication token
  - Ensure you have the correct client secret file in the script directory

#### Access Issues

- **Error**: "File not found" or "Spreadsheet not found"
  - **Solution**: Verify the spreadsheet URL is correct and that your Google account has access to the spreadsheet
  - For private spreadsheets, ensure they are shared with your Google account
  - For public spreadsheets, ensure they are shared with "Anyone with the link"

- **Error**: "This operation is not supported for this document"
  - **Solution**: The URL might be for a different type of Google document (not a spreadsheet)
  - Try opening the URL in a browser to confirm it's a Google Sheet

#### Sheet Access Issues

- **Error**: "Invalid range" or sheet-related errors
  - **Solution**: Use the `--sheet` option to explicitly specify the sheet name
  - If using GID, ensure the GID parameter in the URL is correct

### Verifying Authentication

If you're having persistent issues, run the script with the `--test` flag:

```bash
python load_sheet_to_pandas.py --test
```

This will attempt to authenticate and access a known public spreadsheet. If this succeeds but your target spreadsheet fails, the issue is likely with the specific spreadsheet permissions or format.

## Notes About the Original Task

The script was originally created to access a specific spreadsheet URL:
```
https://docs.google.com/spreadsheets/d/1zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I/edit?gid=1418369420
```

However, testing revealed that this specific spreadsheet:
1. Returns a 404 "File not found" error from the Drive API
2. Returns "This operation is not supported for this document" from the Sheets API
3. Returns a 401 (Unauthorized) status code when accessed directly via HTTP

These errors suggest that either:
- The spreadsheet doesn't exist
- The spreadsheet requires specific permissions that aren't available
- The URL format is non-standard or incorrect
- The spreadsheet might be a different type of Google document

**Important**: While the original spreadsheet couldn't be accessed, the script has been verified to work correctly with public Google Sheets, such as the test sheet at `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`.

To use the script with a different spreadsheet, simply provide the URL with the `--url` parameter:

```bash
python load_sheet_to_pandas.py --url "YOUR_SPREADSHEET_URL"
```

