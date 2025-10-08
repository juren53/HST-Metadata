import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
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
        image_label.setAlignment(Qt.AlignCenter)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)

        # Set the scroll area as the central widget
        self.setCentralWidget(scroll_area)

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the application
sys.exit(app.exec_())

