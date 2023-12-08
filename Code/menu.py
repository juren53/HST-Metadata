#!/usr/bin/python
# menu.py
#----------------------------------------------------------------------------
#    Front End Menu for HST-Metadata Tagging Process
#    Updated:  Sun 22 Oct 2023 09:55:51 AM CDT 
#    Updated:  Sun 29 Oct 2023 13:23:05 PM CDT - added replace_headers.py to menu
#    Updated:  Fri 08 Dec 2023 13:25:15 PM CDT - added python check-for-files.py
#----------------------------------------------------------------------------

import subprocess
import os

os.system('cls')
print("  HST Metadata Tagging Process")
ans = True

while ans:
    print ("""  
    1  Check that necessary Python files are installed
    2  Update headers on CSV file 
    3  Check for valid dates
    4  Tag TIFF or JPEG files

    q  Quit 
    """)

    ans = input("  What would you like to do? ")

    if ans == "1":
        subprocess.call("python check-for-files.py ", shell=True)
    elif ans == "2":	
        subprocess.call("python replace_headers.py ", shell=True)
    elif ans == "3":
        subprocess.call("python check-dates-from-csv.py | more", shell=True)
    elif ans == "4":
        subprocess.call("python write-tags-from-csv.py", shell=True)
    elif ans == "q":
        quit()
    else:
        print("     Not Valid Choice. Try again")
