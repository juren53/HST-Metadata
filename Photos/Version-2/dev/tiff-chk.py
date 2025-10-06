from PIL import Image
im = Image.open("image.tif")
im.verify()  # Raises an exception if not valid
