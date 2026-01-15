"""
Step 1 Dialog - Google Worksheet Preparation

Allows user to enter the Google Worksheet URL and marks Step 1 as complete.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt

from utils.log_manager import get_log_manager


class Step1Dialog(QDialog):
    """Dialog for Step 1: Google Worksheet Preparation."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 1: Google Worksheet Preparation")
        self.setMinimumWidth(600)

        self.log_manager.debug("Opened Step 1 dialog", batch_id=batch_id, step=1)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("<h2>Step 1: Google Worksheet Preparation</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>Enter the URL of the completed Google Worksheet that contains "
            "the metadata for this batch.</p>"
            "<p><b>Requirements:</b></p>"
            "<ul>"
            "<li>The worksheet must be complete with all required fields</li>"
            "<li>Required fields: Title, Description, Accession Number, Date, Rights, Photographer, Organization</li>"
            "<li>The Google Worksheet MUST be saved as a Google Sheet <a href='#'>click here to see example</a></li>"
            "</ul>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # URL input section
        url_label = QLabel("<b>Google Worksheet URL:</b>")
        layout.addWidget(url_label)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        layout.addWidget(self.url_edit)
        
        # Hint text
        hint_label = QLabel(
            "<i>Paste the complete URL from your browser's address bar when viewing the worksheet.</i>"
        )
        from gui.theme_manager import ThemeManager
        theme = ThemeManager.instance()
        hint_label.setStyleSheet(f"color: {theme.get_current_colors().disabled_text};")
        layout.addWidget(hint_label)
        
        layout.addSpacing(20)
        
        # Buttons
        button_box = QDialogButtonBox()
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_and_close)
        button_box.addButton(save_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_box.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)
                
    def _save_and_close(self):
        """Save the URL and mark step as complete."""
        url = self.url_edit.text().strip()

        # Validate URL
        if not url:
            self.log_manager.warning("Step 1: URL is required but was empty", batch_id=self.batch_id, step=1)
            QMessageBox.warning(
                self,
                "URL Required",
                "Please enter the Google Worksheet URL."
            )
            return

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            self.log_manager.warning(f"Step 1: Invalid URL format - {url[:50]}...", batch_id=self.batch_id, step=1)
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Please enter a valid URL starting with http:// or https://"
            )
            return

        # Save URL to configuration
        try:
            self.log_manager.step_start(1, "Google Worksheet Preparation", batch_id=self.batch_id)

            # Create step1 configuration section if it doesn't exist
            if not self.config_manager.get('step_configurations.step1'):
                self.config_manager.set('step_configurations.step1', {})

            # Save the URL
            self.config_manager.set('step_configurations.step1.worksheet_url', url)

            # Mark step 1 as completed
            self.config_manager.update_step_status(1, True)

            # Save configuration to file
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )

                self.log_manager.step_complete(1, "Google Worksheet Preparation", batch_id=self.batch_id)
                self.log_manager.info(f"Step 1: Worksheet URL saved", batch_id=self.batch_id, step=1)

                QMessageBox.information(
                    self,
                    "Step 1 Complete",
                    f"Google Worksheet URL saved successfully!\n\n"
                    f"Step 1 is now marked as complete.\n\n"
                    f"URL: {url}"
                )

                self.accept()
            else:
                self.log_manager.error("Step 1: No config file path found", batch_id=self.batch_id, step=1)
                QMessageBox.warning(
                    self,
                    "Save Error",
                    "Could not save configuration: No config file path found."
                )

        except Exception as e:
            self.log_manager.step_error(1, str(e), batch_id=self.batch_id, exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save configuration:\n{str(e)}"
            )
    
    def get_url(self):
        """Get the entered URL."""
        return self.url_edit.text().strip()
