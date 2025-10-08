import os
import sys
import json
import pickle
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# === CONFIG ===
CLIENT_SECRET_FILE = 'client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token_docs.pickle'  # Using a different pickle file to avoid scope issues
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# Function to extract document ID from URL or validate ID format
def get_valid_document_id():
    """
    Prompts user for document ID or URL and validates it.
    Returns a valid document ID or None if cancelled.
    """
    print("\n=== Google Docs Access ===")
    print("Please enter the Google Document URL or ID")
    print("Example URL: https://docs.google.com/document/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890/edit")
    print("Example ID: 1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890")
    print("Enter 'q' to quit")
    
    while True:
        user_input = input("\nDocument URL or ID: ").strip()
        
        if user_input.lower() == 'q':
            return None
            
        # Check if input is a URL (handles both document and spreadsheet URLs)
        doc_match = re.search(r'https://docs.google.com/document/d/([a-zA-Z0-9_-]+)', user_input)
        sheet_match = re.search(r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9_-]+)', user_input)
        
        if doc_match:
            doc_id = doc_match.group(1)
        elif sheet_match:
            doc_id = sheet_match.group(1)
            print("Note: This appears to be a spreadsheet URL, but we'll try to access it as a document.")
        else:
            doc_id = user_input
        
        # Basic validation - Google Doc IDs are typically longer
        if len(doc_id) < 25:
            print(f"Warning: '{doc_id}' seems too short for a Google Doc ID (typically ~44 chars)")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                continue
                
        print(f"Using document ID: {doc_id}")
        return doc_id

def validate_document(service, document_id):
    """
    Validates if a document ID is accessible and is a Google Doc.
    
    Args:
        service: Google Docs API service instance
        document_id: ID of the document to validate
        
    Returns:
        tuple: (is_valid, document_info) where is_valid is a boolean and document_info contains details or error message
    """
    try:
        # Request basic document metadata
        document = service.documents().get(documentId=document_id).execute()
        
        title = document.get('title', 'Untitled Document')
        
        return True, {
            'title': title,
            'document': document
        }
    
    except HttpError as error:
        if 'not found' in str(error).lower():
            return False, f"Document not found. Please verify the ID and your access permissions."
        elif 'permission' in str(error).lower():
            return False, f"Permission denied. Make sure you have access to this document."
        else:
            return False, f"Error validating document: {error}"
    
    except Exception as error:
        return False, f"Unexpected error validating document: {error}"

def get_credentials():
    """Get valid user credentials from storage or run the OAuth flow.
    
    Returns:
        Credentials, the obtained credentials.
    """
    credentials = None
    
    # Try to load credentials from the token pickle file
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            try:
                credentials = pickle.load(token)
                print("Loaded credentials from token file")
            except Exception as e:
                print(f"Error loading token file: {e}")
    
    # If no valid credentials available, run the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                print("Refreshed expired credentials")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                credentials = None
        
        # If still no valid credentials, run the flow
        if not credentials:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES)
                
                print("Please authenticate using your browser...")
                credentials = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open(TOKEN_PICKLE_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
                print("Saved new credentials to token file")
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                raise
    
    return credentials

def extract_text_from_document(document):
    """
    Extracts text content from a Google Doc document structure.
    
    Args:
        document: The document object returned by the Google Docs API
        
    Returns:
        string: The document's text content
    """
    text_content = []
    
    # Process all document elements
    if 'body' in document and 'content' in document['body']:
        elements = document['body']['content']
        
        for element in elements:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                paragraph_text = []
                
                if 'elements' in paragraph:
                    for para_element in paragraph['elements']:
                        if 'textRun' in para_element:
                            if 'content' in para_element['textRun']:
                                paragraph_text.append(para_element['textRun']['content'])
                
                text_content.append(''.join(paragraph_text))
            
            # Handle tables, lists, and other content types if needed
    
    return '\n'.join(text_content)

def main():
    try:
        # === AUTH ===
        credentials = get_credentials()
        if not credentials:
            print("Authentication failed. Unable to proceed.")
            sys.exit(1)
        
        # === API CLIENT ===
        service = build('docs', 'v1', credentials=credentials)
        
        # === GET VALID DOCUMENT ID ===
        document_id = get_valid_document_id()
        if not document_id:
            print("Operation cancelled by user.")
            sys.exit(0)
        
        # === VALIDATE DOCUMENT ===
        print("\nValidating document access...")
        is_valid, result = validate_document(service, document_id)
        
        if not is_valid:
            print(f"Error: {result}")
            print("\nTroubleshooting tips:")
            print("1. Check if the document ID is correct")
            print("2. Make sure your Google account has access to this document")
            print("3. Verify that this is actually a Google Doc")
            print("4. Try opening the document in your browser: " +
                  f"https://docs.google.com/document/d/{document_id}")
            sys.exit(1)
        
        # Access the validated document info
        document_info = result
        document = document_info['document']
        title = document_info['title']
        
        print(f"\nSuccessfully accessed document: '{title}'")
        
        # Extract and display document content
        print("\nExtracting document content...")
        document_text = extract_text_from_document(document)
        
        # Display document details
        print("\n" + "="*40)
        print(f"DOCUMENT TITLE: {title}")
        print("="*40)
        
        # Display content with some formatting
        if document_text:
            print("\nDOCUMENT CONTENT:")
            print("-"*40)
            print(document_text)
            print("-"*40)
        else:
            print("\nNo text content found in the document.")
        
        # Output document metadata
        print("\nDOCUMENT INFO:")
        print(f"- Document ID: {document_id}")
        print(f"- URL: https://docs.google.com/document/d/{document_id}")
        
        # Additional metadata if available
        if 'documentId' in document:
            print(f"- Internal Document ID: {document['documentId']}")
        if 'revisionId' in document:
            print(f"- Revision ID: {document['revisionId']}")
            
    except HttpError as error:
        status_code = getattr(error, 'status', 'unknown')
        reason = getattr(error, 'reason', str(error))
        
        print(f"API Error (status {status_code}): {reason}")
        if "not found" in str(error).lower():
            print("\nThis error typically means one of the following:")
            print("1. The document ID is incorrect")
            print("2. You don't have permission to access this document")
        
        print("\nTry running the script again with a valid Google Doc ID/URL.")
        
    except Exception as error:
        print(f"An unexpected error occurred: {str(error)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()

