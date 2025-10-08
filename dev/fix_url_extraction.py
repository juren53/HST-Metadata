import re

def test_extraction():
    # The problematic URL
    url = "https://docs.google.com/spreadsheets/d/1zarRJ1t-Gk8Inwfn3FeI_jlivat4ga0I/edit?gid=1418369420#gid=1418369420"
    
    # Current pattern
    current_pattern = r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9_-]+)'
    match = re.search(current_pattern, url)
    print(f"Current pattern result: {match.group(1) if match else 'No match'}")
    
    # New pattern that handles query params and hash fragments
    new_pattern = r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9_-]+)(?:/|$|\?|\#)'
    match = re.search(new_pattern, url)
    print(f"New pattern result: {match.group(1) if match else 'No match'}")

test_extraction()
