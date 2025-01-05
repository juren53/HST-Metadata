#!/user/bin/python3
#
#

import pandas as pd

csv_file = "test.csv"
print("Using ", csv_file)

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
audio_files = [f for f in all_files if isinstance(f, str) and (f.lower().endswith('.mp3') or f.lower().endswith('.wav'))]

# Remove duplicates and sort
unique_audio_files = sorted(set(audio_files))

# Print the results
print("Found", len(unique_audio_files), "unique audio files ") 
for file in unique_audio_files:
    print(file)
