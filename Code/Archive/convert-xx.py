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

    return date_str


# test dates taken from HST PDB
dates = [
    'None',
    '1939',
    'September 18, 1945',
    'ca.1968',
    'July 1948',
    'July, 1948'
]

print("PDB Date               Converted IPTC Date")
print("==================     ===================")

for date in dates:
    print("{:<22} {:>20}".format(date, convert_date(date)))

