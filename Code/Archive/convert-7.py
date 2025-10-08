import re
from datetime import datetime

def convert_date(date_str):
    if not date_str:                          # test for NONE date
        return "00000000"                      

    if re.match(r'\d{4}-\d{4}', date_str):     # test for YYYY - YYYY 'thru date'
        year_range = date_str.split('-')
        return f"{year_range[1]}0000"

    elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
        components = date_str.split('/')
        return f"20{components[2]}{components[0]:0>2}{components[1]:0>2}"

    elif re.match(r'c\. \d{4}', date_str):            # test for circa date
        year = re.findall(r'\d{4}', date_str)[0]
        return f"{year}0000"

    elif re.match(r'\d{1,2}-[A-Za-z]{3}-\d{2}', date_str):   # test for DD-MMM-YY date
        try:
            date_object = datetime.strptime(date_str, "%d-%b-%y")
            formatted_date = date_object.strftime("%Y%m%d")
            return f"19{formatted_date[2:]}"
        except ValueError:
            return date_str

    return date_str

# test dates taken from HST PDB
dates = [
    None,
    '1900-1901',
    '4/18/05',
    '4/22/05',
    'c. 1939',
    '4/22/05',
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
   # '1939',

]

print("PDB Date    Converted IPTC Date")
print("========    ===================")

for date in dates:
    print(date, "\t", convert_date(date))

