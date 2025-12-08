"""Configuration Editor Widget"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class ConfigWidget(QWidget):
    """Widget for viewing and editing configuration."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config_manager = None
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        label = QLabel("<h2>Configuration</h2>")
        layout.addWidget(label)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree.setColumnWidth(0, 300)
        layout.addWidget(self.tree)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_config)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
    def set_config(self, config_manager):
        """Set configuration manager."""
        self.config_manager = config_manager
        self._load_config()
        
    def _load_config(self):
        """Load configuration into tree."""
        self.tree.clear()
        
        if not self.config_manager:
            return
            
        config_dict = self.config_manager.to_dict()
        self._add_dict_to_tree(config_dict, self.tree.invisibleRootItem())
        
        self.tree.expandAll()
        
    def _add_dict_to_tree(self, data, parent_item):
        """Recursively add dictionary to tree."""
        for key, value in data.items():
            if key == '_metadata':
                continue
                
            if isinstance(value, dict):
                item = QTreeWidgetItem(parent_item, [str(key), ""])
                self._add_dict_to_tree(value, item)
            else:
                item = QTreeWidgetItem(parent_item, [str(key), str(value)])
