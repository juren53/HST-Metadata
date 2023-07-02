#!/usr/bin/python3
#-----------------------------------------------------------
# ############   tag-writer.py  v0.3  ################
# THis program creates a GUI interface for entering and    
# writing IPTC metadata tags to TIF and JPG images selected   
# from a directory pick list using the tkinker libraries.
# This program is intended as a free form metadata tagger
# where the photo is not available in the HST PDB
#  Created 	Sat 01 Jul 2023 07:37:56 AM CDT   [IPTC]										 
#-----------------------------------------------------------


import tkinter as tk
from tkinter import filedialog
import exiftool

def select_file():
    global selected_file
    selected_file = filedialog.askopenfilename(title="Select")

def write_metadata():
    if not selected_file:
        print("No file selected!")
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
        et.execute(b"-Headline=" + Headline.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Credit=" + Credit.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-ObjectName=" + ObjectName.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Caption-Abstract=" + CaptionAbstract.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Writer-Editor=" + WriterEditor.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-By-line=" + By_line.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Source=" + Source.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-DateCreated=" + Date.encode('utf-8'), selected_file.encode('utf-8'))

    print("Metadata written successfully!")

# Create the GUI window
root = tk.Tk()
root.title("Image Metadata Writer")

root.geometry("700x500")     # sets default window size 

selected_file = None

# Create select file button
button_select_file = tk.Button(root, text="Select File", command=select_file)
button_select_file.pack()

# Create input fields
#entry_headline = tk.Entry(root)
entry_headline = tk.Entry(root, width=60)
entry_caption_abstract = tk.Entry(root, width=80)
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

# Create write button
button_write = tk.Button(root, text="Write Metadata", command=write_metadata)

# Grid layout
button_write.pack()

label_headline.pack(anchor="w")
entry_headline.pack(anchor="w")

label_credit.pack(anchor="w")
entry_credit.pack(anchor="w")

label_object_name.pack(anchor="w")
entry_object_name.pack(anchor="w")

label_caption_abstract.pack(anchor="w")
entry_caption_abstract.pack(anchor="w")

label_writer_editor.pack(anchor="w")
entry_writer_editor.pack(anchor="w")

label_by_line.pack(anchor="w")
entry_by_line.pack(anchor="w")

label_source.pack(anchor="w")
entry_source.pack(anchor="w")

label_date.pack(anchor="w")
entry_date.pack(anchor="w")

# Create a label widget

label = tk.Label(root, text="tag-writer-3 2023-07-01   ", bg="lightgray")
label.place(relx=1, rely=1, anchor=tk.SE)



root.mainloop()

