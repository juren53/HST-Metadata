#!/usr/bin/python
# menu.py
#----------------------------------------------------------------------------
#    Front End Menu for HST-Metadata Tagging Process
#    Updated:  Sun 22 Oct 2023 09:55:51 AM CDT 
#----------------------------------------------------------------------------

import subprocess
import os

os.system('cls')
print("  HST Metadata Tagging Process")
ans = True

while ans:
    print ("""  
    1. Install Python Files
    2. Check for valid dates
    3. Tag TIFF or JPEG files
    4. Move Processed TIFF and JPEG files to S: drive
	5. Quit 
    """)

    ans = input("What would you like to do? ")

    if ans == "1":
        subprocess.call("python3 ", shell=True)
    elif ans == "2":
        subprocess.call("python check-dates-from-csv.py | more", shell=True)
    elif ans == "3":
        subprocess.call("python write-tags-from-csv.py", shell=True)
    elif ans == "5":
        quit()
    else:
        print("\n Not Valid Choice. Try again")
