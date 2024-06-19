#!/usr/bin/python3
#---------------------ffmpeg-write-tags-from-csv.py v0.02--------------------------
# This code writes BWF tags to all MP3 files 
#  
#  
# BWF labels used below.  e.g ICOP, ISRC, ICRD, ISBJ, ICMT, INAM, IPRD
# 
# Created Sat 24 Feb 2024 21:15:20 PM CST by JAU - Writes one file at a time

# TODO (1) read CSV data and loop thru files listed in CSV file extracting metadata 
# (2) add date parsing routine from JPEG 
# and writing tags for each file; add MP# version
# reuse write-tags-from-csv.py v0.66 as much as possible
#
# **********Updated Mon 26 Jun 2023 12:30:58 PM CDT  Added error trap for missing TIFFs from CSV files **************

#----------------------------------------------------------------

import subprocess

# Path to your input WAV file
input_file = "SR59-12 BlackHawkWaltz.mp3"

# Metadata dictionary
metadata = {
    'COMM': 'Description: "The Black Hawk Waltz" piano solo performed by Harry S. Truman. Full song ',
    'ISBJ': 'Description: "The Black Hawk Waltz" piano solo performed by Harry S. Truman. Full song ',
    'IPLS': 'Involved People: Harry Truman',
    'IPRD': 'Accession Number: SR59-12',
    'TIT1': 'Grouping: NARA-HST-SRC Sound Recordings Collection',
    'TIT2': 'Title: SR59-12',
    'TCON': 'Genre: music',
    'TCOP': 'Copyright: Unrestricted',
    'TIT3': 'Description: "The Black Hawk Waltz" piano solo performed by Harry S. Truman. Full song ',
    'ISRC': 'Source: Harry S. Truman Library',
    'TPE1': 'Artist: Harry S. Truman Library',
    'TPUB': 'Publisher: production and copyright information',
    'TDAT': 'Date DDMM: 0309',
    'TYER': 'Date YYYY: 1948',
    'TOFN': 'Original File Name: SR59-12.mp3',
    'TORY': 'Original Release Year: 1948',
    'TRDA': 'Recording Date: Septemer 30, 1948',
    'ICRD': 'Date String: Septemer 30, 1948',
    'WDAS': 'Source URL: https://www.trumanlibrary.gov/library/sound-recordings-collection',
    'WXXX': 'User Defined URL: https://catalog.archives.gov/',
    # Add more metadata fields as needed
}

# Constructing the ffmpeg command
ffmpeg_command = [
    #'ffmpeg export FFMPEG_FORCE_OVERWRITE_OUTPUT=1'
    'ffmpeg',
    '-i', input_file,'-y',
]

# Add metadata fields to the ffmpeg command
for key, value in metadata.items():
    ffmpeg_command.extend(['-metadata', f'{key}={value}'])

# Output WAV file path
output_file = "output.mp3"

# Add output file path to the ffmpeg command
ffmpeg_command.append(output_file)

# Execute the ffmpeg command
subprocess.run(ffmpeg_command)

