#!/usr/bin/python3
# recent-7.py
#--------------------------------------------
# a Python script that lists the most recent files added or updated in the $HOME directory 
#   
# Wed 24 Jul 2024 12:24:22 PM CDT  Created v 0.01  
# Wed 24 Jul 2024 13:55:11 PM CDT  added code to print filename/path in blue v 0.03
# Wed 24 Jul 2024 15:24:25 PM CDT  added the excluded directory list v 0.04
# Thu 25 Jul 2024 02:33:11 AM CDT  added the date column alignment & no files variable v 0.05
# Mon 29 Jul 2024 09:49:24 AM CDT  modified to read excluded files from excluded_dirs.txt file v 0.06
# Wed 31 Jul 2024 07:34:45 PM CDT  added -n argparse swtich to adjust number of files to list v 0.07
# 
#-------------------------------------------- 


import os
import glob
from datetime import datetime
import argparse

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the current working directory to the script's directory
os.chdir(script_dir)

# Function to read excluded directories from a file
def read_excluded_dirs_from_file(filename):
    exclude_dirs = []
    try:
        with open(filename, 'r') as file:
            exclude_dirs = [line.strip() for line in file]
    except FileNotFoundError:
        print(f"The file '{filename}' does not exist.")
    return exclude_dirs

# Read excluded directories from the file
exclude_dirs_filename = 'excluded_dirs.txt'
exclude_dirs = read_excluded_dirs_from_file(exclude_dirs_filename)

print("Recent ver 0.07  2024-07-31 1935")

# Create the parser
parser = argparse.ArgumentParser(description="A Python script that lists the most recent files added or updated in the $HOME directory.")

# Add the arguments
parser.add_argument('-v', '--version', action='version', version='recent ver 0.07  2024-07-31 1935')
parser.add_argument('-l', '--list', action='store_true', help='list excluded directories')
parser.add_argument('-n', type=int, dest='num', help='Specify the number of files to list [default=15].', default=15)

# Parse the arguments
args = parser.parse_args()

# Update the global num variable based on the command-line argument
num = args.num

# Check if the '-l' switch was used
if args.list:
    # Print the excluded directories
    print("\n".join(exclude_dirs))
    print("\nHere is text for the context:\n")

def list_recent_files(home_dir, num_files=num):
    # Find all files recursively in the home directory
    all_files_pattern = os.path.join(home_dir, '**/*')
    all_files = glob.glob(all_files_pattern, recursive=True)
    
    # Filter out directories and files within the excluded directories
    files_only = [f for f in all_files if os.path.isfile(f) and not any(exclude_dir in f for exclude_dir in exclude_dirs)]
    
    # Sort files by last modification time, most recent first
    sorted_files = sorted(files_only, key=os.path.getmtime, reverse=True)
    
    # Determine the length of the longest file path among the most recent files
    max_path_length = max(len(f) for f in sorted_files[:num_files])
    
    # Print the most recent files with aligned date information
    print("Most recent "+str(num)+" files:"+home_dir)
    for file_path in sorted_files[:num_files]:
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        # Calculate padding for alignment
        padding = max_path_length - len(file_path)
        # Print the entire file path in blue, followed by aligned date information
        print(f"\033[1m{file_path}\033[0m{' ' * padding} {mod_time}")

if __name__ == "__main__":
    home_dir = os.path.expanduser('~')  # Get current user's home directory
    list_recent_files(home_dir)

