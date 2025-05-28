#!/usr/bin/python3
#-----------------------------------------------------------
# ############   fix-offsets.py  v0.4  ################
# THis program finds offset and warning errors that causes
# JPEG images uploaded to NARA Catalog for fail.
# It uses ExifTool and FFjpeg to fix the JPEG image file.
#    
#  Created 	Sat 25 May 2024 02:37:51 PM CDT
#  Updated  Sat 25 May 2024 02:57:22 PM CDT   added ExifTool validation to end 
#  Updated  Sun 26 May 2024 01:55:28 AM CDT   added argparse messages & comments
#  Updated  Sun 26 May 2024 01:55:28 AM CDT   added ExifTool detailed listing
#-----------------------------------------------------------


import argparse
import shutil     # Import file copy library
import subprocess # Import subprocess library

# Create argument parser
parser = argparse.ArgumentParser(
    prog='fix-offsets.py',
    description='This program fixes the offset errors and warning messages in JPEG files',
    epilog='Ver 0.4'
)

# Add filename argument
parser.add_argument('filename') # Source file path

# Parse arguments
args = parser.parse_args()

# Assuming the filename argument is passed correctly
source_file = args.filename

# Destination file path
destination_file = 'input.jpg'

# Temporary output file
output_file = 'output.jpg'

# Copy the source file to the destination
shutil.copy(source_file, destination_file)
print(f"File {source_file} has been copied to {destination_file}")

# Run FFmpeg command
command = f'ffmpeg -i {destination_file} output.jpg'
subprocess.run(command, shell=True, check=True)

# Run extract IPTC tags from post-processed.jpg and embedd tags into output.jpg
command = f'exiftool -tagsfromfile input.jpg -IPTC:all output.jpg'
subprocess.run(command, shell=True, check=True)

# Copy tempory fixed output.jpg to original {accession-no).jpg filename
shutil.copy(output_file,source_file)

# Delete temp input and output files
command = f'rm *put.jpg*'
subprocess.run(command, shell=True, check=True)

# ExifTool validation checker
command = f'exiftool -validate -warning -error -a '+ source_file
subprocess.run(command, shell=True, check=True)

# ExifTool detailed listing
command = f'exiftool -a -G0:1 -s '+ source_file
subprocess.run(command, shell=True, check=True)


