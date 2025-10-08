#!/usr/bin/python3
#---------------------date-conversion.py-------------------------------
# This code converts dates from HST PDB to the IPTC Date format of YYY-MM-DD.
# HST PDB has a _WIDE_ variety of date formats that this code tests for
# in order for it to output a date that fits the YYY-MM-DD format
# 
#
# Created Tue 27 Jun 2023 06:01:35 PM CDT by JAU
# Updated Fri 30 Jun 2023 07:37:31 AM CDT added tests for circa dates and many others
#----------------------------------------------------------------

import re
from datetime import datetime


def convert_date(date_str):

    if date_str == 'None':  # convert NONE to 0000-00-00
        return "0000-00-00"

    if re.match(r'\d{4}-\d{4}', date_str):     # test for 'thru date' - YYYY - YYYY 
        year_range = date_str.split('-')
        return f"{year_range[1]}-00-00"

    elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"20{components[2]}-{components[0]:0>2}-{components[1]:0>2}"

    elif re.match(r'c\. ?\d{4}', date_str):            # test for circa date eg. c.1939
        year = re.findall(r'\d{4}', date_str)[0]
        return f"{year}-00-00"

    elif re.match(r"ca\. ?\d{4}", date_str):            # test for circa date ca.1939
        year = date_str.split(".")[1].strip()
        return f"{year}-00-00"

    elif re.match(r'\d{1,2}-[A-Za-z]{3}-\d{2}', date_str):   # test for DD-MMM-YY date
        try:
            date_object = datetime.strptime(date_str, "%d-%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("%Y-%m-%d")
            return f"{year:0>4}-{formatted_date[5:]}"
        except ValueError:
            return date_str

    elif re.match(r'\d{4}', date_str):  # 1939
        return f"{date_str}-00-00"

    elif re.match(r'[A-Za-z]+, \d{2}/\d{2}/\d{4}', date_str):   #test for Monday, 03/23/1964
        try:
            date_object = datetime.strptime(date_str, "%A, %m/%d/%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]{3}-\d{2}', date_str):   # test for MMM-YY date e.g. May-62
        try:
            date_object = datetime.strptime(date_str, "%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("19%y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'[A-Za-z]+ \d{4}', date_str):  # test for Month YYYY to YYYY-DD-00 eg. July 1948
        try:
            date_object = datetime.strptime(date_str, "%B %Y")
            formatted_date = date_object.strftime("%Y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'[A-Za-z]+, \d{4}', date_str):  # test for July, 1948
        try:
            date_object = datetime.strptime(date_str, "%B, %Y")
            formatted_date = date_object.strftime("%Y-%d-00")
            return formatted_date
        except ValueError:
            return date_str


    if re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date_str):  # test for September 18, 1945
        try:
            date_object = datetime.strptime(date_str, "%B %d, %Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    return date_str

# test dates taken from HST PDB
dates = [
    'None',
    '1900-1901',
    '4/18/05',
    '4/22/05',
    'c. 1939',
    'c.1999',
    '4/24/05',
    '3-Oct-43',
    '10-Oct-44',
    '27-Sep-48',
    '20-Dec-49',
    '26-Jun-57',
    '1945-1953',
    '15-Oct-57',
    '21-Jan-59',
    '2-Nov-59',
    '30-Sep-53',
    '1939',
    'Monday, 03/23/1964',
    'Feb-64',
    'Thursday, 07/19/1962',
    'May-62',
    'September 18, 1945',
    'ca. 1968',
    'ca.1968',
    'July 1948',
    'October 1947',
    'January, 1949',


]

print("PDB Date      Converted IPTC Date")
print("========      ===================")

for date in dates:
    #print(date, "\t", convert_date(date))

    print("{:<22}".format(date[:21]),\
        "{0:>10}".format(convert_date(date)))
 

