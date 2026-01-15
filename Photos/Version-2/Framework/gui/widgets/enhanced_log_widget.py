"""
Enhanced Log Viewer Widget for HSTL Photo Framework

Features:
- Real-time log display with auto-scroll
- Level filtering (DEBUG, INFO, WARNING, ERROR)
- Batch and step filtering
- Text search with highlighting
- Export to file
- Pop-out window capability
"""

from typing import List, Optional
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QComboBox, QLineEdit, QCheckBox, QFileDialog,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QFont

from utils.log_manager import LogRecord


# Color scheme for log levels
LEVEL_COLORS = {
    'DEBUG': '#6c757d',     # Gray
    'INFO': '#28a745',      # Green
    'WARNING': '#ffc107',   # Yellow/Orange
    'ERROR': '#dc3545',     # Red
    'CRITICAL': '#721c24',  # Dark red
}


class LogFilterBar(QWidget):
    """Filter controls for log viewer."""

    filter_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the filter bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setSpacing(8)

        # Level filter
        layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.level_combo.setCurrentText('ALL')
        self.level_combo.setMinimumWidth(80)
        self.level_combo.currentTextChanged.connect(self.filter_changed)
        layout.addWidget(self.level_combo)

        # Batch filter
        layout.addWidget(QLabel("Batch:"))
        self.batch_combo = QComboBox()
        self.batch_combo.addItem('All Batches', None)
        self.batch_combo.setMinimumWidth(120)
        self.batch_combo.currentTextChanged.connect(self.filter_changed)
        layout.addWidget(self.batch_combo)

        # Step filter
        layout.addWidget(QLabel("Step:"))
        self.step_combo = QComboBox()
        self.step_combo.addItem('All Steps', None)
        for i in range(1, 9):
            self.step_combo.addItem(f'Step {i}', i)
        self.step_combo.setMinimumWidth(80)
        self.step_combo.currentTextChanged.connect(self.filter_changed)
        layout.addWidget(self.step_combo)

        # Search
        layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter log messages...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.filter_changed)
        layout.addWidget(self.search_edit, 1)  # Stretch

        # Auto-scroll toggle
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        layout.addWidget(self.auto_scroll_check)

    def get_level_filter(self) -> str:
        """Get selected level filter."""
        return self.level_combo.currentText()

    def get_batch_filter(self) -> Optional[str]:
        """Get selected batch filter."""
        return self.batch_combo.currentData()

    def get_step_filter(self) -> Optional[int]:
        """Get selected step filter."""
        return self.step_combo.currentData()

    def get_search_text(self) -> str:
        """Get search text."""
        return self.search_edit.text()

    def is_auto_scroll(self) -> bool:
        """Check if auto-scroll is enabled."""
        return self.auto_scroll_check.isChecked()

    def add_batch_option(self, batch_id: str, batch_name: str):
        """Add a batch to the filter dropdown."""
        # Check if already exists
        for i in range(self.batch_combo.count()):
            if self.batch_combo.itemData(i) == batch_id:
                return
        display_name = f"{batch_name} ({batch_id[:8]})"
        self.batch_combo.addItem(display_name, batch_id)

    def clear_filters(self):
        """Reset all filters to default."""
        self.level_combo.setCurrentText('ALL')
        self.batch_combo.setCurrentIndex(0)
        self.step_combo.setCurrentIndex(0)
        self.search_edit.clear()


class EnhancedLogWidget(QWidget):
    """
    Enhanced log viewer with filtering, search, and export capabilities.

    Signals:
        pop_out_requested: Emitted when user clicks pop-out button
    """

    pop_out_requested = pyqtSignal()

    def __init__(self, parent=None, max_records: int = 1000):
        super().__init__(parent)
        self._log_records: List[LogRecord] = []
        self._max_records = max_records
        self._is_popped_out = False
        self._init_ui()

    def _init_ui(self):
        """Initialize the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with title and pop-out button
        header_layout = QHBoxLayout()
        title_label = QLabel("<h2>Logs</h2>")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.pop_out_btn = QPushButton("Pop Out")
        self.pop_out_btn.setToolTip("Open logs in a separate window")
        self.pop_out_btn.clicked.connect(self.pop_out_requested)
        header_layout.addWidget(self.pop_out_btn)

        layout.addLayout(header_layout)

        # Filter bar
        self.filter_bar = LogFilterBar()
        self.filter_bar.filter_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Use monospace font
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.log_text.setFont(font)

        # Set dark background for better readability
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
            }
        """)

        layout.addWidget(self.log_text, 1)

        # Status bar with export buttons
        status_layout = QHBoxLayout()

        self.status_label = QLabel("0 log entries")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.export_btn = QPushButton("Export...")
        self.export_btn.setToolTip("Export logs to a file")
        self.export_btn.clicked.connect(self._export_logs)
        status_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setToolTip("Clear the log display")
        self.clear_btn.clicked.connect(self._clear_logs)
        status_layout.addWidget(self.clear_btn)

        layout.addLayout(status_layout)

    @pyqtSlot(object)
    def append_log(self, record: LogRecord):
        """
        Add a log record to the display.

        This slot is thread-safe when connected to GUILogHandler.log_emitted signal.

        Args:
            record: LogRecord to append
        """
        # Add to internal list
        self._log_records.append(record)

        # Trim if over limit
        if len(self._log_records) > self._max_records:
            self._log_records = self._log_records[-self._max_records:]
            # Rebuild display when trimming
            self._apply_filters()
            return

        # Check if record matches current filters
        if self._matches_filters(record):
            self._append_formatted_record(record)

        # Update status
        self._update_status()

    def _matches_filters(self, record: LogRecord) -> bool:
        """Check if record matches current filter settings."""
        return record.matches_filter(
            level_filter=self.filter_bar.get_level_filter(),
            batch_filter=self.filter_bar.get_batch_filter(),
            step_filter=self.filter_bar.get_step_filter(),
            search_text=self.filter_bar.get_search_text()
        )

    def _append_formatted_record(self, record: LogRecord):
        """Append a formatted log record to the display."""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Set color based on level
        fmt = QTextCharFormat()
        color = LEVEL_COLORS.get(record.level, '#d4d4d4')
        fmt.setForeground(QColor(color))

        cursor.insertText(record.format_display() + '\n', fmt)

        # Auto-scroll if enabled
        if self.filter_bar.is_auto_scroll():
            self.log_text.setTextCursor(cursor)
            self.log_text.ensureCursorVisible()

    def _apply_filters(self):
        """Re-display logs based on current filter settings."""
        self.log_text.clear()

        filtered_count = 0
        for record in self._log_records:
            if self._matches_filters(record):
                self._append_formatted_record(record)
                filtered_count += 1

        self._update_status(filtered_count)

    def _update_status(self, filtered_count: Optional[int] = None):
        """Update the status label."""
        total = len(self._log_records)
        if filtered_count is None:
            # Count currently visible
            filtered_count = sum(1 for r in self._log_records if self._matches_filters(r))

        if filtered_count == total:
            self.status_label.setText(f"{total} log entries")
        else:
            self.status_label.setText(f"Showing {filtered_count} of {total} entries")

    def _export_logs(self):
        """Export filtered logs to a file."""
        # Generate default filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"hpm_logs_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            default_name,
            "Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"HPM Log Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                # Write filter info
                f.write("Filters Applied:\n")
                f.write(f"  Level: {self.filter_bar.get_level_filter()}\n")
                f.write(f"  Batch: {self.filter_bar.get_batch_filter() or 'All'}\n")
                f.write(f"  Step: {self.filter_bar.get_step_filter() or 'All'}\n")
                f.write(f"  Search: {self.filter_bar.get_search_text() or 'None'}\n")
                f.write("\n" + "-" * 60 + "\n\n")

                # Write filtered logs
                count = 0
                for record in self._log_records:
                    if self._matches_filters(record):
                        f.write(record.format_display() + '\n')
                        count += 1

                f.write(f"\n--- Exported {count} entries ---\n")

            QMessageBox.information(
                self,
                "Export Complete",
                f"Exported {count} log entries to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not export logs:\n{str(e)}"
            )

    def _clear_logs(self):
        """Clear all logs from display and memory."""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Clear all log entries from the viewer?\n\n"
            "(This does not affect log files on disk)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._log_records.clear()
            self.log_text.clear()
            self._update_status()

    def add_batch_option(self, batch_id: str, batch_name: str):
        """Add a batch to the filter dropdown."""
        self.filter_bar.add_batch_option(batch_id, batch_name)

    def set_max_records(self, max_records: int):
        """Set maximum number of records to keep."""
        self._max_records = max_records
        if len(self._log_records) > max_records:
            self._log_records = self._log_records[-max_records:]
            self._apply_filters()

    def set_popped_out(self, popped_out: bool):
        """Set whether this widget is in pop-out mode."""
        self._is_popped_out = popped_out
        self.pop_out_btn.setVisible(not popped_out)

    def get_records(self) -> List[LogRecord]:
        """Get all log records."""
        return self._log_records.copy()
