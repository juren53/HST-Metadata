import csv
import sys


# Get the file name from the command line
input_file = sys.argv[1]


def print_formatted_row(row):
    max_key_length = max(len(key) for key in row.keys())
    for key, value in row.items():
        print(f"{key.ljust(max_key_length)} {value}")

with open('OriginalTIFs.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Title'] == input_file:
            print_formatted_row(row)
            break

