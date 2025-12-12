"""New Batch Dialog"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QRadioButton,
    QButtonGroup, QGroupBox, QDialogButtonBox
)
from PyQt6.QtCore import QSettings


class NewBatchDialog(QDialog):
    """Dialog for creating a new batch."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = QSettings("HSTL", "PhotoFramework")
        self.setWindowTitle("Create New Batch")
        self.setMinimumWidth(500)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Project name
        layout.addWidget(QLabel("<b>Project Name:</b>"))
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("e.g., January 2025 Batch")
        layout.addWidget(self.project_name_edit)
        
        layout.addSpacing(10)
        
        # Location options
        location_group = QGroupBox("Batch Location")
        location_layout = QVBoxLayout(location_group)
        
        self.location_group = QButtonGroup(self)
        
        # Option 1: Use default (get from settings)
        default_location = self.settings.value("defaultBatchLocation", "C:\\Data\\HSTL_Batches")
        self.default_radio = QRadioButton(f"Use default location ({default_location})")
        self.default_radio.setChecked(True)
        self.location_group.addButton(self.default_radio, 1)
        location_layout.addWidget(self.default_radio)
        
        # Option 2: Custom base directory
        self.custom_base_radio = QRadioButton("Use custom base directory:")
        self.location_group.addButton(self.custom_base_radio, 2)
        location_layout.addWidget(self.custom_base_radio)
        
        base_layout = QHBoxLayout()
        self.base_dir_edit = QLineEdit()
        self.base_dir_edit.setPlaceholderText("C:\\MyBatches")
        self.base_dir_edit.setEnabled(False)
        base_layout.addWidget(self.base_dir_edit)
        
        base_browse_btn = QPushButton("Browse...")
        base_browse_btn.clicked.connect(self._browse_base_dir)
        base_layout.addWidget(base_browse_btn)
        location_layout.addLayout(base_layout)
        
        # Option 3: Full custom path
        self.custom_full_radio = QRadioButton("Use full custom path:")
        self.location_group.addButton(self.custom_full_radio, 3)
        location_layout.addWidget(self.custom_full_radio)
        
        full_layout = QHBoxLayout()
        self.full_path_edit = QLineEdit()
        self.full_path_edit.setPlaceholderText("C:\\CustomPath\\MyProject")
        self.full_path_edit.setEnabled(False)
        full_layout.addWidget(self.full_path_edit)
        
        full_browse_btn = QPushButton("Browse...")
        full_browse_btn.clicked.connect(self._browse_full_path)
        full_layout.addWidget(full_browse_btn)
        location_layout.addLayout(full_layout)
        
        layout.addWidget(location_group)
        
        # Connect radio buttons
        self.location_group.buttonClicked.connect(self._on_location_changed)
        
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _on_location_changed(self, button):
        """Handle location radio button changes."""
        selected_id = self.location_group.id(button)
        
        self.base_dir_edit.setEnabled(selected_id == 2)
        self.full_path_edit.setEnabled(selected_id == 3)
        
    def _browse_base_dir(self):
        """Browse for base directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Base Directory", "C:\\"
        )
        if dir_path:
            self.base_dir_edit.setText(dir_path)
            self.custom_base_radio.setChecked(True)
            self._on_location_changed(self.custom_base_radio)
            
    def _browse_full_path(self):
        """Browse for full path."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Batch Directory", "C:\\"
        )
        if dir_path:
            self.full_path_edit.setText(dir_path)
            self.custom_full_radio.setChecked(True)
            self._on_location_changed(self.custom_full_radio)
            
    def get_values(self):
        """Get entered values."""
        project_name = self.project_name_edit.text().strip()
        
        selected_id = self.location_group.checkedId()
        
        if selected_id == 1:
            # Default location (from settings)
            default_location = self.settings.value("defaultBatchLocation", "C:\\Data\\HSTL_Batches")
            dir_name = project_name.replace(' ', '_')
            data_dir = str(Path(default_location) / dir_name)
        elif selected_id == 2:
            # Custom base directory
            base_dir = self.base_dir_edit.text().strip()
            dir_name = project_name.replace(' ', '_')
            data_dir = str(Path(base_dir) / dir_name)
        else:
            # Full custom path
            data_dir = self.full_path_edit.text().strip()
            
        return project_name, data_dir
