"""
Batch List Widget

Displays all registered batches with status, progress, and management actions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMenu, QLabel, QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QColor, QBrush


class BatchListWidget(QWidget):
    """Widget for displaying and managing batch list."""
    
    batch_selected = pyqtSignal(str, dict)  # batch_id, batch_info
    batch_action_requested = pyqtSignal(str, str)  # action, batch_id
    
    def __init__(self, registry, parent=None):
        super().__init__(parent)
        
        self.registry = registry
        self.show_all = False
        self.settings = QSettings("HSTL", "PhotoFramework")
        
        self._init_ui()
        self._load_column_widths()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("<h2>Batch Projects</h2>")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.show_all_checkbox = QCheckBox("Show All (including archived)")
        self.show_all_checkbox.stateChanged.connect(self._on_show_all_changed)
        header_layout.addWidget(self.show_all_checkbox)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Batch table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Name", "Status", "Progress", "Completed", "Date Created", "Last Accessed", "Batch ID", "Data Directory"
        ])
        
        # Configure table
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Configure columns - all interactive (user adjustable)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Set initial column widths
        self.table.setColumnWidth(0, 200)  # Name
        self.table.setColumnWidth(1, 100)  # Status
        self.table.setColumnWidth(2, 200)  # Progress
        self.table.setColumnWidth(3, 100)  # Completed
        self.table.setColumnWidth(4, 150)  # Date Created
        self.table.setColumnWidth(5, 150)  # Last Accessed
        self.table.setColumnWidth(6, 200)  # Batch ID
        self.table.setColumnWidth(7, 300)  # Data Directory
        
        # Enable stretch for last column
        header.setStretchLastSection(True)
        
        # Left-align specific column headers
        header_item_batch_id = self.table.horizontalHeaderItem(6)
        if header_item_batch_id:
            header_item_batch_id.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        header_item_data_dir = self.table.horizontalHeaderItem(7)
        if header_item_data_dir:
            header_item_data_dir.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Connect signals
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        header.sectionResized.connect(self._on_column_resized)
        
        layout.addWidget(self.table)
        
    def refresh(self):
        """Refresh the batch list."""
        # Reload registry from disk to get latest batches
        self.registry.batches = self.registry._load_registry()
        
        # Get batches
        summaries = self.registry.list_batches_summary()
        
        # Filter by status if needed
        if not self.show_all:
            summaries = [s for s in summaries if s.get('status') == 'active']
        
        # Clear and populate table
        self.table.setRowCount(0)
        
        for summary in summaries:
            self._add_batch_row(summary)
            
    def _add_batch_row(self, summary: dict):
        """Add a batch row to the table."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        batch_id = summary['batch_id']
        
        # Name
        name_item = QTableWidgetItem(summary['name'])
        self.table.setItem(row, 0, name_item)
        
        # Status with color coding
        status = summary.get('status', 'unknown')
        status_item = QTableWidgetItem(status.capitalize())
        # Set text color to black for better contrast
        status_item.setForeground(QBrush(QColor(0, 0, 0)))
        if status == 'active':
            status_item.setBackground(QBrush(QColor(0, 255, 255)))  # Aqua
        elif status == 'completed':
            status_item.setBackground(QBrush(QColor(173, 216, 230)))  # Light blue
        elif status == 'archived':
            status_item.setBackground(QBrush(QColor(211, 211, 211)))  # Light gray
        self.table.setItem(row, 1, status_item)
        
        # Progress bar
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(5, 5, 5, 5)
        
        progress_bar = QProgressBar()
        percentage = summary.get('completion_percentage', 0)
        progress_bar.setValue(int(percentage))
        progress_bar.setFormat(f"{percentage:.0f}%")
        progress_layout.addWidget(progress_bar)
        
        self.table.setCellWidget(row, 2, progress_widget)
        
        # Completed steps
        completed = summary.get('completed_steps', 0)
        total = summary.get('total_steps', 8)
        completed_item = QTableWidgetItem(f"{completed}/{total}")
        completed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, completed_item)
        
        # Date Created
        date_created = summary.get('created', 'Unknown')
        if date_created != 'Unknown':
            # Format datetime
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(date_created)
                date_created = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        created_item = QTableWidgetItem(date_created)
        self.table.setItem(row, 4, created_item)
        
        # Last Accessed
        last_accessed = summary.get('last_accessed', 'Unknown')
        if last_accessed != 'Unknown':
            # Format datetime
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_accessed)
                last_accessed = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        last_item = QTableWidgetItem(last_accessed)
        self.table.setItem(row, 5, last_item)
        
        # Batch ID
        id_item = QTableWidgetItem(batch_id)
        self.table.setItem(row, 6, id_item)
        
        # Data Directory
        data_dir = summary.get('data_directory', 'Unknown')
        data_dir_item = QTableWidgetItem(data_dir)
        self.table.setItem(row, 7, data_dir_item)
        
        # Store batch info in first column
        name_item.setData(Qt.ItemDataRole.UserRole, summary)
        
    def _on_double_click(self, index):
        """Handle double-click on batch."""
        row = index.row()
        name_item = self.table.item(row, 0)
        if name_item:
            summary = name_item.data(Qt.ItemDataRole.UserRole)
            batch_id = summary['batch_id']
            self.batch_selected.emit(batch_id, summary)
            
    def _on_show_all_changed(self, state):
        """Handle show all checkbox change."""
        self.show_all = (state == Qt.CheckState.Checked.value)
        self.refresh()
    
    def _load_column_widths(self):
        """Load saved column widths from settings."""
        for col in range(self.table.columnCount()):
            width = self.settings.value(f"batchList/columnWidth_{col}", None)
            if width is not None:
                self.table.setColumnWidth(col, int(width))
    
    def _on_column_resized(self, column, old_width, new_width):
        """Save column width when resized by user."""
        self.settings.setValue(f"batchList/columnWidth_{column}", new_width)
        
    def _show_context_menu(self, position):
        """Show context menu for batch actions."""
        # Get selected row
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
            
        summary = name_item.data(Qt.ItemDataRole.UserRole)
        batch_id = summary['batch_id']
        status = summary.get('status', 'unknown')
        
        # Create context menu
        menu = QMenu(self)
        
        open_action = menu.addAction("Open Batch")
        open_action.triggered.connect(
            lambda: self.batch_selected.emit(batch_id, summary)
        )
        
        menu.addSeparator()
        
        info_action = menu.addAction("Show Info...")
        info_action.triggered.connect(
            lambda: self.batch_action_requested.emit("info", batch_id)
        )
        
        menu.addSeparator()
        
        if status == 'active':
            complete_action = menu.addAction("Mark as Complete")
            complete_action.triggered.connect(
                lambda: self.batch_action_requested.emit("complete", batch_id)
            )
            
            archive_action = menu.addAction("Archive")
            archive_action.triggered.connect(
                lambda: self.batch_action_requested.emit("archive", batch_id)
            )
        else:
            reactivate_action = menu.addAction("Reactivate")
            reactivate_action.triggered.connect(
                lambda: self.batch_action_requested.emit("reactivate", batch_id)
            )
        
        menu.addSeparator()
        
        remove_action = menu.addAction("Remove from Registry...")
        remove_action.triggered.connect(
            lambda: self.batch_action_requested.emit("remove", batch_id)
        )
        
        # Show menu at cursor position
        menu.exec(self.table.viewport().mapToGlobal(position))
