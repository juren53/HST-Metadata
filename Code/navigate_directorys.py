import os

def navigate_directory_tree():
    current_directory = os.getcwd()
    print("Current directory:", current_directory)

    while True:
        user_input = input("Enter 'up' to go up a level, 'down' to go down a level, or 'exit' to quit: ").lower()

        if user_input == "up":
            # Navigate up a level by getting the parent directory
            os.chdir(os.path.dirname(current_directory))
            current_directory = os.getcwd()
            print("Current directory:", current_directory)
        elif user_input == "down":
            # List the subdirectories in the current directory
            subdirectories = [name for name in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, name))]
            if not subdirectories:
                print("No subdirectories found.")
                continue

            print("Subdirectories:")
            for index, subdir in enumerate(subdirectories, start=1):
                print(f"{index}. {subdir}")

            # Ask the user to choose a subdirectory
            try:
                choice = int(input("Enter the number of the subdirectory to navigate into: "))
                if 1 <= choice <= len(subdirectories):
                    os.chdir(os.path.join(current_directory, subdirectories[choice - 1]))
                    current_directory = os.getcwd()
                    print("Current directory:", current_directory)
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        elif user_input == "exit":
            print("Exiting directory navigator.")
            break
        else:
            print("Invalid input. Please enter 'up', 'down', or 'exit'.")

if __name__ == "__main__":
    navigate_directory_tree()

