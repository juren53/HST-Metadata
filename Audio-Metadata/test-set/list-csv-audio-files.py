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
audio_files = [f for f in all_files if isinstance(f, str) and (f.lower().endswith('.mp3') or f.lower().endswith('.wav'))]

# Remove duplicates and sort
unique_audio_files = sorted(set(audio_files))

# Print the results
print("Found", len(unique_audio_files), "unique audio files:")
for file in unique_audio_files:
    print(file)

#!/usr/bin/python3
###################  list-dir-audio-files.py  #################

import os
import glob

def list_audio_files():
    # Get lists of both mp3 and wav files
    mp3_files = glob.glob('*.mp3')
    wav_files = glob.glob('*.wav')
    
    # Combine the lists
    all_audio_files = mp3_files + wav_files
    
    # Sort alphabetically
    all_audio_files.sort()
    
    # Print results
    if all_audio_files:
        print(f"Found {len(all_audio_files)} audio file(s):")
        print("\nMP3 files:")
        for file in mp3_files:
            print(f"- {file}")
            
        print("\nWAV files:")
        for file in wav_files:
            print(f"- {file}")
    else:
        print("No MP3 or WAV files found in the current directory.")

    # Return the list in case it's needed for further processing
    return all_audio_files

if __name__ == '__main__':
    list_audio_files()


