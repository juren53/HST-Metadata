#!/usr/bin/env python3
"""
HSTL Photo Framework - PyQt6 GUI Application

Main entry point for the graphical user interface version of the HSTL Photo Framework.
Provides a comprehensive visual interface for managing photo metadata processing workflows.

Version: 0.1.5b
Commit Date: 2026-01-12 22:18 CST

Usage:
    python hstl_gui.py
"""

import sys
import warnings
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QLockFile, QDir

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent.parent
sys.path.insert(0, str(framework_dir))

from gui.main_window import MainWindow
from gui.theme_manager import ThemeManager
from gui.zoom_manager import ZoomManager

# Version information
__version__ = "0.1.5b"
__commit_date__ = "2026-01-12 22:18 CST"


def main():
    """Main entry point for the GUI application."""
    # Configure Python warnings to be logged instead of printed to console
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger('py.warnings')
    warnings_logger.setLevel(logging.WARNING)
    
    # Set up file handler for warnings (append mode)
    log_dir = Path.home() / '.hstl_photo_framework' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'warnings.log'
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    warnings_logger.addHandler(file_handler)
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("HSTL Photo Framework")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("HSTL")

    # Initialize and apply theme
    theme_mgr = ThemeManager.instance()
    theme_mgr.apply_saved_theme(app)

    # Initialize zoom manager with base font
    zoom_mgr = ZoomManager.instance()
    zoom_mgr.initialize_base_font(app)

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
