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
