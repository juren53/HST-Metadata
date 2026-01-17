"""
Pop-out Log Viewer Dialog for HSTL Photo Framework

Provides a standalone window for viewing logs, useful for multi-monitor
setups where the user wants to keep logs visible while working.
"""

from typing import Optional

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

from gui.widgets.enhanced_log_widget import EnhancedLogWidget
from utils.log_manager import LogRecord


class LogViewerDialog(QDialog):
    """
    Pop-out log viewer window.

    This dialog hosts an EnhancedLogWidget in a standalone window
    that can be positioned independently of the main application window.

    Signals:
        closed: Emitted when the dialog is closed
    """

    closed = pyqtSignal()

    def __init__(self, parent=None, max_records: int = 1000):
        super().__init__(parent)
        self._init_ui(max_records)
        self._setup_window()

    def _init_ui(self, max_records: int):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create the log widget
        self.log_widget = EnhancedLogWidget(max_records=max_records)
        self.log_widget.set_popped_out(True)
        layout.addWidget(self.log_widget)

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("HPM Log Viewer")
        self._current_batch_name = None

        # Make it an independent window
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinMaxButtonsHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # Set reasonable default size
        self.resize(1000, 600)

        # Position slightly offset from parent if available
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(parent_geo.x() + 50, parent_geo.y() + 50)

    def append_log(self, record: LogRecord):
        """Forward log record to the widget."""
        self.log_widget.append_log(record)

    def add_batch_option(self, batch_id: str, batch_name: str):
        """Add batch to filter dropdown."""
        self.log_widget.add_batch_option(batch_id, batch_name)

    def set_max_records(self, max_records: int):
        """Set maximum number of records."""
        self.log_widget.set_max_records(max_records)

    def set_batch_name(self, batch_name: str):
        """Set the current batch name and update the title bar."""
        self._current_batch_name = batch_name
        if batch_name:
            self.setWindowTitle(f"HPM Log Viewer - {batch_name}")
        else:
            self.setWindowTitle("HPM Log Viewer")

    def closeEvent(self, event):
        """Handle dialog close."""
        self.closed.emit()
        event.accept()

    def show_and_raise(self):
        """Show the dialog and bring it to front."""
        self.show()
        self.raise_()
        self.activateWindow()
