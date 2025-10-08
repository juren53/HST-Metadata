import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PIL import Image

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Image Viewer")

        # Load the image
        image = Image.open('59-783.tif')

        # Create QLabel to display the image
        image_label = QLabel(self)
        pixmap = QPixmap.fromImage(image.toqimage())
        image_label.setPixmap(pixmap)

        # Set the size of the main window
        self.resize(pixmap.width(), pixmap.height())

        # Set the image label as the central widget
        self.setCentralWidget(image_label)

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the application
sys.exit(app.exec_())

