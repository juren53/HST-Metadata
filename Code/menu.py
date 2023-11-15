#!/usr/bin/python
# menu.py
#----------------------------------------------------------------------------
#    Front End Menu for HST-Metadata Tagging Process
#    Updated:  Sun 22 Oct 2023 09:55:51 AM CDT 
#    Updated:  Sun 29 Oct 2023 13:23:05 PM CDT - added replace_headers.py to menu
#    Updated:  Tue 14 Nov 2023 10:15_01 AM CST - added copy-files.bat to "5."
#----------------------------------------------------------------------------

import subprocess
import os

os.system('cls')
print("  HST Metadata Tagging Process   [2023-11-14]")
ans = True

while ans:
    print ("""  
    1. Install Python Files
    2. Create export.csv file 
    3. Check for valid dates
    4. Tag TIFF or JPEG files
    5. Move Processed TIFF and JPEG files to S: drive
    6. Quit 
    """)

    ans = input("What would you like to do? ")

    if ans == "1":
        subprocess.call("python install-files.py ", shell=True)
    elif ans == "2":	
        subprocess.call("python replace_headers.py ", shell=True)
    elif ans == "3":
        subprocess.call("python check-dates-from-csv.py | more", shell=True)
    elif ans == "4":
        subprocess.call("python write-tags-from-csv.py", shell=True)
    elif ans == "5":
        subprocess.call("copy-files.bat", shell=True)	
    elif ans == "6":
        quit()
    else:
        print("\n Not Valid Choice. Try again")
