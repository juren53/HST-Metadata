import os
from PIL import Image

def display_images_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.tif') or filename.endswith('.tiff') or filename.endswith('.jpeg') or filename.endswith('.jpg'):
            try:
                image = Image.open(os.path.join(directory, filename))
                image.show()
                image.close()
            except Exception as e:
                print(f"Error opening {filename}: {str(e)}")

# Set the current directory as the working directory
directory = os.getcwd()

# Call the function to display images in the current directory
display_images_in_directory(directory)

