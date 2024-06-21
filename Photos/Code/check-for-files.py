import os

os.system('cls')

def check_files_exist(*files):
    current_directory = os.getcwd()
    non_existing_files = []
    for file in files:
        if not os.path.exists(os.path.join(current_directory, file)):
            non_existing_files.append(file)

    if non_existing_files:
        print("The following file(s) do not exist in the current directory:")
        for file in non_existing_files:
            print(f"- {file}")
    else:
        print("All files exist in the current directory. You are good to proceed to the next step.")

# Files to check
files_to_check = ['write-tags-from-csv.py', 'menu.py','replace_headers.py','check-for-files.py','check-dates-from-csv.py']

# Check if files exist
check_files_exist(*files_to_check)
