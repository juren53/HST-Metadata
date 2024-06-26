#!/usr/bin/python3
#---------------------audio-date-convert.py  v0.02--------------------------
# This code converts dates from HSTL audio db in DD-MMM-YY format
# into ISO 8701 standard date formate YYYY-MM-DD.  
# 
# Created Mon 24 Jun 2024 04:22:44 PM CDT  Reads dates from LIST_Audio-Dates.txt   ver 0,01
# Updated Mon 24 Jun 2024 05:41:11 PM CDT  Reads dates from FullExport-SoundExample-1-17-24.csv  ver 0,02

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
        title_str = row['title']
        
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
        #print(f"{date_str} -> {dt.isoformat()[:10]}  {title_str}")
        print(f"{date_str} -> {dt.isoformat()[:10]}")
