#!/usr/bin/python3
#---------------------audio-read-csv.py  v0.01--------------------------
# This code reads from HSTL audio data output to a CSV file.
# It converts dates from HSTL audio db in DD-MMM-YY format
# into ISO 8701 standard date formate YYYY-MM-DD and reads 
# column headings in the CSV file as variable names
# 
# Created Tue 24 Jun 2024 04:22:44 PM CDT  Reads dates from LIST_Audio-Dates.txt   ver 0.01
#

# ----------------------------------------------------------------

import csv
import datetime

# Define a dictionary to map month abbreviations to numbers
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

# Open the CSV file
with open('FullExport-SoundExample-1-17-24.csv', 'r') as csvfile:
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

        print(f"{an} {date_str} -> {dt.isoformat()[:10]}")

        #print(f"{date_str} -> {dt.isoformat()[:10]}  {title_str}")
