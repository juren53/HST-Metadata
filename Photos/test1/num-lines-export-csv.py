import csv

with open("export.csv", "r") as file:
    reader = csv.reader(file)
    num_lines = sum(1 for row in reader)
    print(f"Number of lines in the file: {num_lines}")
