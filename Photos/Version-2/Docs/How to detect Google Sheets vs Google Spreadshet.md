## How to detect a Google Sheet vs a Google Spreadsheet

You can determine whether a Google Sheets URL points to a native Google Sheet or an uploaded Excel file by using the Google Drive API. The key is to check the file’s mimeType. Native Google Sheets use the mimeType application/vnd.google-apps.spreadsheet, while uploaded Excel files retain their original format—for example, .xlsx files have the mimeType application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, even when viewed in Google Sheets.

Here's a Python function that uses the Google Drive API to achieve this.

**Prerequisites:**

Before you can run this code, you'll need:

1.  **Google API Client Library for Python:** `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`
2.  **Google Cloud Project and API Credentials:**
      * Go to the [Google Cloud Console](https://console.cloud.google.com/).
      * Create a new project or select an existing one.
      * Enable the **Google Drive API** for your project.
      * Create **OAuth 2.0 Client IDs** credentials (desktop app type is usually easiest for local scripts). Download the `credentials.json` file and place it in the same directory as your Python script.

**Python Code:**

```python
import os
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def authenticate_google_drive():
    """Authenticates with Google Drive API and returns a service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred during authentication: {error}")
        return None

def extract_file_id_from_url(url):
    """
    Extracts the Google Drive file ID from a Google Sheets URL.
    Returns None if no ID is found.
    """
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None

def detect_google_sheet_type(sheet_url, drive_service):
    """
    Detects and reports the type of Google Sheet URL.

    Args:
        sheet_url (str): The URL of the Google Sheet.
        drive_service: An authenticated Google Drive API service object.

    Returns:
        str: A description of the sheet type (e.g., "Native Google Sheet",
             "Excel File (.xlsx) viewed in Google Sheets", "Unknown File Type",
             "Invalid URL or File Not Found").
    """
    if not drive_service:
        return "Authentication Failed."

    file_id = extract_file_id_from_url(sheet_url)
    if not file_id:
        return "Invalid Google Sheets URL format (could not extract file ID)."

    try:
        # Retrieve file metadata, specifically the mimeType
        file_metadata = drive_service.files().get(fileId=file_id, fields='mimeType,name').execute()
        mime_type = file_metadata.get('mimeType')
        file_name = file_metadata.get('name', 'Unknown File')

        if mime_type == "application/vnd.google-apps.spreadsheet":
            return f"Native Google Sheet: '{file_name}'"
        elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return f"Excel File (.xlsx) viewed in Google Sheets: '{file_name}'"
        elif mime_type == "application/vnd.ms-excel":
            return f"Excel File (.xls) viewed in Google Sheets: '{file_name}'"
        else:
            return f"Unknown File Type (MIME: {mime_type}): '{file_name}'"
    except HttpError as error:
        if error.resp.status == 404:
            return "File Not Found or You Do Not Have Permission to Access It."
        else:
            return f"An API error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Example Usage ---
if __name__ == "__main__":
    # Authenticate once
    drive_service = authenticate_google_drive()

    if drive_service:
        # Your example URLs
        url1 = "https://docs.google.com/spreadsheets/d/1mgxguKnNThYH8PspEge6xS2xxPwdU2Qv/edit?gid=1418369420#gid=1418369420"
        url2 = "https://docs.google.com/spreadsheets/d/14uNYVk68fFuoQM2exIRTsifkL7brn4pTzqt6DC3M9uk/edit?gid=1418369420#gid=1418369420"
        url_non_existent = "https://docs.google.com/spreadsheets/d/1234567890abcdefghijklmnopqrstuvwxyz/edit"
        url_invalid_format = "https://example.com/spreadsheet"

        print(f"Analyzing URL 1: {url1}")
        print(f"Result: {detect_google_sheet_type(url1, drive_service)}\n")

        print(f"Analyzing URL 2: {url2}")
        print(f"Result: {detect_google_sheet_type(url2, drive_service)}\n")

        print(f"Analyzing URL (Non-existent/Private): {url_non_existent}")
        print(f"Result: {detect_google_sheet_type(url_non_existent, drive_service)}\n")

        print(f"Analyzing URL (Invalid format): {url_invalid_format}")
        print(f"Result: {detect_google_sheet_type(url_invalid_format, drive_service)}\n")
    else:
        print("Failed to authenticate Google Drive service. Cannot proceed.")

```

### How the Code Works:

1.  **`authenticate_google_drive()`:**

      * This function handles the OAuth2.0 authentication process.
      * It checks for an existing `token.json` file (which stores your credentials after the first successful authentication). If not found or expired, it will open a browser window for you to log in to your Google account and grant permissions.
      * It then builds and returns a `drive` service object, which is used to make API calls.

2.  **`extract_file_id_from_url(url)`:**

      * Google Sheets URLs contain a unique file ID (e.g., `1mgxguKnNThYH8PspEge6xS2xxPwdU2Qv`). This helper function uses a regular expression to extract this ID from the URL.

3.  **`detect_google_sheet_type(sheet_url, drive_service)`:**

      * Takes the `sheet_url` and the authenticated `drive_service` as input.
      * Extracts the `file_id`.
      * Makes a `drive_service.files().get()` API call to retrieve metadata about the file, specifically requesting the `mimeType` field.
      * Compares the retrieved `mimeType` to known Google Sheets and Excel MIME types:
          * `application/vnd.google-apps.spreadsheet`: This is the `mimeType` for a true, native Google Sheet.
          * `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`: This is the `mimeType` for an `.xlsx` (Excel) file.
          * `application/vnd.ms-excel`: This is for older `.xls` Excel files.
      * Returns a descriptive string based on the `mimeType`.
      * Includes error handling for cases like invalid URLs, files not found (e.g., due to wrong ID or permission issues), or other API errors.

### To Use It:

1.  Save the code as a `.py` file (e.g., `sheet_detector.py`).
2.  Make sure you have your `credentials.json` file in the same directory.
3.  Run the script: `python sheet_detector.py`
4.  The first time you run it, a browser window will open for you to authorize access. After that, `token.json` will be created, and subsequent runs will be faster.

This function will give you a clear indication of the underlying file format, which directly explains why your Python code behaves differently when processing the two types of URLs.
