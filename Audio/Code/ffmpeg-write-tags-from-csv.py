#!/usr/bin/python3
#---------------------ffmpeg-write-tags-from-csv.py v0.06--------------------------
# This code writes BWF tags to all MP3 files

# BWF labels used below. e.g ICOP, ISRC, ICRD, ISBJ, ICMT, INAM, IPRD
# Created Sat 24 Feb 2024 21:15:20 PM CST by JAU - Writes one file at a time
# TODO (1) read CSV data and loop thru files listed in CSV file extracting metadata
# (2) add date parsing routine from JPEG
# and writing tags for each file; add MP
# version
# reuse write-tags-from-csv.py v0.66 as much as possible

# Updated Mon 26 Jun 2023 12:30:58 PM CDT Added error trap for missing TIFFs from CSV files
# Updated Thu 20 Jun 2024 04:21:19 PM CDT Added Album tag TALB  v0.06
# ----------------------------------------------------------------
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
    'TALB': 'Title: SR59-12',
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
    'WXXX': 'NAC URL: https://catalog.archives.gov/',
    # Add more metadata fields as needed
}

# Constructing the ffmpeg command
ffmpeg_command = [
    'ffmpeg',
    '-i', input_file,
    '-y',
]

# Add metadata fields to the ffmpeg command
for key, value in metadata.items():
    ffmpeg_command.extend(['-metadata', f'{key}={value}'])

# Output WAV file path
output_file = "output.mp3"

# Add output file path to the ffmpeg command
ffmpeg_command.append(output_file)

# Execute the ffmpeg command to add metadata
subprocess.run(ffmpeg_command)

# Constructing the ffmpeg command to add thumbnail to MP3 file
thumbnail_command = [
    'ffmpeg -i output.mp3 -i output.jpg -map 0 -map 1 -c copy -id3v2_version 3 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (Front)" output-2.mp3'
]

# Execute the ffmpeg command to add thumbnail to MP3 file
subprocess.run(thumbnail_command)

