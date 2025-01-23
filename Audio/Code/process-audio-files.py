#!/usr/bin/python3
#---------------------process-audio-files.py  v 0.01  --------------------------
# this Python code applies metatags from an HSTL AV Archive CSV file to MP3 files
#
#
# Created Wed 22 Jan 2025 02:25:09 PM CST  initial integration of fragments
# -----------------------------------------------------------------------------

import csv
import datetime
import subprocess
import os
import requests
from urllib.parse import urlparse

audio_csv = "test.csv"

# Create necessary directories
os.makedirs('tmp', exist_ok=True)
os.makedirs('processed', exist_ok=True)

# Define a dictionary to map month abbreviations to numbers
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

def download_file(url, local_filename):
    """Download a file from URL if it doesn't exist locally"""
    if os.path.exists(local_filename):
        print(f"File already exists: {local_filename}")
        return
    
    print(f"Downloading: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {local_filename}")
    else:
        print(f"Failed to download: {url}")
        return None

def process_audio_file(row, mp3_url, file_number):
    """Process a single MP3 file with metadata"""
    if not mp3_url:
        return
    
    # Extract the date from the 'Date' column
    date_str = row['Date']
    
    # Parse the date
    components = date_str.split('-')
    if len(components) != 3:
        print(f"Invalid date: {date_str}")
        return

    day, month, year = components
    month_num = month_map[month[:3]]
    year = int(year)
    if year < 100:
        year += 1900

    # Create datetime object
    try:
        dt = datetime.date(year, month_num, int(day))
    except ValueError:
        print(f"Invalid date: {date_str}")
        return

    # Get filename from URL
    filename = os.path.basename(urlparse(mp3_url).path)
    an = row['Accession Number']
    
    # If there are multiple files, append the file number to the accession number
    if file_number > 1:
        output_filename = f"{an}-{file_number}.mp3"
    else:
        output_filename = f"{an}.mp3"

    # Download the file
    download_file(mp3_url, f"tmp/{filename}")

    # Metadata dictionary
    metadata = {
        'COMM': f"{row['Description']} {date_str}",
        'ISBJ': f"{row['Description']} {date_str}",
        'comment': f"Audition: {row['Description']} {date_str}",
        
        'TIT1': 'NARA-HST-SRC Sound Recordings Collection',
        'TIT2': row['title'],
        'TIT3': f"{row['Description']} {date_str}",
        'TALB': an,
        'IPRD': an,
        'TPE1': 'Harry S. Truman Library',
        'IPLS': 'Harry Truman',
        'TCOP': row['Restrictions'],
        'TPUB': row['Production and Copyright'],
        '©pub': row['Production and Copyright'],
        'composer': f"Audition: {row['Production and Copyright']}",
        
        'dc:publisher': row['Production and Copyright'],
        'ISRC': 'Harry S. Truman Library',

        'ICRD': date_str,
        'TDAT': f"{dt.isoformat()[:10][-2:]}{str(month_num)}",
        'TYER': str(year),
        'TORY': str(year),
        'TRDA': dt.isoformat()[:10],

        'TOFN': filename,
        'TCON': 'speech',

        'WOAS': 'Source URL: https://www.trumanlibrary.gov/library/sound-recordings-collection',
        'WXXX': 'NAC URL: https://catalog.archives.gov/',
        'TEXT': 'HSTL Metatagging Software: audio-tags-14.py using FFmpeg [5th round of testing] 2024-11-12'
    }

    # Constructing the ffmpeg command for metadata
    ffmpeg_command = ['ffmpeg', '-i', f"tmp/{filename}", '-y']
    for key, value in metadata.items():
        ffmpeg_command.extend(['-metadata', f'{key}={value}'])
    ffmpeg_command.append(f'tmp/{output_filename}-tagged.mp3')

    # Execute the ffmpeg command to add metadata
    subprocess.run(ffmpeg_command)

    # Create thumbnail with accession number
    cmd = [
        'ffmpeg',
        '-i', 'HST-thumbnail-c.png',
        '-y',
        '-vf', f'drawtext=text=\'{an}\':x=10:y=10:fontsize=32:fontcolor=yellow:box=1:boxcolor=black@0.5:fontfile=arial.ttf',
        'temp.jpg'
    ]
    subprocess.run(cmd)

    # Add thumbnail to MP3
    thumbnail_command = [
        'ffmpeg',
        '-i', f'tmp/{output_filename}-tagged.mp3',
        '-y',
        '-i', 'temp.jpg',
        '-map', '0',
        '-map', '1',
        '-c', 'copy',
        '-id3v2_version', '3',
        '-metadata:s:v', 'title="HST icon"',
        '-metadata:s:v', 'comment="Cover (Front)"',
        f'processed/{output_filename}'
    ]
    subprocess.run(thumbnail_command)
    
    print(f"Processed: {output_filename}")

# Process the CSV file
with open(audio_csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Process each Sound_File column if it contains a URL
        for i in range(1, 11):
            column = f'Sound_File_{i}'
            if column in row and row[column]:
                process_audio_file(row, row[column].strip(), i)
