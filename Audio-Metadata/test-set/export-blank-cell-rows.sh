#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <input_csv_file> <output_csv_file> <column_number>"
    echo "Example: $0 input.csv blank_rows.csv 3  # Exports rows with blank cells in the 3rd column"
    exit 1
fi

# Assign arguments to variables
INPUT_CSV="$1"
OUTPUT_CSV="$2"
COLUMN_NUMBER="$3"

# Write rows with blank cells to a new CSV file
# Includes the header row and rows with blank cells in the specified column
awk -F, -v col="$COLUMN_NUMBER" -v output_file="$OUTPUT_CSV" '
    NR == 1 {
        # Always write the header to the output file
        print $0 > output_file
    }
    NR > 1 {
        gsub(/^[ \t]+|[ \t]+$/, "", $col)  # Trim whitespace
        if ($col == "") {
            print $0 > output_file
            blank_count++
        }
    }
    END { 
        print "\nTotal blank cells found: " blank_count 
    }
' "$INPUT_CSV"

# Confirm the export
echo "Rows with blank cells have been exported to $OUTPUT_CSV"

# Optional: Display the contents of the output file
echo "\nContents of $OUTPUT_CSV:"
cat "$OUTPUT_CSV"
