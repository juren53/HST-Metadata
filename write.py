from PIL import Image
from PIL.ExifTags import TAGS

def set_image_metadata(file_path, title, description):
    image = Image.open(file_path)
    exif_data = {}
    for tag, value in image.getexif().items():
        decoded = TAGS.get(tag, tag)
        exif_data[decoded] = value
    exif_data['ImageDescription'] = description
    exif_data['ImageDescription'] = title
    image.save(file_path, exif=image.info.get('exif') + bytes(
        [(0x02, b'\x1b[1;31mDescription\x00', description.encode('UTF-8')),
         (0x02, b'\x1b[1;31mTitle\x00', title.encode('UTF-8'))]) if image.format == 'JPEG' else None)

# Example usage:
set_image_metadata("example.jpg", "My Title", "This is my image description")


