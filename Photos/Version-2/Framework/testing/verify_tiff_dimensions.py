import sys
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

        print(f"Analyzing: {image_path}")
        print(f"  Actual Dimensions (PIL): {actual_width}x{actual_height}")
        print(f"  EXIF Dimensions (ExifTool): {exif_width}x{exif_height}")

        if actual_width == exif_width and actual_height == exif_height:
            print("  Dimensions match.")
        else:
            print("  Dimensions do NOT match.")

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_tiff_dimensions.py <path_to_tiff_image>")
        sys.exit(1)

    image_file = sys.argv[1]
    verify_dimensions(image_file)
