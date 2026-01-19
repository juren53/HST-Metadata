#!/usr/bin/env python3
"""
Test script to preview the Get Latest Updates dialog
without actually checking for updates or modifying versions.

This allows you to see how the dialog looks with different scenarios.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton, QMainWindow
from PyQt6.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from __init__ import __version__


def test_update_available_dialog():
    """Test the 'Update Available' dialog"""
    # Simulate different versions for testing
    current_version = __version__
    remote_version = "0.1.7g"  # Change this to test different versions
    
    version_text = f"Current version: v{current_version}\n" \
                  f"Update available: v{remote_version}\n\n"
    
    reply = QMessageBox.question(
        None,
        "Get Latest Updates",
        f"An update is available.\n\n"
        f"{version_text}"
        "Do you want to download the latest update?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        print("User clicked Yes - would proceed with download")
    else:
        print("User clicked No - cancelled")


def test_already_uptodate_dialog():
    """Test the 'Already Up-to-Date' dialog"""
    QMessageBox.information(
        None,
        "Already Up-to-Date",
        f"You are already up to date with v{__version__}.\n\n"
        "No updates are available at this time.",
    )


def test_uncommitted_changes_dialog():
    """Test the 'Uncommitted Changes' warning dialog"""
    changes_desc = "3 modified, 1 untracked file(s)"
    
    reply = QMessageBox.warning(
        None,
        "Uncommitted Changes Detected",
        f"You have unsaved changes: {changes_desc}\n\n"
        "Downloading the update may cause conflicts with your changes.\n\n"
        "Do you want to continue anyway?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        print("User clicked Yes - would proceed despite changes")
    else:
        print("User clicked No - cancelled due to uncommitted changes")


def test_update_complete_dialog():
    """Test the 'Update Complete' success dialog"""
    files_changed = 5
    stats_text = f"{files_changed} file(s) updated"
    
    QMessageBox.information(
        None,
        "Update Complete",
        f"Successfully downloaded and installed the latest update!\n\n"
        f"{stats_text}\n\n"
        "⚠️ Please restart HPM for changes to take effect.",
    )


def test_update_failed_dialog():
    """Test the 'Update Failed' error dialog"""
    error_message = "Network connection timeout"
    
    QMessageBox.critical(
        None,
        "Update Failed",
        f"Failed to download update from GitHub:\n\n{error_message}\n\n"
        "Please resolve any issues and try again.",
    )


def main():
    """Run all test dialogs"""
    app = QApplication(sys.argv)
    
    # Create a simple window with buttons to test each dialog
    window = QMainWindow()
    window.setWindowTitle("Update Dialog Tester")
    window.setGeometry(100, 100, 400, 300)
    
    # Create central widget with buttons
    from PyQt6.QtWidgets import QWidget, QVBoxLayout
    
    central = QWidget()
    layout = QVBoxLayout(central)
    
    # Add test buttons
    btn1 = QPushButton("Test: Update Available")
    btn1.clicked.connect(test_update_available_dialog)
    layout.addWidget(btn1)
    
    btn2 = QPushButton("Test: Already Up-to-Date")
    btn2.clicked.connect(test_already_uptodate_dialog)
    layout.addWidget(btn2)
    
    btn3 = QPushButton("Test: Uncommitted Changes Warning")
    btn3.clicked.connect(test_uncommitted_changes_dialog)
    layout.addWidget(btn3)
    
    btn4 = QPushButton("Test: Update Complete")
    btn4.clicked.connect(test_update_complete_dialog)
    layout.addWidget(btn4)
    
    btn5 = QPushButton("Test: Update Failed")
    btn5.clicked.connect(test_update_failed_dialog)
    layout.addWidget(btn5)
    
    layout.addStretch()
    
    window.setCentralWidget(central)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
