import pandas as pd

# Read the CSV file
df = pd.read_csv('audio.csv')

# Identify columns that are links to MP3 files
mp3_columns = [col for col in df.columns if 'Sound Recording' in col]

# Function to count non-null MP3 links
def count_mp3_links(row):
    return sum(pd.notna(row[col]) for col in mp3_columns)

# Filter for records with only one MP3 link
single_mp3_records = df[df.apply(count_mp3_links, axis=1) == 1]

# Display the results
print(f"Total records with only one MP3 file: {len(single_mp3_records)}")

# Output to CSV
single_mp3_records.to_csv('single.csv', index=False)

# Optional: Print out details of the records
print("\nRecords with Single MP3 File:")
for index, row in single_mp3_records.iterrows():
    print(f"\nTitle: {row['title']}")
    print(f"Date: {row['Date']}")
    
    # Find and print the single MP3 link
    for col in mp3_columns:
        if pd.notna(row[col]):
            print(f"MP3 Link: {row[col]}")
