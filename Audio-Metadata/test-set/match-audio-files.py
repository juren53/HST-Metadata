#!python3
##########################   match-audio-files-4.py  ###########
# This Python code identifies and counts matches between MP3 files 
# listed in an HSTL audio CSV file and MP3
# files found in the current directory prior to applying 
# meta-tags to the MP3 files.

# Created Thu 09 Jan 2025 07:35:50 PM CST 
#
################################################################
import pandas as pd

csv_file = 'test.csv'

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file)
#df = pd.read_csv('audio-records.csv')

# Define a function to strip the URL prefix
def strip_url_prefix(url):
    return url.split('/')[-1] if isinstance(url, str) else url

# Apply the function to columns 7 through 16 (which are indices 6 to 15)
for col in df.columns[6:16]:  # Adjusted for zero-based indexing
    df[col] = df[col].apply(strip_url_prefix)

# Get all unique filenames from columns 7-16
all_files = df.iloc[:, 6:16].values.flatten()

# Filter for mp3 and wav files, removing any None/NaN values
csv_files = [f for f in all_files if isinstance(f, str) and (f.lower().endswith('.mp3'))]
#csv_files = [f for f in all_files if isinstance(f, str) and (f.lower().endswith('.mp3') or f.lower().endswith('.wav'))]

# Remove duplicates and sort
unique_audio_files = sorted(set(csv_files))

# Print the results
print("Found", len(unique_audio_files), "MP3 files in the HSTL CSV file: "+csv_file)

# for file in unique_audio_files:
#     print(file)

import os

# Get the current working directory
current_dir = os.getcwd()

# Initialize an empty list to store MP3 files
mp3_files = []

# Iterate through all files in the current directory
for filename in os.listdir(current_dir):
    # Check if the file is an MP3 file
    if filename.endswith(".mp3"):
        mp3_files.append(filename)

# Print the list of MP3 files
# print("List of MP3 files in the current directory:")
# for file in mp3_files:
#     print(file)

################################################

def find_matches(mp3_files, csv_files):
    """
    Find and report matches between mp3_files and csv_files.
    
    Args:
    mp3_files (list): List of MP3 filenames
    csv_files (list): List of CSV filenames
    
    Returns:
    dict: Dictionary containing matched filenames and their counts
    """
    matches = {}
    for mp3_file in mp3_files:
        for csv_file in csv_files:
            if mp3_file == csv_file:
                matches[mp3_file] = matches.get(mp3_file, 0) + 1
    return matches

# Find matches between mp3_files and csv_files
matched_files = find_matches(mp3_files, csv_files)

# Print the results
# print("\nMatched Files:")
# for file, count in matched_files.items():
#    #print(f"{file}: {count} match(s)")
#    print(f"{file}")

# Print total number of matches
total_matches = sum(matched_files.values())
print(f"\nTotal number of matches: {total_matches}")
print(" ")

########################################################

def find_unmatched_files(csv_files, mp3_files):
    """Find and report unmatched filenames between csv_files and mp3_files."""
    unmatched = [file for file in csv_files if file not in mp3_files]
    return unmatched

# Find unmatched files
unmatched_files = find_unmatched_files(csv_files, mp3_files)

# Report unmatched files
if unmatched_files:
    print("\nUmatched Files:")
    for file in unmatched_files:
        print(file)
else:
    print("All files found in the HSTL CSV file are present in the current working directory.")
#    print("All files found in csv_files are also present in mp3_files.")



