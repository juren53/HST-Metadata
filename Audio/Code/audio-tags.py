#!/usr/bin/python3
#---------------------audio-tags.py  v0.07   --------------------------
# Preliminarily named audio-read-csv.py v 0.01 - 0.06 now called audio-tags.py
# This code reads from HSTL audio data output from a CSV file.
# It converts dates from HSTL audio db in DD-MMM-YY format
# into ISO 8701 standard date formate YYYY-MM-DD and reads 
# column headings in the CSV file as variable names
# 
# Created Tue 24 Jun 2024 04:22:44 PM CDT  Reads dates from LIST_Audio-Dates.txt   ver 0.01
# Updated Wed 25 Jun 2024 01:33:55 AM CDT  Read data from CSV file  ver 0.02
# Updated Thu 26 Jun 2024 05:43:22 AM CDT  Write tags to MP3 files  ver 0.03
# Updated Sat 29 Jun 2024 02:13:43 AM CDT  Embed custom thumbnails into MP3 files ver 0.04
# Updated Sat 29 Jun 2024 09:02:38 AM CDT  Writes tagged MP3s to a processed directory ver 0.05
# Updated Sun 30 Jun 2024 03:10:22 AM CDT  Writes temporary output files to 'tmp/' directory ver 0.06
# Updated Mon 01 Jul 2024 01:09:29 PM CDT  Renamed to audio-tags.py & csv_filename variable created ver 0.07
# ----------------------------------------------------------------

import csv
import datetime

#csv_filename = "short.csv"
csv_filename = "two.csv"

# Define a dictionary to map month abbreviations to numbers
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

# Open the CSV file
with open(csv_filename, 'r') as csvfile:
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


        # Build filename variable from accession number variable + .mp3 extension
        filename = an+".mp3"

        # Print the original date and the ISO 8601 date
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
            'TEXT': 'Location: '+place,
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
            '-i', input_file,Only $2,750.00
            '-y',
        ]

        # Add metadata fields to the ffmpeg command
        for key, value in metadata.items():
            ffmpeg_command.extend(['-metadata', f'{key}={value}'])

        # Output WAV file path
        output_file = 'tmp/'+an+"-output.mp3"

        # Add output file path to the ffmpeg command
        ffmpeg_command.append(output_file)

        # Execute the ffmpeg command to add metadata
        subprocess.run(ffmpeg_command)



        # Construct the FFmpeg command to overlay the AN in yellow onto the JPEG thumbnail
        cmd = [
            'ffmpeg',
            '-i', 'HST-thumbnail-c.png',
            '-y',
            '-vf', f'drawtext=text=\'{an}\':x=10:y=10:fontsize=32:fontcolor=yellow:box=1:boxcolor=black@0.5',
            'temp.jpg'
        ]

        # Run the FFmpeg command that creates the custom thumbnail
        subprocess.run(cmd)

        # Constructing the ffmpeg command to add thumbnail to MP3 file
        input_file = 'tmp/'+an+'-output.mp3'
        thumbnail_file = 'temp.jpg'
        output_file = "processed/"+an+'.mp3'

        thumbnail_command = [
            'ffmpeg',
            '-i', input_file,
            '-y',
            '-i', thumbnail_file,
            #'-vf format=yuv420p',      ################################
            '-map', '0',
            '-map', '1',
            '-c', 'copy',
            '-id3v2_version', '3',
            '-metadata:s:v', 'title="Album cover"',
            '-metadata:s:v', 'comment="Cover (Front)"',
            output_file

        ]

        # Execute the ffmpeg command to add thumbnail to MP3 file
        subprocess.run(thumbnail_command)

        
