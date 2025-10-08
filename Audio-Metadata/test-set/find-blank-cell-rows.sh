#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <csv_file> <column_number>"
    echo "Example: $0 data.csv 3  # Finds rows with blank cells in the 3rd column"
    exit 1
fi

# Assign arguments to variables
CSV_FILE="$1"
COLUMN_NUMBER="$2"

# Find and list rows with blank cells in the specified column
echo "Rows with blank cells in column $COLUMN_NUMBER:"
awk -F, -v col="$COLUMN_NUMBER" '
    NR == 1 { header = $0; next }  # Store header row
    {
        gsub(/^[ \t]+|[ \t]+$/, "", $col)  # Trim whitespace
        if ($col == "") {
            print "Line " NR ": " $0
            blank_count++
        }
    }
    END { 
        print "\nTotal blank cells found: " blank_count 
        print "Header: " header
    }
' "$CSV_FILE"
