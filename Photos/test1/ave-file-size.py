import os

directory = '.'
files = os.listdir(directory)
total_size = 0
for file in files:
    file_path = os.path.join(directory, file)
    file_size = os.stat(file_path).st_size
    total_size += file_size
average_size = int(total_size / 1024 / 1024)
print(f"Average file size: {average_size} MB")
