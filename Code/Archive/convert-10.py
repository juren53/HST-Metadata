import re
from datetime import datetime


def convert_date(date_str):
    if not date_str:                          # test for NONE date
        return "0000-00-00"                      

    if re.match(r'\d{4}-\d{4}', date_str):     # test for YYYY - YYYY 'thru date'
        year_range = date_str.split('-')
        return f"{year_range[1]}-00-00"

    elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"20{components[2]}-{components[0]:0>2}-{components[1]:0>2}"

    elif re.match(r'c\. \d{4}', date_str):            # test for circa date
        year = re.findall(r'\d{4}', date_str)[0]
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

    elif re.match(r'\d{4}', date_str):  # test for YYYY format
        return f"{date_str}-00-00"

    elif re.match(r'[A-Za-z]+, \d{2}/\d{2}/\d{4}', date_str):   # test for day_of_week, MM/DD/YYYY date
        try:
            date_object = datetime.strptime(date_str, "%A, %m/%d/%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]{3}-\d{2}', date_str):   # test for MMM-YY date
        try:
            date_object = datetime.strptime(date_str, "%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("19%y-%m-00")
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
    '4/24/05',
    '3-Oct-43',
    '10-Oct-44',
    '30-Jun-45',
    '27-Sep-48',
    'c. 1999',
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


]

print("PDB Date    Converted IPTC Date")
print("========    ===================")

for date in dates:
    #print(date, "\t", convert_date(date))

    print("{:<15}".format(date[:14]),\
        "{0:>10}".format(convert_date(date))
 

