#---------------------add-thumbnail-02.py v0.02--------------------------
# This code adds JPEG thumbnails to MP3 files
# 
# 
# 
# Created Thu 20 Jun 2024 11:22:33 AM CDT
# Updated Fri 21 Jun 2024 08:19:48 PM CDT  Added argparse to input AN 
#                                          to build the MP3 filename

# ----------------------------------------------------------------

import subprocess
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Add thumbnail to an MP3 file using FFmpeg.')
parser.add_argument('text', type=str, help='The accession number (i.e. filename) of the MP3 file')

# Parse the arguments
args = parser.parse_args()

# Construct the filename
filename = args.text + ".mp3"

# Construct the FFmpeg command
cmd = [
    'ffmpeg', 
    '-i', filename, 
    '-i', 'temp.jpg', 
    '-map', '0', 
    '-map', '1', 
    '-c', 'copy', 
    '-id3v2_version', '3', 
    '-metadata:s:v', 'title=Album cover', 
    '-metadata:s:v', 'comment=Cover (Front)', 
    'output-2.mp3'
]

# Run the FFmpeg command
subprocess.run(cmd)



