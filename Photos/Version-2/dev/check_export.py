#!/usr/bin/env python3

import pandas as pd
import sys

# Load the CSV file
df = pd.read_csv('export.csv')

# Display columns
print("Columns in export.csv:")
print(df.columns)

# Look for 'Source' column
if 'Source' in df.columns:
    print("\nExamining Source column:")
    for i in range(min(20, len(df))):
        value = df.loc[i, 'Source'] if pd.notna(df.loc[i, 'Source']) else '[empty]'
        print(f"Row {i}: {value}")
else:
    print("\nSource column not found in export.csv")

# Check for any columns containing 'Related Collection' in their values
print("\nSearching for 'Related Collection' in any cell:")
found = False
for col in df.columns:
    for i in range(min(20, len(df))):
        if i < len(df) and pd.notna(df.loc[i, col]):
            value = str(df.loc[i, col])
            if 'related collection' in value.lower():
                found = True
                print(f"Found in row {i}, column '{col}': {value}")

if not found:
    print("No cells containing 'Related Collection' found in the first 20 rows.")

# Look for 'Sample Related Collection Papers' in any cell
print("\nSearching for 'Sample Related Collection Papers' in any cell:")
found = False
for col in df.columns:
    for i in range(min(50, len(df))):
        if i < len(df) and pd.notna(df.loc[i, col]):
            value = str(df.loc[i, col])
            if 'sample related collection papers' in value.lower():
                found = True
                print(f"Found in row {i}, column '{col}': {value}")

if not found:
    print("No cells containing 'Sample Related Collection Papers' found in the first 50 rows.")

