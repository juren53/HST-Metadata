import csv
#import datetime
from datetime import datetime
import subprocess



# Define a dictionary to map month abbreviations to numbers
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

csv_filename = "two.csv"

# Open the CSV file
with open(csv_filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Iterate over each row in the CSV file
    for row in reader:
        # Extract necessary fields from the row
        date_str = row['Date']
        an = row['Accession Number']
        description = row['Description']
        place = row['Place']
        copyright = row['Production and Copyright']
        filename = an + ".mp3"
 

        ##### Date Conversion Section ##################
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
            dt = datetime(int(year), month_num, int(day)).date()
        except ValueError:
            print(f"Invalid date: {date_str}")
            continue
  

        # Convert the string to a datetime object
        date_obj = datetime.strptime(date_str, '%d-%b-%y')
  
        # Reformat the date object back to a string with the day padded to two digits
        padded_date_str = date_obj.strftime('%d-%b-%y')
      
        year = int(datetime.datetime.strptime(padded_date_str, "%d-%b-%Y").year)


        # Metadata dictionary
        metadata = {
            'COMM': 'Description: ' + description,
            'ISBJ': 'Description: ' + description,
            'IPLS': 'Involved People: Harry Truman',
            'IPRD': 'Accession Number: ' + an,
            'TI1': 'Grouping: NARA-HST-SRC Sound Recordings Collection',
            'TI2': 'Title: ' + an,
            'TALB': 'Title: ' + an,
            'TCON': 'Genre: speech',
            'TCOP': restrictions,
            'TEXT': 'Location: ' + place,
            'TI3': 'Description: ' + description,
            'ISRC': 'Source: Harry S. Truman Library',
            'TPE1': 'Artist: Harry S. Truman Library',
            'TPUB': 'Publisher: ' + copyright,
            'TDAT': 'Date DDMM: ' + str(datetime.datetime.strptime(date_str, "%d-%b-%Y").day).zfill(2) + str(month_map[date_str[:3]]),
            'TYER': 'Date YYYY: ' + str(year),
            'TOFN': 'Original File Name: ' + filename,
            'TORY': 'Original Release Year: ' + str(year),
            'TRDA': 'Recording Date: ' + date_str,
            'ICRD': 'Date String: ' + date_str,
            'WDAS': 'Source URL: https://www.trumanlibrary.gov/library/sound-recordings-collection',
            'WXXX': 'NAC URL: https://catalog.archives.gov/',
        }

        # Constructing the ffmpeg command to add metadata and create thumbnail
        ffmpeg_command = [
            'ffmpeg',
            '-i', filename,
            '-y',
            '-vf', f'drawtext==\'{an}\':x=10:y=10:fontsize=32:fontcolor=yellow:box=1:boxcolor=black@0.5',
            '-metadata', f'COMM={metadata["COMM"]}',
            '-metadata', f'TIT2={metadata["TI2"]}',
            '-metadata', f'TALB={metadata["TALB"]}',
            '-metadata', f'TCON={metadata["TCON"]}',
            '-metadata', f'TCOP={metadata["TCOP"]}',
            '-metadata', f'TEXT={metadata["TEXT"]}',
            '-metadata', f'TIT3={metadata["TI3"]}',
            '-metadata', f'ISRC={metadata["ISRC"]}',
            '-metadata', f'TPE1={metadata["TPE1"]}',
            '-metadata', f'TPUB={metadata["TPUB"]}',
            '-metadata', f'TDAT={metadata["TDAT"]}',
            '-metadata', f'TYER={metadata["TYER"]}',
            '-metadata', f'TOFN={metadata["TOFN"]}',
            '-metadata', f'TORY={metadata["TORY"]}',
            '-metadata', f'TRDA={metadata["TRDA"]}',
            '-metadata', f'ICRD={metadata["ICRD"]}',
            '-metadata', f'WDAS={metadata["WDAS"]}',
            '-metadata', f'WXXX={metadata["WXXX"]}',
            '-filter_complex', '[0:a]aformt=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a]',
            '-map', '[a]',
            '-id3v2_version', '3',
            '-metadata:s:v', 'title="Album cover"',
            '-metadata:s:v', 'comment="Cover (Front)"',
            'processed/' + an + '.mp3'
        ]

        # Execute the ffmpeg command
        subprocess.run(ffmpeg_command)

