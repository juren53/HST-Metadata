"""Set Data Location Dialog"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import QSettings


class SetDataLocationDialog(QDialog):
    """Dialog for setting the default data files location."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = QSettings("HSTL", "PhotoFramework")
        self.setWindowTitle("Set Data Files Location")
        self.setMinimumWidth(600)
        
        self._init_ui()
        self._load_current_location()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Description
        desc_label = QLabel(
            "<p>Set the default location for batch data files. New batches will be created "
            "in this location unless you specify a different path.</p>"
            "<p><b>Note:</b> This only affects new batches. Existing batches remain in their "
            "current locations.</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Current location display
        layout.addWidget(QLabel("<b>Default Batch Location:</b>"))
        
        path_layout = QHBoxLayout()
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("C:\\Data\\HSTL_Batches")
        path_layout.addWidget(self.location_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_location)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        layout.addSpacing(10)
        
        # Reset to default button
        reset_btn = QPushButton("Reset to Default (C:\\Data\\HSTL_Batches)")
        reset_btn.clicked.connect(self._reset_to_default)
        layout.addWidget(reset_btn)
        
        layout.addSpacing(20)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _load_current_location(self):
        """Load the current default location from settings."""
        default_location = self.settings.value("defaultBatchLocation", "C:\\Data\\HSTL_Batches")
        self.location_edit.setText(default_location)
        
    def _browse_location(self):
        """Browse for a directory."""
        current_path = self.location_edit.text() or "C:\\"
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Default Batch Location", current_path
        )
        if dir_path:
            self.location_edit.setText(dir_path)
            
    def _reset_to_default(self):
        """Reset to the default location."""
        self.location_edit.setText("C:\\Data\\HSTL_Batches")
        
    def _on_accept(self):
        """Validate and save the location."""
        location = self.location_edit.text().strip()
        
        if not location:
            QMessageBox.warning(
                self,
                "Invalid Location",
                "Please specify a location for batch data files."
            )
            return
        
        # Check if path exists or can be created
        path = Path(location)
        if not path.exists():
            reply = QMessageBox.question(
                self,
                "Directory Does Not Exist",
                f"The directory does not exist:\n\n{location}\n\n"
                "Would you like to create it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error Creating Directory",
                        f"Failed to create directory:\n\n{str(e)}"
                    )
                    return
            else:
                return
        
        # Save to settings
        self.settings.setValue("defaultBatchLocation", location)
        self.accept()
        
    def get_location(self):
        """Get the selected location."""
        return self.location_edit.text().strip()
