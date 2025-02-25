#!/usr/bin/python3
#--------------------- install-files.py --------- Wed 25 Oct 2023 08:31:49 AM CDT ----------------
# This code installs Python files from GitHub used in the HST Metadata Tagging Project
# to a local working directory where the tagging process ocurrs.
#
# Created Tue 24 Oct 2023 08:31:49 AM CDT by JAU
# Modified Wed 25 Oct 2023 11:15:49 AM CDT - - handles files in multiple URLs
#-------------------------------------------------------------------------------------


import requests
import os

# Define your list of GitHub raw file URLs
file_urls = [
    "https://github.com/juren53/HST-Metadata/raw/master/Photos/Code/write-tags-from-csv.py",
    "https://github.com/juren53/HST-Metadata/raw/master/Photos/Code/check-dates-from-csv.py",	
    "https://github.com/juren53/HST-Metadata/raw/master/Photos/Code/menu.py",
    "https://github.com/juren53/HST-Metadata/raw/master/Photos/Code/menu.bat",
    "https://github.com/juren53/HST-Metadata/raw/master/Photos/Code/replace_headers.py",
    "https://github.com/juren53/HST-Metadata/raw/master/Photos/Code/check-for-files.py",


    # Add more file URLs as needed
]

# Local directory to save the downloaded files
local_directory = "C:\\Temp\\Metadata-tagging"

# Create the local directory if it doesn't exist
if not os.path.exists(local_directory):
    os.makedirs(local_directory)

for url in file_urls:
    # Extract the filename from the URL
    file_name = os.path.basename(url)

    # Create the local file path by joining the local directory and the file name
    local_file_path = os.path.join(local_directory, file_name)

    # Make a GET request to download the file
    response = requests.get(url)

    if response.status_code == 200:
        # Write the content to the local file using binary mode ('wb')
        with open(local_file_path, "wb") as local_file:
            local_file.write(response.content)
        print(f"File {file_name} downloaded successfully.")
    else:
        print(f"Failed to download {url}. Status code: {response.status_code}")
