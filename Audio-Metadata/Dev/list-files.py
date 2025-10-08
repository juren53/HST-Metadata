import pandas as pd
import numpy as np

# Load the CSV file into a DataFrame
df = pd.read_csv('audio-records.csv')

# Function to strip the URL prefix
def strip_url_prefix(url):
    return url.split('/')[-1] if isinstance(url, str) else url

# Apply the function to columns 7 through 16 (which are indices 6 to 15)
for col in df.columns[6:16]:
    df[col] = df[col].apply(strip_url_prefix)

# Function to check file extension and add to list if mp3 or wav
def add_to_file_list(url):
    if isinstance(url, (str, float)):
        file_extension = str(url).split('.')[-1].lower() if isinstance(url, str) else ''
        if file_extension in ['mp3', 'wav']:
            return True
    return False

# Apply the function to columns 7 through 16 (which are indices 6 to 15)
for col in df.columns[6:16]:
    df[col] = df[col].apply(add_to_file_list)

# Create lists of mp3 and wav files
mp3_files = df[df['url_column'] == True]['url_column'].tolist()
wav_files = df[df['url_column'] == True]['url_column'].tolist()

print("List of MP3 files:", mp3_files)
print("List of WAV files:", wav_files)

