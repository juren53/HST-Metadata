#!/usr/bin/python3
#-----------------------------------------------------------
# ############   audio-csv-analysis.py ver c  ################
#
# This Python code reads a CSV file containing HSTL audio records,
# identifies columns related to MP3 files, and extracts the filenames
# from their URLs and then saves the modified data, with only the
# filenames in the MP3 columns, to a new CSV file called 'output.csv'.
#
# created on Sun 01 Dec 2024 08:14:37 PM CST 
#-----------------------------------------------------------
import pandas as pd

# Read the CSV file
df = pd.read_csv('audio-records.csv')

# Print column names
print("Column names:")
print(df.columns.tolist())

# Identify MP3 columns dynamically
mp3_columns = [col for col in df.columns if col.startswith('Sound Recording')]

# Print MP3 columns
print("\nMP3 Columns:")
print(mp3_columns)

# Function to extract filename from URL
def extract_filename(url):
    if pd.isna(url):
        return url
    # Split the URL and take the last part (filename)
    return url.split('/')[-1]

# Process MP3 columns to extract only filenames
for col in mp3_columns:
    df[col] = df[col].apply(extract_filename)

# Save all columns to output.csv
df.to_csv('output.csv', index=False)

# Print some information about the output
print("\nTotal records in output:", len(df))
print("\nFirst few rows of MP3 filenames:")
for col in mp3_columns:
    print(f"\n{col}:")
    print(df[col].head())
