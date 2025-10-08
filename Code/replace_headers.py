import csv

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
replace_headers("export.csv", "updated_export.csv", new_headers)

