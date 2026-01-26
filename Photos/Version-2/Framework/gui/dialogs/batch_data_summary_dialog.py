"""Batch Data Directory Summary Dialog"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QDialogButtonBox, QHeaderView
)
from PyQt6.QtCore import Qt, QSettings
from utils.file_utils import FileUtils


class BatchDataSummaryDialog(QDialog):
    """Dialog showing batch data directory summary with file counts and sizes."""
    
    def __init__(self, batch_info, parent=None):
        super().__init__(parent)
        
        self.batch_info = batch_info
        self.data_directory = Path(batch_info.get('data_directory', ''))
        self.settings = QSettings("HSTL", "PhotoFramework")
        
        self.setWindowTitle(f"Batch Data Summary - {batch_info.get('name', 'Unknown')}")
        self.setMinimumSize(600, 500)
        
        self._init_ui()
        self._load_summary()
        self._load_column_widths()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Header label
        header_label = QLabel(f"<b>Data Directory:</b> {self.data_directory}")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Category", "Number of Files", "Size"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        
        # Set proportional column widths (50% for Category, 25% each for counts and size)
        total_width = 600  # Base width
        header.resizeSection(0, int(total_width * 0.50))  # Category: 50%
        header.resizeSection(1, int(total_width * 0.25))  # Number of Files: 25%
        header.resizeSection(2, int(total_width * 0.25))  # Size: 25%
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        layout.addWidget(self.table)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
    def _load_summary(self):
        """Load and display batch data directory summary."""
        if not self.data_directory.exists():
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Directory not found"))
            return
        
        # Define directory structure
        directories = [
            # (label, path, category)
            ("**Input**", None, "header"),
            ("Spreadsheet", self.data_directory / "input" / "spreadsheet", "data"),
            ("TIFFs", self.data_directory / "input" / "tiff", "data"),
            ("", None, "spacer"),
            ("**Output**", None, "header"),
            ("Export CSV", self.data_directory / "output" / "csv", "data"),
            ("Processed TIFFs", self.data_directory / "output" / "tiff_processed", "data"),
            ("JPEG Converted", self.data_directory / "output" / "jpeg", "data"),
            ("JPEG Resized", self.data_directory / "output" / "jpeg_resized", "data"),
            ("JPEG Watermarked", self.data_directory / "output" / "jpeg_watermarked", "data"),
            ("", None, "spacer"),
            ("Reports", self.data_directory / "reports", "data"),
            ("Logs", self.data_directory / "logs", "data"),
            ("Config", self.data_directory / "config", "data"),
            ("", None, "spacer"),
            ("**Total**", None, "total"),
        ]
        
        self.table.setRowCount(len(directories))
        
        total_files = 0
        total_size = 0
        
        for row, (label, dir_path, category) in enumerate(directories):
            # Category column
            category_item = QTableWidgetItem(label)
            
            if category == "header" or category == "total":
                # Bold headers
                font = category_item.font()
                font.setBold(True)
                category_item.setFont(font)
                self.table.setItem(row, 0, category_item)
                
                if category == "header":
                    # Empty cells for headers
                    self.table.setItem(row, 1, QTableWidgetItem(""))
                    self.table.setItem(row, 2, QTableWidgetItem(""))
                    
            elif category == "spacer":
                # Empty row
                self.table.setItem(row, 0, QTableWidgetItem(""))
                self.table.setItem(row, 1, QTableWidgetItem(""))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                
            elif category == "data":
                self.table.setItem(row, 0, category_item)
                
                if dir_path and dir_path.exists():
                    # Count files
                    file_count = sum(1 for f in dir_path.rglob('*') if f.is_file())
                    
                    # Get directory size
                    dir_size = FileUtils.get_directory_size(dir_path)
                    
                    # Update totals
                    total_files += file_count
                    total_size += dir_size
                    
                    # File count column
                    count_item = QTableWidgetItem(str(file_count))
                    count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, 1, count_item)
                    
                    # Size column
                    size_item = QTableWidgetItem(FileUtils.format_file_size(dir_size))
                    size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, 2, size_item)
                else:
                    # Directory doesn't exist
                    count_item = QTableWidgetItem("0")
                    count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, 1, count_item)
                    
                    size_item = QTableWidgetItem("0 B")
                    size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, 2, size_item)
        
        # Fill in total row (last row)
        total_row = len(directories) - 1
        
        # Total files
        total_count_item = QTableWidgetItem(str(total_files))
        total_count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        font = total_count_item.font()
        font.setBold(True)
        total_count_item.setFont(font)
        self.table.setItem(total_row, 1, total_count_item)
        
        # Total size
        total_size_item = QTableWidgetItem(FileUtils.format_file_size(total_size))
        total_size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        font = total_size_item.font()
        font.setBold(True)
        total_size_item.setFont(font)
        self.table.setItem(total_row, 2, total_size_item)
    
    def _load_column_widths(self):
        """Load saved column widths from settings."""
        header = self.table.horizontalHeader()
        
        # Try to load saved widths
        col0_width = self.settings.value("batch_data_summary/col0_width", type=int)
        col1_width = self.settings.value("batch_data_summary/col1_width", type=int)
        col2_width = self.settings.value("batch_data_summary/col2_width", type=int)
        
        # Apply saved widths if they exist
        if col0_width:
            header.resizeSection(0, col0_width)
        if col1_width:
            header.resizeSection(1, col1_width)
        if col2_width:
            header.resizeSection(2, col2_width)
    
    def _save_column_widths(self):
        """Save column widths to settings."""
        header = self.table.horizontalHeader()
        
        self.settings.setValue("batch_data_summary/col0_width", header.sectionSize(0))
        self.settings.setValue("batch_data_summary/col1_width", header.sectionSize(1))
        self.settings.setValue("batch_data_summary/col2_width", header.sectionSize(2))
    
    def closeEvent(self, event):
        """Handle dialog close event to save column widths."""
        self._save_column_widths()
        super().closeEvent(event)
