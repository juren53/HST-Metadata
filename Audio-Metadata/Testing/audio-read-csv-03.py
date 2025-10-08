#!/usr/bin/python3
#---------------------audio-read-csv.py  v0.03--------------------------
# This code reads from HSTL audio data output from a CSV file.
# It converts dates from HSTL audio db in DD-MMM-YY format
# into ISO 8701 standard date formate YYYY-MM-DD and reads 
# column headings in the CSV file as variable names
# 
# Created Tue 24 Jun 2024 04:22:44 PM CDT  Reads dates from LIST_Audio-Dates.txt   ver 0.01
# Updated Wed 25 Jun 2024 01:33:55 AM CDT  Read data from CSV file  ver 0.02
# Updated Thu 26 Jun 2024 05:43:22 AM CDT  Write tags to MP3 files  ver 0.03

# ----------------------------------------------------------------

import csv
import datetime

# Define a dictionary to map month abbreviations to numbers
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

# Open the CSV file
with open('short.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Iterate over each row in the CSV file
    for row in reader:
        # Extract the date from the 'Date' column
        date_str = row['Date']
        title = row['title']
        an = row['Accession Number']
        restrictions = row['Restrictions']
        place = row['Place']
        speakers = row['Speakers']
        copyright = row['Production and Copyright']
        description = row['Description']

        
        # Split the date string into components
        components = date_str.split('-')
        if len(components) != 3:
            print(f"Invalid date: {date_str}")
            continue

        day, month, year = components
        month_num = month_map[month[:3]]
        year = int(year)
        if year < 100:
            year += 1900

        # Create a datetime object from the components
        try:
            dt = datetime.date(year, month_num, int(day))
        except ValueError:
            print(f"Invalid date: {date_str}")
            continue

        # Print the original date and the ISO 8601 date

        filename = an+".mp3"

        print(f"{an}   {dt.isoformat()[:10]} {filename}")

        #print(f"{date_str} -> {dt.isoformat()[:10]}  {title_str}")

        ##############################################

        import subprocess

        # Path to your input WAV file
        input_file = filename

        # Metadata dictionary
        metadata = {
            'COMM': 'Description: '+description,
            'ISBJ': 'Description: '+description,
            'IPLS': 'Involved People: Harry Truman',
            'IPRD': 'Accession Number: '+an,
            'TIT1': 'Grouping: NARA-HST-SRC Sound Recordings Collection',
            'TIT2': 'Title: '+an,
            'TALB': 'Title: '+an,
            'TCON': 'Genre: speech',
            'TCOP':  restrictions,
            'TIT3': 'Description: '+description,
            'ISRC': 'Source: Harry S. Truman Library',
            'TPE1': 'Artist: Harry S. Truman Library',
            'TPUB': 'Publisher: '+copyright,
            'TDAT': 'Date DDMM: '+str(day)+str(month_num),
            'TYER': 'Date YYYY: '+str(year),
            'TOFN': 'Original File Name: '+filename,
            'TORY': 'Original Release Year: '+str(year),
            'TRDA': 'Recording Date: '+dt.isoformat()[:10],
            'ICRD': 'Date String: '+date_str,
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
        output_file = an+"-output.mp3"

        # Add output file path to the ffmpeg command
        ffmpeg_command.append(output_file)

        # Execute the ffmpeg command to add metadata
        subprocess.run(ffmpeg_command)



        # Construct the FFmpeg command to overlay the AN in yellow onto the JPEG thumbnail
        cmd = [
            'ffmpeg',
            '-i', 'HST-thumbnail-c.png',
            '-y',
            '-vf', f'drawtext=text=\'{an}\':x=10:y=10:fontsize=24:fontcolor=yellow:box=1:boxcolor=black@0.5',
            'temp.jpg'
        ]

        # Run the FFmpeg command that creates the custom thumbnail
        subprocess.run(cmd)

        
        # Constructing the ffmpeg command to add thumbnail to MP3 file
        thumbnail_command = [
            'ffmpeg',
            ' -i {an+"-output.mp3"} -i output.jpg -map 0 -map 1 -c copy -id3v2_version 3 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (Front)" output-2.mp3'

        ]

        # Execute the ffmpeg command to add thumbnail to MP3 file
        subprocess.run(thumbnail_command)

        
