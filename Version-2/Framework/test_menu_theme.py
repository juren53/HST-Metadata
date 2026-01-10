#!/usr/bin/env python3
"""Test script to verify menu theme styling."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent
sys.path.insert(0, str(framework_dir))

from gui.theme_manager import ThemeManager, ThemeMode

class ThemeTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu Theme Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager.instance()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create central widget with theme toggle button
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)
        
        self.setCentralWidget(central_widget)
        
        # Apply initial theme
        self.theme_manager.apply_theme(QApplication.instance(), ThemeMode.LIGHT)
    
    def _create_menu_bar(self):
        """Create menu bar for testing."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        new_action = file_menu.addAction("&New")
        open_action = file_menu.addAction("&Open")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("E&xit")
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        cut_action = edit_menu.addAction("Cu&t")
        copy_action = edit_menu.addAction("&Copy")
        paste_action = edit_menu.addAction("&Paste")
        
        # View menu
        view_menu = menubar.addMenu("&View")
        zoom_in_action = view_menu.addAction("Zoom &In")
        zoom_out_action = view_menu.addAction("Zoom &Out")
        view_menu.addSeparator()
        fullscreen_action = view_menu.addAction("&Fullscreen")
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        current_mode = self.theme_manager.current_mode
        if current_mode == ThemeMode.LIGHT:
            new_mode = ThemeMode.DARK
        else:
            new_mode = ThemeMode.LIGHT
        
        self.theme_manager.apply_theme(QApplication.instance(), new_mode)
        
        # Update button text
        mode_text = "Dark" if new_mode == ThemeMode.LIGHT else "Light"
        self.theme_button.setText(f"Switch to {mode_text} Theme")

def main():
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = ThemeTestWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()