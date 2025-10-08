import csv
import exiftool

def read_metadata_from_csv(csv_file):
    metadata = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            metadata.append(row)
    return metadata

def update_tiff_metadata(tiff_files, metadata):
    with exiftool.ExifTool() as et:
        for tiff_file, tags in zip(tiff_files, metadata):
            et.execute("-overwrite_original", "-TagsFromFile", csv_file, "-XMP:Title=" + tags["Title"], tiff_file)

csv_file = "OriginalTIFs.csv"
tiff_files = ["file1.tif", "file2.tif", "file3.tif"]  # Replace with your TIFF file paths

metadata = read_metadata_from_csv(csv_file)
update_tiff_metadata(tiff_files, metadata)

