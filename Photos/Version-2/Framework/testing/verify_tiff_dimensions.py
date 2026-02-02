import sys
import os
import argparse
from PIL import Image
from exiftool import ExifToolHelper

def verify_dimensions(image_path):
    """
    This programs checks the acutal data i.e. pixel counts, against 
    EXIF metadata in TIFF images.  

       e.g. EXIF data from ExifTool - not actual data - metadata
       Image Width   : 3678
       Image Height  : 4431

    Args:
        image_path (str): The path to the TIFF image file.
    """
    try:
        # Get actual dimensions using Pillow
        with Image.open(image_path) as img:
            actual_width, actual_height = img.size

        # Get EXIF dimensions using pyexiftool
        with ExifToolHelper() as et:
            metadata = et.get_metadata(image_path)
            if metadata:
                exif_width = metadata[0].get('EXIF:ImageWidth')
                exif_height = metadata[0].get('EXIF:ImageHeight')
            else:
                exif_width, exif_height = None, None

        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        print(f"Analyzing: {image_path}")
        print(f"  {'Actual Dimensions (PIL):':<28} {actual_width:<4}x{actual_height:<4}")
        print(f"  {'EXIF Dimensions (ExifTool):':<28} {exif_width:<4}x{exif_height:<4}")

        if actual_width == exif_width and actual_height == exif_height:
            print(f"  {GREEN}Dimensions match.{RESET}")
        else:
            print(f"  {RED}Dimensions do NOT match.{RESET}")

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
        print(f"An error occurred with {image_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify TIFF image dimensions against EXIF metadata.")
    parser.add_argument("path", nargs="?", help="Path to a single TIFF image file or a directory containing TIFF images.")

    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        sys.exit(1)

    if os.path.isfile(args.path):
        if args.path.lower().endswith(('.tif', '.tiff')):
            verify_dimensions(args.path)
        else:
            print(f"Error: '{args.path}' is not a TIFF image file.")
            sys.exit(1)
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.lower().endswith(('.tif', '.tiff')):
                    image_path = os.path.join(root, file)
                    verify_dimensions(image_path)
    else:
        print(f"Error: '{args.path}' is not a valid file or directory.")
        sys.exit(1)
