import os
import pickle
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- CONFIGURATION ---
# The ID of the spreadsheet to read columns from.
SPREADSHEET_ID = '1pPbY2m9cZA3pXSYyvPnrFQqtaceMVufZrvuVXSq2ZKs'
# The title for the new Google Form.
FORM_TITLE = 'HPM_form'
# The name of the file containing your Google Cloud client secrets.
CLIENT_SECRETS_FILE = '../client_secret.json'
# The scopes required for the script to access Sheets and Forms.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/forms.body'
]
# The file to store your authentication token once created.
TOKEN_PICKLE_FILE = 'token_form_generator.pickle'

def get_credentials():
    """
    Handles user authentication by loading existing credentials or
    initiating an OAuth 2.0 flow for the user to grant permissions.
    """
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Could not find '{os.path.basename(CLIENT_SECRETS_FILE)}'. Please download your OAuth 2.0 "
                    "Client credentials from the Google Cloud Console and place the "
                    "file in the project root directory (one level above this script)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

def main():
    """
    Main function to authenticate, read a Google Sheet, and create a Google Form.
    """
    try:
        # --- 1. Authenticate and Get Credentials ---
        print("Authenticating with Google...")
        creds = get_credentials()
        print("Authentication successful.")

        # --- 2. Read Google Sheet Headers ---
        print(f"Accessing spreadsheet (ID: {SPREADSHEET_ID}) to get column headers...")
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.sheet1  # Assumes the first sheet
        headers = worksheet.row_values(1)
        if not headers:
            print("No headers found in the first row of the sheet. Exiting.")
            return
        print(f"Found headers: {headers}")

        # --- 3. Create the Google Form ---
        print(f"Creating new Google Form titled '{FORM_TITLE}'...")
        forms_service = build('forms', 'v1', credentials=creds)
        new_form = {
            "info": {
                "title": FORM_TITLE,
                "documentTitle": FORM_TITLE
            }
        }
        created_form = forms_service.forms().create(body=new_form).execute()
        form_id = created_form['formId']
        form_url = created_form['responderUri']
        print(f"Successfully created form. You can view it here: {form_url}")

        # --- 4. Add Questions to the Form ---
        print("Adding questions to the form based on sheet headers...")
        # Create a batch update request to add all questions at once.
        # Questions are added in reverse order of the list to appear in the correct order on the form.
        update_requests = {
            "requests": [
                {
                    "createItem": {
                        "item": {
                            "title": header,
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {
                                        "paragraph": False  # False for short answer
                                    }
                                }
                            }
                        },
                        "location": {"index": 0} # Add new items at the beginning
                    }
                }
                for header in reversed(headers)
            ]
        }
        forms_service.forms().batchUpdate(formId=form_id, body=update_requests).execute()
        print("Successfully added all questions to the form.")

        # --- 5. Final Instructions ---
        print("\n--- Important Notes ---")
        print(f"Your new form is available at: {form_url}")
        print("By default, form responses will be collected in a *new* spreadsheet, not your original one.")
        print("To change this, open the form, go to the 'Responses' tab, click the three dots, and select 'Select response destination'.")
        print("Script finished.")

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
