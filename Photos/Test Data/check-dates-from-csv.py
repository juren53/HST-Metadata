#!/usr/bin/python3
#--------------------- check-dates-csv.py --------- Wed 23 Aug 2023 02:31:49 AM CDT ----------------
# This code checks dates in the CSV file generated from the HSTL PDB to verify that the 
# date conversion algorithms work for the series being processed.  
# The program should be run before metadata tags are written using write-tags-from-csv.py.
#
# Created Tue 15 Aug 2023 07:55:45 PM CDT by JAU
# updated Wed 23 Aug 2023 02:31:49 AM CDT added test for circa dates like " Ca.   Saturday, 07/01/1950"
# -------------------------------------------------------------------------------------------------

import csv
import re
import datetime as dt 
from datetime import datetime

#  date conversion function here...


def convert_date(date_str):

    if date_str == 'None':                            # test/convert dates like NONE to 0000-00-00

         return f"0000-00-00"

  
    elif date_str == '\n\n\n\n\n\n\n\n\n\n \n\nHarry':  # test/convert dates like NONE to 0000-00-00
        return f"0000-00-00"

    elif re.match(r'\d{4}-\d{4}', date_str):          # test/convert dates like 'thru date' - YYYY - YYYY 
        year_range = date_str.split('-')
        return f"{year_range[1]}-00-00"

    elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"20{components[2]}-{components[0]:0>2}-{components[1]:0>2}"

    elif re.match(r'c\. ?\d{4}', date_str):            # test/convert dates like circa date eg. c.1939
        year = re.findall(r'\d{4}', date_str)[0]
        return f"{year}-00-00"

    elif re.match(r"ca\. ?\d{4}", date_str):            # test/convert dates like circa  ca.1939 date
        year = date_str.split(".")[1].strip()
        return f"{year}-00-00"

    elif re.match(r"Ca\. ?\d{4}", date_str):            # test/convert dates like circa  Ca.1939 date
        year = date_str.split(".")[1].strip()
        return f"{year}-00-00"

    elif re.match(r"Ca\.  ?\d{2}/\d{4}$", date_str):    # test/convert dates like circa  Ca. 10/1911 date
        year_month = date_str.split(".")[1].strip()
        month, year = year_month.split("/")
        return f"{year}-{month:0>2}-00"

    elif re.match(r'\d{1,2}-[A-Za-z]{3}-\d{2}', date_str):   # test/convert dates like '20-Dec-49'
        try:
            date_object = dt.datetime.strptime(date_str, "%d-%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("%Y-%m-%d")
            return f"{year:0>4}-{formatted_date[5:]}"
        except ValueError:
                    return date_str

    elif re.match(r'\d{4}', date_str):                     # test/convert dates like 1939  
        return f"{date_str}-00-00"

    elif re.match(r'[A-Za-z]+, \d{2}/\d{2}/\d{4}', date_str):   #test/convert dates like Monday, 03/23/1964  
        try:
            date_object = dt.datetime.strptime(date_str, "%A, %m/%d/%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]{3}-\d{2}', date_str):          # test/convert dates like MMM-YY  e.g. May-62 
        try:
            date_object = dt.datetime.strptime(date_str, "%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("19%y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]+ \d{4}', date_str):              # test/convert dates like July 1948 
        try:
            date_object = dt.datetime.strptime(date_str, "%B %Y")
            formatted_date = date_object.strftime("%Y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]+, \d{4}', date_str):               # test/convert dates like July, 1948
        try:
            date_object = dt.datetime.strptime(date_str, "%B, %Y")
            formatted_date = date_object.strftime("%Y-%d-00")
            return formatted_date
        except ValueError:
           return date_str


    elif re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date_str):  # test/convert dates like September 18, 1945
        try:
            date_object = dt.datetime.strptime(date_str, "%B %d, %Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str


    elif re.match(r"Ca\.\s+([A-Za-z]+), (\d{2})/(\d{2})/(\d{4})", date_str):   # ttest/convert dates like`Ca.   Saturday, 07/01/1950`
        try:
            match = re.match(r"Ca\.\s+([A-Za-z]+), (\d{2})/(\d{2})/(\d{4})", date_str)
            day_name = match.group(1)
            month = int(match.group(2))
            day = int(match.group(3))
            year = int(match.group(4))

            date_object = datetime(year, month, day)
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str


    return date_str


# Read the CSV file and extract dates from column C
csv_file_path = 'export.csv'

n = 1

dates_to_convert = []

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if len(row) > 2:                    # Ensure the row has enough columns
            date_str = row[2].strip()       # Assuming column C is the third column
            dates_to_convert.append(date_str)
            
            an = row[1].strip()


# Convert dates and print the results
print("CSV Date          Converted  Date")
print("========          ===============")

for original_date, converted_date in zip(dates_to_convert, map(convert_date, dates_to_convert)):
 
    print("{:<40} {:>12} {:>12}{:>12}".format(original_date, converted_date, an, n))

    n = n + 1

print("\nConversion complete.")

