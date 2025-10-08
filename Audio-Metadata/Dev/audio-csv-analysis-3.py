import pandas as pd
import os

# Read the CSV file
df = pd.read_csv('audio-records.csv')

# Columns to extract
columns_to_extract = df.columns[:18]

# Function to extract file name from URL
def extract_filename(url):
    if pd.isna(url):
        return url
    return os.path.basename(url)

# Process Sound Recording columns (8-18)
mp3_columns = [col for col in df.columns if 'Sound Recording' in col][1:]

# Extract just the filenames
for col in mp3_columns:
    df[col] = df[col].apply(extract_filename)

# Select and output specified columns
output_df = df[columns_to_extract]

# Save to CSV
output_df.to_csv('output.csv', index=False)

# Print some information about the output
print("Columns in output CSV:")
print(output_df.columns.tolist())
print(f"\nTotal records in output: {len(output_df)}")
print("\nFirst few rows of MP3 file names:")
for col in mp3_columns:
    print(f"\n{col}:")
    print(output_df[col].head())
