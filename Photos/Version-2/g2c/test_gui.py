#!/usr/bin/env python3
"""
Simple PyQt5 test application to debug GUI startup issues
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Test Window")
        self.setGeometry(100, 100, 400, 200)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Labels
        title = QLabel("PyQt5 Test Application")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        status = QLabel("If you can see this, PyQt5 is working correctly!")
        status.setAlignment(Qt.AlignCenter)
        layout.addWidget(status)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        print("✅ Test window initialized successfully")

def main():
    print("🚀 Starting PyQt5 test application...")
    
    # Set environment to avoid conflicts
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    
    app = QApplication(sys.argv)
    print("✅ QApplication created")
    
    window = TestWindow()
    print("✅ Window created")
    
    window.show()
    print("✅ Window shown - GUI should be visible now")
    print("💡 Close the window or press Ctrl+C to exit")
    
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n🛑 Received keyboard interrupt - exiting")
        sys.exit(0)

if __name__ == "__main__":
    main()