#!/usr/bin/env python3
"""
HSTL Photo Framework - PyQt6 GUI Application

Main entry point for the graphical user interface version of the HSTL Photo Framework.
Provides a comprehensive visual interface for managing photo metadata processing workflows.

Version: 0.0.6
Commit Date: 2025-12-12 11:30

Usage:
    python hstl_gui.py
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent.parent
sys.path.insert(0, str(framework_dir))

from gui.main_window import MainWindow

# Version information
__version__ = "0.0.6"
__commit_date__ = "2025-12-12 11:30"


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
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
