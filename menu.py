# !/usr/bin/python3
# menu.py
#Thu 05 Dec 2019 07:37:11 AM CST 

from tkinter import *
from tkinter import filedialog
import tkinter as tk
import os
import glob
import subprocess as sub


def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def listfiles():
   win = tk.Tk()
   win.title("TIF Files")
   win.geometry("200x200+50+150") # Width x Height + Location (X/Y)
   dir = folder_path.get()
   os.chdir(dir)   
 
   flist = glob.glob('*.tif')
 
   lbox = tk.Listbox(win)
   lbox.pack()

   for item in flist:
       print(item)
       lbox.insert(tk.END, item)

   win.wm_attributes("-topmost", 1) # sets top most window
 
   win.mainloop()

def list_tags():

    root = tk.Tk()
    root.title("IPTC Tags")
    root.geometry("600x400+300+100") # Width x Height + Location (X/Y)
    dir = folder_path.get()
    os.chdir(dir)   
   
    os.system("pwd > dir")
    p = sub.Popen('/home/juren/Projects/HST-Metadata/Code/script',stdout=sub.PIPE,stderr=sub.PIPE)
    #p = os.system("exiftool -iptc:all *.tif")
    output, errors = p.communicate()
 
    text = Text(root)
    text.pack()


    text.insert(END, output)
    root.wm_attributes("-topmost", 1) # sets top most window

    root.mainloop()


def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    global dir
    filename = filedialog.askdirectory()
    folder_path.set(filename)

def exitapp():
	
    sys. exit()

root = Tk()

root.title("HST AV Archives Metadata Tool")

root.geometry("900x600+10+10") # Width x Height + Location (X/Y)

folder_path = StringVar()
lbl1 = Label(master=root,textvariable=folder_path)
lbl1.grid(row=0, column=0)
button2 = Button(text="Select Working Directory", command=browse_button)
button2.grid(row=4, column=0)


menubar = Menu(root)
filemenu = Menu(menubar, tearoff = 0)

menubar.add_cascade(label = "File", menu = filemenu)
filemenu.add_command(label = "Set Working Directory", command = listfiles)
filemenu.add_command(label = "List TIF Files", command = listfiles)
filemenu.add_command(label = "List Tags in Files", command = list_tags)
filemenu.add_command(label = "List Tags from HST PDB", command = donothing)
filemenu.add_command(label = "Write Tags from HST PDB", command = donothing)
filemenu.add_command(label = "Write Photographer, Collection and Editor  Tags", command = donothing)
filemenu.add_command(label = "Save as...", command = donothing)
filemenu.add_command(label = "Close", command = donothing)

filemenu.add_separator()

filemenu.add_command(label = "Exit", command = exitapp)

editmenu = Menu(menubar, tearoff=0)

menubar.add_cascade(label = "Edit", menu = editmenu)
editmenu.add_command(label = "Undo", command = donothing)

editmenu.add_separator()

editmenu.add_command(label = "Cut", command = donothing)
editmenu.add_command(label = "Copy", command = donothing)
editmenu.add_command(label = "Paste", command = donothing)
editmenu.add_command(label = "Delete", command = donothing)
editmenu.add_command(label = "Select All", command = donothing)


viewmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label = "View", menu = viewmenu)
viewmenu.add_command(label = "All Files", command = donothing)
viewmenu.add_command(label = "Single File", command = donothing)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label = "Help Index", command = donothing)
helpmenu.add_command(label = "About...", command = donothing)
menubar.add_cascade(label = "Help", menu = helpmenu)


# display the menu
root.config(menu = menubar)

root.mainloop()
