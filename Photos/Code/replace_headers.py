#!/usr/bin/python3
#---------------------replace_headers.py v0.02--------------------------
# This code lets the user select from a list of CSV files in the current
# directory and then inserts the HST IPTC headers in the selected file.
# A new file called export.csv is created that can then be used by
# write-tags-from-csv.py to write metadata to TIFF and JPEG HSTL photos.

# The first row of the downloaded CSV [headers] are modified to
# match the HSTL IPTC labels  e.g Headline, Objectname, Credit, By-line, SpecialInstructions,
# Writer-Editor, Source, By-lineTitle, and Caption-Abstract.
# 
# Created Thu 03 Aug 2023 08:09:43 AM CDT by JAU v0.01
# Updated Mon 07 Aug 2023 04:10:01 PM CDT  Added a routine to select the exported CSV file v0.02


import os
import csv

# Clear the screen
os.system('cls' if os.name == 'nt' else 'clear')

# Get the list of CSV files in the working directory
csv_files = [file for file in os.listdir() if file.endswith('.csv')]

# Print the list of CSV files
print("CSV Files in the Working Directory:")
for i, file in enumerate(csv_files):
    print(f"{i + 1}. {file}")

# Ask the user to select a CSV file
selected_file_index = int(input("Select a CSV file (enter the corresponding number): ")) - 1
selected_file = csv_files[selected_file_index]

# Read and print the first three lines of the selected CSV file
with open(selected_file, 'r') as file:
    csv_reader = csv.reader(file)
    print("First three lines of the selected exported CSV file:")
    for _ in range(3):
        line = next(csv_reader, None)
        if line:
            print(line)

#print(selected_file)

# Define the new header row
new_headers = [
    "Headline", "ObjectName", "SpecialInstructions", "CopyrightNotice",
    "Caption-Abstract", "Source", "By-line", "By-lineTitle", "Credit", "Writer-Editor"
]

# Function to replace the headers and write the modified data back to the CSV file
def replace_headers(input_file, output_file, new_headers):
    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile)
        data = list(reader)

    # Update the header row with new_headers
    data[0] = new_headers

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)

# Call the function with the appropriate file paths
replace_headers(selected_file, "export.csv", new_headers)

print(" ")

# Read and print the first three lines of the selected CSV file
with open("export.csv", 'r') as file:
    csv_reader = csv.reader(file)
    print("First three lines of the export.csv file:")
    for _ in range(3):
        line = next(csv_reader, None)
        if line:
            print(line)

