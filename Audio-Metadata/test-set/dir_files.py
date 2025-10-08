import os

# Get the current working directory
current_dir = os.getcwd()

# Initialize an empty list to store MP3 files
mp3_files = []

# Iterate through all files in the current directory
for filename in os.listdir(current_dir):
    # Check if the file is an MP3 file
    if filename.endswith(".mp3"):
        mp3_files.append(filename)

# Print the list of MP3 files
print("List of MP3 files in the current directory:")
for file in mp3_files:
    print(file)

