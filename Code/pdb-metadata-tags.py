#!/usr/bin/python3
#-----------------------------------------------------------
#  Extracts metadata from HST Photo Database for the AN 
#  provided as the first argument on the command line.
#  Example: python(3) pdb-metadata-2.py 72-3113
#  Note: The file 72-3113.tif needs to bin the current directory
#  Created  Wed 27 Nov 2019 03:58:49 PM CST	
#  Updated	Mon 26 Jun 2023 09:44:14 PM CDT  added section 
#         embed IPTC tags to the corresponding TIFF file													 
#-----------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import sys
import dateparser
import datetime
import re
import exiftool

# et = exiftool.ExifTool()

#accno = "72-3113"   # - entry with three element date
#accno = "95-22-87"  # - entry with two element date
#accno = "2009-1504" # - entry with single element date
#accno = "2006-487"  # - entry with no date 
#accno = "80-16"     # - entry with no date or rights statement

ObjectName = sys.argv[1]

filename = ObjectName + ".tif"

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
    D2 = datetime.datetime(D2.year, D2.month, D2.day)

    D2 = datetime.datetime(D2.year, D2.month, D2.day)
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

with exiftool.ExifTool() as et:
    et.execute(b"-Headline=" + Headline.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Credit=" + Credit.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-SpecialInstructions=" + SpecialInstructions.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-ObjectName=" + ObjectName.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Caption-Abstract=" + CaptionAbstract.encode('utf-8'), filename.encode('utf-8'))
    et.execute(b"-Writer-Editor=" + WriterEditor.encode('utf-8'), filename.encode('utf-8'))
'''
    et.execute(b"-By-line=" + By_line.encode('utf-8'), filename.encode('utf-8'))


    et.execute(b"-Source=" + Source.encode('utf-8'), filename.encode('utf-8'))

'''
print("Processing complete!!!")


