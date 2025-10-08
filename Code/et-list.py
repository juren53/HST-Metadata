#!/usr/bin/python3
#-----------------------------------------------------------
# ############   et-list.py  v0.1  ################
# THis uses ExifTool to list errors warnings and metadata for a single image file.
#    
#  Created 	Sat 01 Jun 2024 02:37:51 PM CDT
#
#
#-----------------------------------------------------------


import argparse
#import shutil     # Import file copy library
import subprocess # Import subprocess library

# Create argument parser
parser = argparse.ArgumentParser(
    prog='fix-offsets.py',
    description='This program fixes the offset errors and warning messages in JPEG files',
    epilog='Ver 0.3'
)

# Add filename argument
parser.add_argument('filename') # Source file path

# Parse arguments
args = parser.parse_args()

# Assuming the filename argument is passed correctly
source_file = args.filename


# ExifTool validation checker
command = f'exiftool -validate -warning -error -a '+ source_file
subprocess.run(command, shell=True, check=True)

# ExifTool detail list
command = f'exiftool -a -G0:1 -s '+ source_file
subprocess.run(command, shell=True, check=True)

