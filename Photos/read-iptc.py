#!/usr/bin/python
#---------------------read-iptc.py-------------------------------
#This code reads and display the IPTC data from file indicated
#in the command line  e.g. python read-iptc.py {path/filename}
# 
#This program expands on code posted by bhaskarkc
# https://gist.github.com/bhaskarkc/abcbc4a35229815bd6ce4ab7372748f9 
#
# J. U'Ren added sys argv to allow filename input as an argument
# on the command line
#
#----------------------------------------------------------------
# pip install pillow

from PIL import Image, IptcImagePlugin
import sys

# Get the file name from the command line
input = sys.argv[1]

im = Image.open(input)
iptc = IptcImagePlugin.getiptcinfo(im)

if iptc:
    for k, v in iptc.items():
        print("{} {}".format(k, repr(v.decode())))
else:
    print(" This image has no iptc info")

# We can user getter function to get values
# from specific IIM codes
# https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata
def get_caption():
    return iptc.get((2,120)).decode()

#print(get_caption())
