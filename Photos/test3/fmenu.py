# In Python3 write a menu routine that asks the user via CLI if the want to process TIFF files or JPEG files and then sets a 'ext' variable of either 'jpg' or 'tif' to be used later in the program.


def file_processing_menu():
    ext = None

    while ext is None:
        print("Menu:")
        print("1. Process TIFF files")
        print("2. Process JPEG files")
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            ext = "tif"
        elif choice == "2":
            ext = "jpg"
        else:
            print("Invalid choice. Please try again.")

    print("File extension set to:", ext)
    # Rest of your code using the 'ext' variable goes here


# Call the menu routine
file_processing_menu()

