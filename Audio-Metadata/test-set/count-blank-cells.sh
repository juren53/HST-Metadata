#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <csv_file> <column_number>"
    echo "Example: $0 data.csv 3  # Counts blank cells in the 3rd column"
    exit 1
fi

# Assign arguments to variables
CSV_FILE="$1"
COLUMN_NUMBER="$2"

# Count blank cells in the specified column
# Uses awk to:
# - Set field separator to comma
# - Check if the specified column is empty or just contains whitespace
# - Count such occurrences
BLANK_COUNT=$(awk -F, -v col="$COLUMN_NUMBER" '
    NR > 1 {  # Skip header row
        gsub(/^[ \t]+|[ \t]+$/, "", $col)  # Trim whitespace
        if ($col == "") count++
    }
    END { print count }
' "$CSV_FILE")

echo "Number of blank cells in column $COLUMN_NUMBER: $BLANK_COUNT"
