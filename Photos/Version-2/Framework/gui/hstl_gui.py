#!/usr/bin/env python3
"""
HSTL Photo Framework - PyQt6 GUI Application

Main entry point for the graphical user interface version of the HSTL Photo Framework.
Provides a comprehensive visual interface for managing photo metadata processing workflows.

Version: 0.0.10
Commit Date: 2025-12-14 14:20

Usage:
    python hstl_gui.py
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QLockFile, QDir

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent.parent
sys.path.insert(0, str(framework_dir))

from gui.main_window import MainWindow

# Version information
__version__ = "0.0.10"
__commit_date__ = "2025-12-14 14:20"


def main():
    """Main entry point for the GUI application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("HSTL Photo Framework")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("HSTL")
    
    # Check for single instance using lock file
    lock_file_path = QDir.tempPath() + "/hstl_photo_framework.lock"
    lock_file = QLockFile(lock_file_path)
    
    if not lock_file.tryLock(100):
        # Another instance is already running
        QMessageBox.critical(
            None,
            "Application Already Running",
            "HSTL Photo Framework is already running.\n\n"
            "Only one instance of the application can run at a time.\n\n"
            "Please close the existing instance before starting a new one."
        )
        sys.exit(1)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
