from PIL import Image
import matplotlib.pyplot as plt
import tkinter as tk
import piexif

def display_image_with_exif():
    # Open the image
    image = Image.open('59-783.tif')

    # Create the GUI window
    root = tk.Tk()

    # Create a frame to hold the image
    image_frame = tk.Frame(root)
    image_frame.pack(side=tk.LEFT)

    # Display the image
    plt.imshow(image)
    plt.axis('off')

    # Get the EXIF information
    exif_info = piexif.load(image.info["exif"])
    exif_text = ""
    for ifd in ("0th", "Exif", "GPS", "Interop", "1st"):
        for tag in exif_info.get(ifd, {}):
            tag_name = piexif.TAGS[ifd].get(tag, tag)
            tag_value = exif_info[ifd][tag]
            exif_text += f"{tag_name}: {tag_value}\n"

    # Create a label to show the EXIF information
    exif_label = tk.Label(root, text=exif_text)
    exif_label.pack(side=tk.RIGHT)

    # Show the GUI
    root.mainloop()

# Call the function to display the image with EXIF information
display_image_with_exif()

