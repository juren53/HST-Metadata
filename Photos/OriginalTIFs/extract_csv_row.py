import csv
import sys

def extract_row_from_csv(csv_file, title):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Title'] == title:
                return row
    return None

def print_row_vertically(row):
    if row is None:
        print("No matching row found.")
        return
    
    max_key_length = max(len(key) for key in row.keys())
    for key, value in row.items():
        print(f"{key.ljust(max_key_length)} {value}")

# Check if the script is run with the correct command line arguments
if len(sys.argv) != 3:
    print("Usage: python extract_csv_row.py <csv_file> <title>")
    sys.exit(1)

csv_file = sys.argv[1]
title = sys.argv[2]

row = extract_row_from_csv(csv_file, title)
print_row_vertically(row)

