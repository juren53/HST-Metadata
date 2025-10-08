import os

filename = "85-8-4.jpg"
file_extension = os.path.splitext(filename)[1]
file_name_without_extension = os.path.splitext(filename)[0]

print("File Name:", file_name_without_extension)
print("File Extension:", file_extension)


