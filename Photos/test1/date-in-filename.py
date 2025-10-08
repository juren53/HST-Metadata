import datetime

# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create a new file with the formatted date and time in the filename
filename = f"REPORT_{formatted_datetime}.txt"

with open(filename, "w") as file:
    file.write("This is a new file created at: " + str(current_datetime))
    
print(f"New file '{filename}' created.")
