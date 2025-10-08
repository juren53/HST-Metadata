import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt
from PIL import Image

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Image Viewer")

        # Load the image
        image = Image.open('59-783.tif')
        qimage = QImage(image.tobytes(), image.width, image.height, QImage.Format_RGB888)

        # Create QGraphicsScene and set background color
        scene = QGraphicsScene()
        scene.setBackgroundBrush(Qt.black)

        # Create QGraphicsView to display the image
        view = QGraphicsView(scene)
        view.setRenderHint(QPainter.Antialiasing)
        view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        view.setDragMode(QGraphicsView.ScrollHandDrag)

        # Create QGraphicsPixmapItem to hold the image
        pixmap_item = scene.addPixmap(QPixmap.fromImage(qimage))

        # Set the QGraphicsPixmapItem as the central item in the scene
        scene.setSceneRect(pixmap_item.boundingRect())
        view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

        # Set the QGraphicsView as the central widget
        self.setCentralWidget(view)

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = ImageViewer()
window.show()

# Run the application
sys.exit(app.exec_())

