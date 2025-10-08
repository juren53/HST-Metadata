#!/usr/bin/env python3
import re

# Test the URL extraction on a problematic URL
def test_extraction():
    url = "https://docs.google.com/spreadsheets/d/1zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I/edit?gid=1418369420#gid=1418369420"
    
    # Extract the file ID
    file_id = extract_file_id_from_url(url)
    print(f"Extracted file ID: {file_id}")
    
    # Check proper file ID
    correct_id = "1zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I"
    print(f"Matches expected ID: {file_id == correct_id}")

def extract_file_id_from_url(url_or_id):
    """Extract a file ID from a Google Drive URL or return the ID if already an ID."""
    # If it's likely already an ID (not a URL), return it
    if not any(x in url_or_id for x in ['http', 'drive.google', 'docs.google']):
        return url_or_id
        
    # Handle Google Drive links of various formats
    drive_link_patterns = [
        # Standard Drive file link
        r'https://drive.google.com/file/d/([a-zA-Z0-9_-]+)',
        # Open links
        r'https://drive.google.com/open\?id=([a-zA-Z0-9_-]+)',
        # Docs, Sheets, Slides
        r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'https://docs.google.com/document/d/([a-zA-Z0-9_-]+)',
        r'https://docs.google.com/presentation/d/([a-zA-Z0-9_-]+)',
        # Forms and other types
        r'https://docs.google.com/forms/d/([a-zA-Z0-9_-]+)'
    ]
    
    # Check if the input matches any of the URL patterns
    for pattern in drive_link_patterns:
        match = re.search(pattern, url_or_id)
        if match:
            # Clean up ID (remove trailing slashes or other characters)
            file_id = match.group(1)
            file_id = file_id.split('/')[0]  # Remove anything after a slash
            file_id = file_id.split('?')[0]  # Remove query parameters
            file_id = file_id.split('#')[0]  # Remove fragments
            return file_id
    
    # If we get here, we couldn't extract an ID using the patterns
    print(f"Warning: Could not extract a file ID from: {url_or_id}")
    print("Proceeding with the full string as the ID, but this might not work.")
    return url_or_id

if __name__ == "__main__":
    test_extraction()
