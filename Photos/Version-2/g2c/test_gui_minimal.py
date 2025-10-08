#!/usr/bin/env python3

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test G2C GUI")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        label = QLabel("Test GUI - If you see this, the basic GUI works!")
        layout.addWidget(label)

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    
    print("Creating window...")
    window = TestWindow()
    
    print("Showing window...")
    window.show()
    
    print("Starting event loop...")
    # Use exec_() instead of exec() for older PyQt5 versions
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
