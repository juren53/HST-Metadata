from PIL import Image
import matplotlib.pyplot as plt

# Open the image
image = Image.open('59-783.tif')

# Display the image
plt.imshow(image)
plt.show()

