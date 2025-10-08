#!/usr/bin/python3
#--------------------- install-files.py --------- Wed 25 Oct 2023 08:31:49 AM CDT ----------------
# This code installs Python files from GitHub used in the HST Metadata Tagging Project
# to a local working directory where the tagging process ocurrs.
#
# Created Wed 25 Oct 2023 08:31:49 AM CDT by JAU
#
#-------------------------------------------------------------------------------------
import requests
import os

# URL of the file you want to download
url = "https://github.com/juren53/HST-Metadata/raw/master/Code/write-tags-from-csv.py"

# Specify the local directory where you want to save the file
local_directory = "/home/juren/Temp"

# Extract the filename from the URL
filename = url.split("/")[-1]

# Create the full path for the local file
local_file_path = os.path.join(local_directory, filename)

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (HTTP status code 200)
if response.status_code == 200:
    # Open the local file and write the downloaded content
    with open(local_file_path, 'wb') as file:
        file.write(response.content)
    print(f"File '{filename}' has been successfully downloaded to '{local_file_path}'")
else:
    print(f"Failed to download the file. HTTP status code: {response.status_code}")
