#!/usr/bin/python3
#------------date-conversion.py -- updated Tue 22 Aug 2023 06:56:49 PM CDT ----------------
#
# This code converts test dates from HST PDB to the ISO Date format of YYYY-MM-DD.
# HST PDB has a _WIDE_ variety of date formats that this code tests for
# in order for it to output a date that fits the YYY-MM-DD format
# 
#
# Created Tue 27 Jun 2023 06:01:35 PM CDT by JAU
# Updated Fri 30 Jun 2023 07:37:31 AM CDT added tests for circa dates and many others
# updated Tue 22 Aug 2023 06:56:49 PM CDT added test for circa dates like " Ca.   Saturday, 07/01/1950"
#----------------------------------------------------------------

import re
from datetime import datetime


def convert_date(date_str):

    if date_str == 'None':                      # test/convert a date like `NONE` to 0000-00-00
        return "0000-00-00"

    elif re.match(r'\d{4}-\d{4}', date_str):     # test/convert a date like '1900-1901' i.e.'thru date'
        year_range = date_str.split('-')
        return f"{year_range[1]}-00-00"

    elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"20{components[2]}-{components[0]:0>2}-{components[1]:0>2}"

    elif re.match(r'c\. ?\d{4}', date_str):                   # test/convert a date like `c.1939`
        year = re.findall(r'\d{4}', date_str)[0]
        return f"{year}-00-00"

    elif re.match(r"ca\. ?\d{4}", date_str):                  # test/convert a date like `ca.1939`
        year = date_str.split(".")[1].strip()
        return f"{year}-00-00"

    elif re.match(r'\d{1,2}-[A-Za-z]{3}-\d{2}', date_str):    # test/covert a date like 20-Dec-49
        try:
            date_object = datetime.strptime(date_str, "%d-%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("%Y-%m-%d")
            return f"{year:0>4}-{formatted_date[5:]}"
        except ValueError:
            return date_str

    elif re.match(r'\d{4}', date_str):                       # test/convert a date like 1939
        return f"{date_str}-00-00"

    elif re.match(r'[A-Za-z]+, \d{2}/\d{2}/\d{4}', date_str):   #test/covert a date like Monday, 03/23/1964
        try:
            date_object = datetime.strptime(date_str, "%A, %m/%d/%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]{3}-\d{2}', date_str):   # test/convert a date like May-62
        try:
            date_object = datetime.strptime(date_str, "%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("19%y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]+ \d{4}', date_str):  # test/convert a date like July 1948
        try:
            date_object = datetime.strptime(date_str, "%B %Y")
            formatted_date = date_object.strftime("%Y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]+, \d{4}', date_str):  # test/convert a date like July, 1948
        try:
            date_object = datetime.strptime(date_str, "%B, %Y")
            formatted_date = date_object.strftime("%Y-%d-00")
            return formatted_date
        except ValueError:
            return date_str


    elif re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date_str):  # test/convert a date like `September 18, 1945`
        try:
            date_object = datetime.strptime(date_str, "%B %d, %Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str


    elif re.match(r"Ca\.\s+([A-Za-z]+), (\d{2})/(\d{2})/(\d{4})", date_str):   # test/convert a date like`Ca.   Saturday, 07/01/1950`
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
    'Ca.   Saturday, 07/01/1950',
    'Ca.   Monday, 06/01/1953',
    'Friday, 08/20/1948 - Sunday, 08/29/1948',

]

print("PDB Date      Converted IPTC Date")
print("========      ===================")

for date in dates:
    #print(date, "\t", convert_date(date))

    print("{:<30}".format(date[:30]),\
        "{0:>10}".format(convert_date(date)))
 

