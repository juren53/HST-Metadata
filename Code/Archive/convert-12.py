import re
from datetime import datetime


def convert_date(date_str):
    if date_str == 'None':  # convert NONE to 0000-00-00
        return "0000-00-00"

    if re.match(r'\d{4}', date_str):  # convert YYYY to YYYY-00-00
        return f"{date_str}-00-00"

    if re.match(r'[A-Za-z]+, \d{2}/\d{2}/\d{4}', date_str):  # convert Month DD, YYYY to YYYY-MM-DD
        try:
            date_object = datetime.strptime(date_str, "%B %d, %Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'ca\. \d{4}', date_str):  # convert ca. YYYY to YYYY-00-00
        year = re.findall(r'\d{4}', date_str)[0]
        return f"{year}-00-00"

    if re.match(r'[A-Za-z]+ \d{4}', date_str):  # convert Month YYYY to YYYY-DD-00
        try:
            date_object = datetime.strptime(date_str, "%B %Y")
            formatted_date = date_object.strftime("%Y-%d-00")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'[A-Za-z]+, \d{4}', date_str):  # convert Month, YYYY to YYYY-DD-00
        try:
            date_object = datetime.strptime(date_str, "%B, %Y")
            formatted_date = date_object.strftime("%Y-%d-00")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'\d{4}-\d{4}', date_str):     # test for YYYY - YYYY 'thru date'
        year_range = date_str.split('-')
        return f"{year_range[1]}-00-00"

  
    if re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"20{components[2]}-{components[0]:0>2}-{components[1]:0>2}"

    if re.match(r'c\. \d{4}', date_str):  # test for circa date
        year = re.findall(r'\d{4}', date_str)[0]
        return f"{year}-00-00"

    if re.match(r'\d{1,2}-[A-Za-z]{3}-\d{2}', date_str):  # test for DD-MMM-YY date
        try:
            date_object = datetime.strptime(date_str, "%d-%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100  # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("%Y-%m-%d")
            return f"{year:0>4}-{formatted_date[5:]}"
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
    'ca.1968',
    'July 1948',
    'January, 1949'


]

print("PDB Date      Converted IPTC Date")
print("========      ===================")

for date in dates:
    #print(date, "\t", convert_date(date))

    print("{:<22}".format(date[:21]),\
        "{0:>10}".format(convert_date(date)))
 

