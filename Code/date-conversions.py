#!/usr/bin/python3
#---------------------date-conversion.py-------------------------------
# This code converts dates from HST PDB to the IPTC Date format of MM:DD:YYY.
# HST PDB has a _WIDE_ variety of date formats that this code tests for
# in order for it to output a date that fits the MM:DD:YYYY format
# 
#
# Created Tue 27 Jun 2023 06:01:35 PM CDT by JAU
# 
#----------------------------------------------------------------

import re
from datetime import datetime

def convert_date(date_str):
    if not date_str:
        return "00:00:0000"

    if re.match(r'\d{4}-\d{4}', date_str):
        year_range = date_str.split('-')
        return f"00:00:{year_range[1]}"
    elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"{components[0]:0>2}:{components[1]:0>2}:{'20' + components[2] if int(components[2]) <= 10 else '19' + components[2]}"
    elif re.match(r'c\. \d{4}', date_str):
        year = re.findall(r'\d{4}', date_str)[0]
        return f"00:00:{year}"
    elif re.match(r'\d{1,2}-[A-Za-z]{3}-\d{2}', date_str):
        date_object = datetime.strptime(date_str, "%d-%b-%y")
        return date_object.strftime("%m:%d:%Y")

    return date_str

dates = [
    None,
    '1900-1901',
    '4/18/05',
    '4/22/05',
    'c. 1939',
    '4/22/05',
    '4/24/05',
    '4/24/05',
    '4/24/05',
    '3-Oct-43',
    '10-Oct-44',
    '30-Jun-45',
    '27-Sep-48',
    '20-Dec-49',
    '26-Jun-57',
    '15-Oct-57',
    '21-Jan-59',
    '2-Nov-59'
]

for date in dates:
    print(convert_date(date))

