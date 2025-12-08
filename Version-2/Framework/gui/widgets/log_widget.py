"""Log Viewer Widget"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel


class LogWidget(QWidget):
    """Widget for viewing logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        label = QLabel("<h2>Logs</h2>")
        layout.addWidget(label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
