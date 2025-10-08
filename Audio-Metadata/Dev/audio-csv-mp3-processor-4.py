import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('audio-records.csv')

# Define a function to strip the URL prefix
def strip_url_prefix(url):
    return url.split('/')[-1] if isinstance(url, str) else url

# Apply the function to columns 7 through 16 (which are indices 6 to 15)
for col in df.columns[6:16]:  # Adjusted for zero-based indexing
    df[col] = df[col].apply(strip_url_prefix)

# Count the number of .mp3 files in each row for columns 7 through 16
mp3_counts = df.iloc[:, 6:16].apply(lambda row: row.str.contains('.mp3', na=False).sum(), axis=1)

# Total number of mp3 files across all records
total_mp3_files = mp3_counts.sum()

# Count the occurrences of each count from 1 to 10
mp3_count_distribution = mp3_counts.value_counts().reindex(range(1, 11), fill_value=0)

# Print the results
for count, total in mp3_count_distribution.items():
    print(f"Total number of files with {count} mp3 files: {total}")

# Print the total number of mp3 files counted
print(f"Total number of mp3 files counted: {total_mp3_files}")
print(f"Total number of records in the DataFrame: {len(df)}")

# Additional Diagnostics
# Check how many records have more than 10 mp3 files
more_than_ten = mp3_counts[mp3_counts > 10]
print(f"Total number of records with more than 10 mp3 files: {len(more_than_ten)}")

# Display rows with more than 10 mp3 files, if any
if not more_than_ten.empty:
    print("Records with more than 10 mp3 files:")
    print(df[mp3_counts > 10])
