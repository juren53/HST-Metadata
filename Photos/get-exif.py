from PIL import Image
from PIL.ExifTags import TAGS
import sys

# Get the file name from the command line
input = sys.argv[1]


def print_exif_data(exif_data):
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        content = exif_data.get(tag_id)
        print(f'{tag:25}: {content}')

with Image.open(input) as im:
    exif = im.getexif()
    
    print_exif_data(exif)
    print()
    print_exif_data(exif.get_ifd(0x8769))

