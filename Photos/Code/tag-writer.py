#!/usr/bin/python3
#-----------------------------------------------------------
# ############   tag-writer.py  ver 0.07  ################
# This program creates a GUI interface for entering and    
# writing IPTC metadata tags to TIF and JPG images selected   
# from a directory pick list using the tkinter libraries.
# This program is intended as a free form metadata tagger
# when metada can not be pulled from an online database. 
#  Created Sat 01 Jul 2023 07:37:56 AM CDT   [IPTC]
#  Updated Sun 02 Jul 2023 04:53:41 PM CDT added no-backup
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT Updated to use execute_json() for robust metadata retrieval
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT added read existing metadata from file for editing 
#  Updated Sun 30 Mar 2023 03:20:00 AM CDT added command-line argument support & status msg after write
#-----------------------------------------------------------

import tkinter as tk
from tkinter import filedialog
from tkinter import Menu
import exiftool
import argparse
import os
import sys
import io
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Try to import PIL/Pillow components with fallback options
PIL_AVAILABLE = False
IMAGETK_AVAILABLE = False
try:
    from PIL import Image
    PIL_AVAILABLE = True
    try:
        from PIL import ImageTk
        IMAGETK_AVAILABLE = True
    except ImportError:
        logging.warning("ImageTk not available - thumbnail display will be disabled")
except ImportError:
    logging.warning("PIL/Pillow not available - image handling functionality will be limited")

def select_file(file_path=None):
    global selected_file, filename_label
    if file_path:
        if os.path.isfile(file_path):
            selected_file = file_path
            # Update the filename label if it exists
            if 'filename_label' in globals() and filename_label:
                filename_label.config(text=f"File: {os.path.basename(selected_file)}")
            read_metadata()  # Read metadata after selecting the file
            update_thumbnail()  # Update the thumbnail display
        else:
            print(f"Error: The file '{file_path}' does not exist or is not accessible.")
            sys.exit(1)
    else:
        selected_file = filedialog.askopenfilename(title="Select")
        if selected_file:  # Only update if a file was actually selected
            # Update the filename label if it exists
            if 'filename_label' in globals() and filename_label:
                filename_label.config(text=f"File: {os.path.basename(selected_file)}")
            read_metadata()  # Read metadata after selecting the file
            update_thumbnail()  # Update the thumbnail display

def get_metadata(file_path):
    """Retrieve metadata from the specified file using execute_json() method."""
    with exiftool.ExifTool() as et:
        # Use execute_json to get metadata in JSON format
        metadata_json = et.execute_json("-j", file_path)
        
        # metadata_json returns a list of dictionaries, with one dict per file
        # Since we're only processing one file, we take the first element
        if metadata_json and len(metadata_json) > 0:
            return metadata_json[0]
        else:
            return {}

def read_metadata():
    if not selected_file:
        print("No file selected!")
        return

    metadata = get_metadata(selected_file)  # Use the new get_metadata function
    
    # Define a helper function to safely get metadata values
    def safe_get(metadata, key, default=''):
        """Safely retrieve a value from metadata with a default if not found."""
        # Try several possible prefixes for IPTC metadata
        possible_keys = [
            f'IPTC:{key}',  # Standard IPTC prefix
            key,            # Direct key
            f'XMP:{key}',   # XMP prefix
            f'EXIF:{key}'   # EXIF prefix
        ]
        
        for possible_key in possible_keys:
            if possible_key in metadata:
                value = metadata[possible_key]
                # Convert to string if not already
                if value is None:
                    return default
                return str(value)
        
        return default

    # Populate the entry fields with existing metadata
    entry_headline.delete(0, tk.END)
    entry_headline.insert(0, safe_get(metadata, 'Headline'))
    
    entry_credit.delete(0, tk.END)
    entry_credit.insert(0, safe_get(metadata, 'Credit'))
    
    entry_object_name.delete(0, tk.END)
    entry_object_name.insert(0, safe_get(metadata, 'ObjectName'))
    
    entry_caption_abstract.delete(0, tk.END)
    entry_caption_abstract.insert(0, safe_get(metadata, 'Caption-Abstract'))
    
    entry_writer_editor.delete(0, tk.END)
    entry_writer_editor.insert(0, safe_get(metadata, 'Writer-Editor'))
    
    entry_by_line.delete(0, tk.END)
    entry_by_line.insert(0, safe_get(metadata, 'By-line'))
    
    entry_source.delete(0, tk.END)
    entry_source.insert(0, safe_get(metadata, 'Source'))
    
    entry_date.delete(0, tk.END)
    entry_date.insert(0, safe_get(metadata, 'DateCreated'))
def write_metadata():
    global status_label
    if not selected_file:
        print("No file selected!")
        status_label.config(text="Error: No file selected!", fg="red")
        return

    Headline = entry_headline.get()
    Credit = entry_credit.get()
    ObjectName = entry_object_name.get()
    CaptionAbstract = entry_caption_abstract.get()
    WriterEditor = entry_writer_editor.get()
    By_line = entry_by_line.get()
    Source = entry_source.get()
    Date = entry_date.get()

    with exiftool.ExifTool() as et:
        # Set the save_backup parameter to False
        et.save_backup = False

        et.execute(b"-Headline=" + Headline.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Credit=" + Credit.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-ObjectName=" + ObjectName.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Caption-Abstract=" + CaptionAbstract.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Writer-Editor=" + WriterEditor.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-By-line=" + By_line.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Source=" + Source.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-DateCreated=" + Date.encode('utf-8'), selected_file.encode('utf-8'))

    print("Metadata written successfully!")
    status_label.config(text="Metadata written successfully!", fg="green")

def update_version_label_position(event=None):
    """Update the position of the version label to stay in the bottom right corner."""
    global version_label, root
    # Place the label at bottom right with a small margin
    version_label.place(x=root.winfo_width() - version_label.winfo_reqwidth() - 5, 
                       y=root.winfo_height() - version_label.winfo_reqheight() - 5)

def update_thumbnail():
    """Load the selected image file and display it as a thumbnail with robust error handling."""
    global selected_file, thumbnail_label, thumbnail_image
    
    logging.debug("=== THUMBNAIL DEBUGGING START ===")
    logging.debug(f"Update thumbnail called for file: {selected_file}")
    
    # Clear previous thumbnail
    if 'thumbnail_label' in globals() and thumbnail_label:
        logging.debug("Clearing previous thumbnail")
        thumbnail_label.config(image='')
    else:
        logging.debug("No thumbnail_label found in globals")
    
    # If no file is selected, show appropriate message and return early
    if not selected_file:
        logging.debug("No file selected, aborting thumbnail update")
        if 'thumbnail_label' in globals() and thumbnail_label:
            thumbnail_label.config(text="No image to display", image='')
        return
    
    # If PIL is not available, show appropriate message and return early
    if not PIL_AVAILABLE:
        logging.debug("PIL/Pillow not available, cannot proceed with thumbnail creation")
        if 'thumbnail_label' in globals() and thumbnail_label:
            thumbnail_label.config(text="Image preview not available\n(PIL/Pillow library not installed)", image='')
        return
    
    try:
        # Try to determine if the file is an image without opening it
        file_ext = os.path.splitext(selected_file)[1].lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp']
        
        logging.debug(f"Checking file extension: {file_ext}")
        if file_ext not in image_extensions:
            logging.debug(f"File extension {file_ext} not recognized as an image type")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Not an image file\nFile type: {file_ext}", image='')
            return
        
        # Try to open the image
        try:
            logging.debug(f"Attempting to open image file: {selected_file}")
            img = Image.open(selected_file)
            # Print image info for debugging
            original_width, original_height = img.size
            img_format = img.format
            img_mode = img.mode
            
            logging.debug(f"Image successfully opened: {img_format} format, {img_mode} mode")
            logging.debug(f"Original dimensions: {original_width}x{original_height} pixels")
            
            # Also print to console for immediate feedback
            print(f"DEBUG: Loaded image: {os.path.basename(selected_file)}")
            print(f"DEBUG: Format: {img_format}, Mode: {img_mode}, Size: {original_width}x{original_height}")
        except Exception as e:
            logging.error(f"Error opening image: {str(e)}")
            print(f"ERROR: Failed to open image: {str(e)}")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Cannot open image:\n{str(e)[:30]}...", image='')
            return
        
        # Calculate new dimensions while maintaining aspect ratio
        max_size = (200, 200)
        logging.debug(f"Resizing image to maximum dimensions: {max_size}")
        
        # Store original image for comparison
        original_img = img.copy()
        
        try:
            # LANCZOS was introduced in Pillow 9.1.0, use ANTIALIAS for older versions as fallback
            try:
                logging.debug("Attempting to resize using LANCZOS filter")
                img.thumbnail(max_size, Image.LANCZOS)
                logging.debug("Successfully resized using LANCZOS")
            except AttributeError as e:
                logging.debug(f"LANCZOS not available: {str(e)}, trying ANTIALIAS")
                try:
                    img.thumbnail(max_size, Image.ANTIALIAS)
                    logging.debug("Successfully resized using ANTIALIAS")
                except AttributeError as e2:
                    logging.debug(f"ANTIALIAS not available: {str(e2)}, using default method")
                    # If neither is available, use the default method
                    img.thumbnail(max_size)
                    logging.debug("Successfully resized using default method")
            
            # Log the new dimensions
            new_width, new_height = img.size
            logging.debug(f"Resized dimensions: {new_width}x{new_height} pixels")
            print(f"DEBUG: Resized to: {new_width}x{new_height}")
        except Exception as e:
            logging.error(f"Error resizing image: {str(e)}")
            print(f"ERROR: Failed to resize image: {str(e)}")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Cannot resize image:\n{str(e)[:30]}...", image='')
            return
        
        # Check if ImageTk is available before trying to create PhotoImage
        if not IMAGETK_AVAILABLE:
            logging.debug("ImageTk not available, cannot create PhotoImage")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text="ImageTk not available\nCannot display preview", image='')
                thumbnail_label.config(bg="light gray")  # Visual indicator
            return
            
        # Try to convert to PhotoImage for tkinter display
        try:
            logging.debug("Creating PhotoImage from resized image")
            photo_img = ImageTk.PhotoImage(img)
            logging.debug(f"PhotoImage created successfully, dimensions: {photo_img.width()}x{photo_img.height()}")
            print(f"DEBUG: PhotoImage created: {photo_img.width()}x{photo_img.height()}")
            
            # Check if the PhotoImage dimensions match the resized image
            if photo_img.width() != new_width or photo_img.height() != new_height:
                logging.warning(f"PhotoImage dimensions ({photo_img.width()}x{photo_img.height()}) don't match resized image ({new_width}x{new_height})")
            
            thumbnail_image = photo_img  # Store reference to prevent garbage collection
            logging.debug("Reference to PhotoImage stored in thumbnail_image global variable")
            
            # Update the thumbnail display
            if 'thumbnail_label' in globals() and thumbnail_label:
                logging.debug("Updating thumbnail_label with the new image")
                # Configure the label with the new image and ensure it fills the available space
                thumbnail_label.config(image=thumbnail_image, text="", width=photo_img.width(), height=photo_img.height())
                # Force the thumbnail_label to maintain the image's size
                thumbnail_label.image = thumbnail_image  # Keep a reference to prevent garbage collection
                logging.debug("Successfully updated thumbnail_label")
                
                # Verify that the label is visible and correctly positioned
                logging.debug(f"thumbnail_label dimensions: {thumbnail_label.winfo_width()}x{thumbnail_label.winfo_height()}")
                logging.debug(f"thumbnail_label visibility: {'visible' if thumbnail_label.winfo_ismapped() else 'not visible'}")
                print(f"DEBUG: Label dimensions: {thumbnail_label.winfo_width()}x{thumbnail_label.winfo_height()}")
                print(f"DEBUG: Label visibility: {'visible' if thumbnail_label.winfo_ismapped() else 'not visible'}")
            else:
                logging.error("thumbnail_label not found or not properly initialized")
        except Exception as e:
            logging.error(f"Error creating PhotoImage: {str(e)}")
            print(f"ERROR: Failed to create PhotoImage: {str(e)}")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Cannot create thumbnail:\n{str(e)[:30]}...", image='')
    except Exception as e:
        # Catch-all for any other errors
        logging.error(f"Unexpected error in thumbnail display: {str(e)}")
        print(f"ERROR: Unexpected error in thumbnail display: {str(e)}")
        if 'thumbnail_label' in globals() and thumbnail_label:
            thumbnail_label.config(text=f"Error displaying preview:\n{str(e)[:30]}...", image='')
    
    logging.debug("=== THUMBNAIL DEBUGGING END ===")
    # Force update the GUI to ensure changes are visible
    if 'root' in globals():
        try:
            root.update_idletasks()
            # Print updated label dimensions for debugging
            if 'thumbnail_label' in globals() and thumbnail_label:
                print(f"DEBUG: After update_idletasks - Label dimensions: {thumbnail_label.winfo_width()}x{thumbnail_label.winfo_height()}")
                print(f"DEBUG: After update_idletasks - Label visibility: {'visible' if thumbnail_label.winfo_ismapped() else 'not visible'}")
            logging.debug("Forced GUI update via update_idletasks()")
        except Exception as e:
            logging.error(f"Error updating GUI: {str(e)}")


def start_gui(initial_file=None):
    global root, entry_headline, entry_caption_abstract, entry_credit, entry_object_name
    global entry_writer_editor, entry_by_line, entry_source, entry_date, selected_file
    global status_label, filename_label, version_label, thumbnail_label, thumbnail_image
    # Create the GUI window
    root = tk.Tk()
    root.title("Metadata Tag Writer")
    
    root.geometry("1000x400")     # sets default window size 
    
    # Add function to exit application when 'q' is pressed
    def quit_app(event=None):
        root.destroy()
    
    # Bind the 'q' key to the quit_app function
    root.bind('<q>', quit_app)
        
    menubar = Menu(root)
    root.config(menu=menubar)
    
    filemenu = Menu(menubar)
    menubar.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Open")
    filemenu.add_command(label="Save")
    filemenu.add_command(label="Exit", command=quit_app)
    selected_file = None
    
    # Create select file button
    button_select_file = tk.Button(root, text="Select File", command=select_file)
    button_select_file.grid(row=0, column=0)
    
    # Create write button
    button_write = tk.Button(root, text="Write Metadata", command=write_metadata)
    button_write.grid(row=0, column=1)
    
    # Create filename display label
    filename_label = tk.Label(root, text="No file selected", font=("Arial", 10, "bold"))
    filename_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    # Create input fields
    entry_headline = tk.Entry(root, width=60)
    entry_caption_abstract = tk.Entry(root, width=60)
    entry_credit = tk.Entry(root)
    entry_object_name = tk.Entry(root)
    entry_writer_editor = tk.Entry(root)
    entry_by_line = tk.Entry(root)
    entry_source = tk.Entry(root)
    entry_date = tk.Entry(root)
    
    # Create labels
    label_headline = tk.Label(root, justify="left", text="Headline:")
    label_caption_abstract = tk.Label(root, text="Caption Abstract:")
    label_credit = tk.Label(root, text="Credit:")
    label_object_name = tk.Label(root, text="Unique ID [Object Name]: ")
    label_writer_editor = tk.Label(root, text="Writer Editor:")
    label_by_line = tk.Label(root, text="By-line [photographer]:")
    label_source = tk.Label(root, text="Source:")
    label_date = tk.Label(root, text="Date Created [YYY-MM-DD]:")
    
    # Grid layout
    label_headline.grid(row=2, column=0, sticky="w")
    entry_headline.grid(row=2, column=1, sticky="w")
    
    label_credit.grid(row=3, column=0, sticky="w")
    entry_credit.grid(row=3, column=1, sticky="w")
    
    label_object_name.grid(row=4, column=0, sticky="w")
    entry_object_name.grid(row=4, column=1, sticky="w")
    
    label_caption_abstract.grid(row=5, column=0, sticky="w")
    entry_caption_abstract.grid(row=5, column=1, sticky="w")
    
    label_writer_editor.grid(row=6, column=0, sticky="w")
    entry_writer_editor.grid(row=6, column=1, sticky="w")
    
    label_by_line.grid(row=7, column=0, sticky="w")
    entry_by_line.grid(row=7, column=1, sticky="w")
    
    label_source.grid(row=8, column=0, sticky="w")
    entry_source.grid(row=8, column=1, sticky="w")
    
    label_date.grid(row=9, column=0, sticky="w")
    entry_date.grid(row=9, column=1, sticky="w")
    
    # Status message label
    status_label = tk.Label(root, text="", fg="green")
    status_label.grid(row=10, columnspan=2, sticky="w")
    
    # Create and configure the thumbnail display area
    # Create a frame with fixed size for thumbnail display
    thumbnail_frame = tk.Frame(root, width=220, height=220, relief=tk.SUNKEN, borderwidth=1)
    thumbnail_frame.grid(row=2, column=2, rowspan=8, padx=10, pady=5, sticky="ne")
    # Prevent the frame from shrinking to fit its contents
    thumbnail_frame.grid_propagate(False)
    # Make sure the frame expands within its cell
    thumbnail_frame.columnconfigure(0, weight=1)
    thumbnail_frame.rowconfigure(0, weight=1)
    
    # Place holder for thumbnail image
    thumbnail_image = None
    
    # Adjust the thumbnail label based on PIL/ImageTk availability
    if PIL_AVAILABLE and IMAGETK_AVAILABLE:
        thumbnail_status = "No image to display"
    elif PIL_AVAILABLE and not IMAGETK_AVAILABLE:
        thumbnail_status = "ImageTk not available\nCannot display thumbnails"
    else:
        thumbnail_status = "PIL/Pillow not available\nCannot display thumbnails"
    
    logging.debug(f"Creating thumbnail_label with status: {thumbnail_status}")
    # Create label with appropriate minimal size to display a 200x157 image
    thumbnail_label = tk.Label(thumbnail_frame, text=thumbnail_status, 
                              width=200, height=157,  # Set minimum width/height in pixels
                              compound=tk.TOP,  # Position image at the top, text below
                              anchor=tk.CENTER,  # Center the content
                              relief=tk.FLAT,
                              padx=5, pady=5)  # Add padding inside the label
    
    # Position the label to fill the entire frame
    thumbnail_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    # Log information about the thumbnail label
    logging.debug(f"thumbnail_label created with initial dimensions: {thumbnail_label.winfo_reqwidth()}x{thumbnail_label.winfo_reqheight()}")
    print(f"DEBUG: Thumbnail label created with dimensions: {thumbnail_label.winfo_reqwidth()}x{thumbnail_label.winfo_reqheight()}")
    
    # Add indicator about PIL status
    if not PIL_AVAILABLE or not IMAGETK_AVAILABLE:
        status_frame = tk.Frame(thumbnail_frame)
        status_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        
        # Use Unicode symbols for indicators
        status_icon = "⚠️" if not PIL_AVAILABLE else "ℹ️"
        status_text = "PIL missing" if not PIL_AVAILABLE else "ImageTk missing"
        
        status_indicator = tk.Label(status_frame, text=f"{status_icon} {status_text}", 
                                   fg="red" if not PIL_AVAILABLE else "orange",
                                   font=("Arial", 8))
        status_indicator.grid(row=0, column=0, pady=2)
    
    # Create version label that will be positioned dynamically
    version_text = "tag-writer.py   ver .07  2025-03-30   "
    # Add PIL status to version label
    if not PIL_AVAILABLE:
        version_text += " [PIL missing]"
    elif not IMAGETK_AVAILABLE:
        version_text += " [ImageTk missing]"
    
    version_label = tk.Label(root, text=version_text, bg="lightgray")
    
    # Bind resize event to update the version label position
    root.bind("<Configure>", update_version_label_position)
    
    # If an initial file was provided, select it
    if initial_file:
        select_file(initial_file)
    else:
        filename_label.config(text="No file selected")
    
    # Call once to position the version label after window is fully created
    # We use after() to ensure the window is fully rendered
    root.update_idletasks()
    root.after(100, update_version_label_position)
    
    # Initialize the thumbnail display if a file is selected
    if initial_file:
        update_thumbnail()
    
    root.mainloop()

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Metadata Tag Writer for TIF and JPG images")
    parser.add_argument("file_path", nargs="?", help="Path to the image file to process")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information and exit")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Handle version flag
    # Handle version flag
    if args.version:
        version_text = "tag-writer.py  version .07  (2025-03-30)"
        
        # Add PIL/ImageTk status to version output
        if not PIL_AVAILABLE:
            version_text += " [PIL/Pillow not available]"
        elif not IMAGETK_AVAILABLE:
            version_text += " [ImageTk not available]"
        else:
            version_text += " [Full thumbnail support]"
            
        print(version_text)
        sys.exit(0)
    # Handle file path argument
    if args.file_path:
        try:
            # Log PIL/ImageTk availability status
            if not PIL_AVAILABLE:
                logging.warning("Starting without PIL/Pillow support - thumbnail display disabled")
            elif not IMAGETK_AVAILABLE:
                logging.warning("Starting without ImageTk support - thumbnail display disabled")
            else:
                logging.info("Starting with full thumbnail support")
                
            start_gui(args.file_path)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            sys.exit(1)
    else:
        # No arguments provided, start with GUI only
        # Log PIL/ImageTk availability status
        if not PIL_AVAILABLE:
            logging.warning("Starting without PIL/Pillow support - thumbnail display disabled")
        elif not IMAGETK_AVAILABLE:
            logging.warning("Starting without ImageTk support - thumbnail display disabled")
        else:
            logging.info("Starting with full thumbnail support")
            
        start_gui()
