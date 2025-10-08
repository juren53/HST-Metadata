#!/usr/bin/python3


import os
import csv

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
    print("First three lines of the selected CSV file:")
    for _ in range(1):
        line = next(csv_reader, None)
        if line:
            print(line)

