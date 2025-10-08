import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('test.csv')
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
csv_files = [f for f in all_files if isinstance(f, str) and (f.lower().endswith('.mp3') or f.lower().endswith('.wav'))]

# Remove duplicates and sort
unique_audio_files = sorted(set(csv_files))

# Print the results
print("Found", len(unique_audio_files), "unique audio files:")
for file in unique_audio_files:
    print(file)

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
print("List of MP3 files in the current directory:")
for file in mp3_files:
    print(file)
