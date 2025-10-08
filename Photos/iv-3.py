from PIL import Image
import matplotlib.pyplot as plt

# Open the image
image = Image.open('72-3113.jpg')

# Display the image in grayscale
plt.imshow(image, cmap='gray')
plt.show()
