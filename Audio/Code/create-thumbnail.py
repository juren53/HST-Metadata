#!/usr/bin/python3
#---------------------create-thumbnail-2.py v0.02--------------------------
# This code adds accession numbers to JPEG thumbnails  that will later be embedded
# in MP3 files 


# Created Thy 20 Jun 2024 11:22:33 AM CDT
# Updated Fri 21 Jun 2024 09:19:48 AM CDT  Added argparse CLI AN argument

# ----------------------------------------------------------------

import subprocess
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Overlay text on an image using FFmpeg.')
parser.add_argument('text', type=str, help='The text to be printed on the image')

# Parse the arguments
args = parser.parse_args()

# Construct the FFmpeg command to overlay the AN in yellow onto the JPEG thumbnail
cmd = [
    'ffmpeg',
    '-i', 'HST-thumbnail-c.png',
    '-y',
    '-vf', f'drawtext=text=\'{args.text}\':x=10:y=10:fontsize=24:fontcolor=yellow:box=1:boxcolor=black@0.5',
    'temp.jpg'
]

# Run the FFmpeg command
subprocess.run(cmd)

print("HST thumbnail created with ",args.text,"overlayed")


