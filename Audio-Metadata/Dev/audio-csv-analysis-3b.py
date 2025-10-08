import pandas as pd

# Read the CSV file
df = pd.read_csv('audio.csv')

# Columns for MP3 file links (Sound Recording columns)
mp3_columns = [f'Sound Recording_{i}' for i in range(1, 11)]
mp3_columns.insert(0, 'Sound Recording')

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
print("Columns in output CSV:")
print(df.columns.tolist())
print(f"\nTotal records in output: {len(df)}")
print("\nFirst few rows of MP3 filenames:")
for col in mp3_columns:
    print(f"\n{col}:")
    print(df[col].head())
