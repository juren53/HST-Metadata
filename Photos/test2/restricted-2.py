import csv
from PIL import Image

csv_file = "sample-tiffs.csv"  # Path to the CSV file
copyright_image = "watermark.png"  # Path to the copyright transparency image

restricted_files = []

with open(csv_file, newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        filename = row["ObjectName"] + ".tif"
        if row["CopyrightNotice"] == "Restricted":
            try:
                image = Image.open(filename)
                copyright = Image.open(copyright_image).convert("RGBA")
                image.paste(copyright, (0, 0), mask=copyright.split()[3])
                image.save(filename)
                restricted_files.append(filename)
            except FileNotFoundError:
                print(f"File not found: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

print("Restricted files processed:")
for file in restricted_files:
    print(file)

