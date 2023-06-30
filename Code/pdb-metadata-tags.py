#!/usr/bin/python3
#-----------------------------------------------------------
# ############   pdb-metadata-tags.py  ################
#  Extracts metadata from HST Photo Database for the AN 
#  provided as the first argument on the command line and
#  embeds the IPTC tags into the corresponding TIFF file.
#  Example: python(3) pdb-metadata-2.py 72-3113
#  Note: The file 72-3113.tif needs to bin the current directory
#  Created  Wed 27 Nov 2019 03:58:49 PM CST	
#  Updated	Mon 26 Jun 2023 09:44:14 PM CDT  added section 
#         embed IPTC tags to the corresponding TIFF file
#  Updated  Tues 27 Jun 2023 07:11:32 AM CDT added Byline 
#         Source tags 													 
#-----------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import sys
import dateparser
#import datetime
import datetime as dt 
import re
import exiftool
import os
import re
#from datetime import datetime


# et = exiftool.ExifTool()

#accno = "72-3113"   # - entry with three element date
#accno = "95-22-87"  # - entry with two element date
#accno = "2009-1504" # - entry with single element date
#accno = "2006-487"  # - entry with no date 
#accno = "80-16"     # - entry with no date or rights statement

#ObjectName = sys.argv[1]

filename = sys.argv[1]

ObjectName = os.path.splitext(filename)[0]

#filename = ObjectName + ".tif"

url = 'https://www.trumanlibrary.gov/photograph-records/' + ObjectName

response = requests.get(url, timeout=5)
html = response.content

soup = BeautifulSoup(html,'lxml')

print("ObjectName: " + ObjectName)
print(" ")

#### Extract Title #####

Headline = str(soup.h1.text).strip()
#print("HeadLine: " + str(soup.h1.text).strip())
#print("HeadLine: " + Headine)

alltext = soup.get_text()

#### Extract Description #####

left = (alltext.find("Description"))
right = (alltext.find("Date(s)"))

CaptionAbstract = (alltext[left+11:right].strip())
print(" ")
print("Caption-Abstract: " + CaptionAbstract)

#### Extracts Date #####

x = (alltext.find("Date(s)"))     # extracts text only 

D1=(alltext[x+12:x+30].rstrip())  # extracts date string as D1

D2 = dateparser.parse(D1)   # parses D1 date string into date variable D2

try:
    D2 = dt.datetime(D2.year, D2.month, D2.day)

    # D2 = dt.datetime(D2.year, D2.month, D2.day)
    #, settings={'STRICT_PARSING': True}

    print(" ")
    w = (len(re.findall(r'\w+', D1)))
    D2 = (D2.year,D2.month,D2.day)
    
    SpecialInstructions = D1

    print("SpecialInstructions: " + SpecialInstructions)


    if w == 1:
        print(str(D2[0]) + ":01:01")
    elif w == 2:
        print(str(D2[0]) + ":" + str('{:02d}'.format(D2[1]) + ":01"))
    else:
        print(str(D2[0]) + ":" + str('{:02d}'.format(D2[1]))+ ":" + str('{:02d}'.format(D2[2])))

except AttributeError:
    print(" ")
    print("Date: No Date string for this item in HST PDB")

#### Date Conversion Routine #####


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
            date_object = dt.datetime.strptime(date_str, "%d-%b-%y")
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
            date_object = dt.datetime.strptime(date_str, "%A, %m/%d/%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    elif re.match(r'[A-Za-z]{3}-\d{2}', date_str):   # test for MMM-YY date e.g. May-62
        try:
            date_object = dt.datetime.strptime(date_str, "%b-%y")
            year = date_object.year
            if year > 2021:  # assuming 2021 as the cutoff year for 19xx vs. 20xx
                year -= 100   # Subtract 100 years if the year is greater than 2021
            formatted_date = date_object.strftime("19%y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'[A-Za-z]+ \d{4}', date_str):  # test for Month YYYY to YYYY-DD-00 eg. July 1948
        try:
            date_object = dt.datetime.strptime(date_str, "%B %Y")
            formatted_date = date_object.strftime("%Y-%m-00")
            return formatted_date
        except ValueError:
            return date_str

    if re.match(r'[A-Za-z]+, \d{4}', date_str):  # test for July, 1948
        try:
            date_object = dt.datetime.strptime(date_str, "%B, %Y")
            formatted_date = date_object.strftime("%Y-%d-00")
            return formatted_date
        except ValueError:
            return date_str


    if re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date_str):  # test for September 18, 1945
        try:
            date_object = dt.datetime.strptime(date_str, "%B %d, %Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return date_str

    return date_str


print(convert_date(D1))

Date = (convert_date(D1))


#### Extract Rights Statement #####

Rights = soup.find('div', {'class': "field field--name-field-rights-undetermined-text field--type-markup field--label-hidden field__item"})

print(" ")

try:
    print("Rights: " + Rights.text)  
except AttributeError: 
    print("Rights: No Rights information included for this item in HST PDB")


#CopyrightNotice = Rights.text
    
#print(CopyrightNotice)
print(" ")
#### Credit Statement #####

Credit = "Harry S. Truman Library"

print("Credit: "+Credit)
print(" ")
#### Writer-Editor Statement #####

WriterEditor = "LAA"

print("Writer-Editor :" + WriterEditor)
print(" ")

By_line = "Photographers name goes here "
Source = " Name of collection goes here "
#By-lineTitle = 'Name of Institutional Creator goes here'

#Date = "2023-07-04"

with exiftool.ExifTool() as et:
    et.execute(b"-Headline=" + Headline.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Credit=" + Credit.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-SpecialInstructions=" + SpecialInstructions.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-ObjectName=" + ObjectName.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Caption-Abstract=" + CaptionAbstract.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Writer-Editor=" + WriterEditor.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-By-line=" + By_line.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Source=" + Source.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-ReleaseDate=" + Date.encode('utf-8'), filename.encode('utf-8'))
'''
    et.execute(b"-By-lineTitle=" + By-lineTitle.encode('utf-8'), filename.encode('utf-8'))


    et.execute(b"-Source=" + Source.encode('utf-8'), filename.encode('utf-8'))

'''
print("Processing complete!!!")


