#!/usr/bin/env python3
"""
GUI wrapper for g2c.py - Google Drive to CSV Converter with IPTC Mapping

This GUI application provides a user-friendly interface for the g2c.py functionality,
automatically pulling the most recent URL from the clipboard and using 'export.csv'
as the default export filename.

Features:
- Automatic clipboard URL detection and validation
- Progress tracking for long-running operations
- Built-in preview of processed data
- One-click export to CSV
- Error handling with user-friendly messages

Requirements:
- PyQt5
- All dependencies from g2c.py
"""

import sys
import os
import re
import threading
import traceback
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, 
                            QProgressBar, QMessageBox, QTableWidget, QTableWidgetItem,
                            QSplitter, QGroupBox, QCheckBox, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon

# Try to import clipboard functionality
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("Note: pyperclip not available. Install with: pip install pyperclip")

# Import the g2c functionality
try:
    from g2c import (detect_and_convert_if_needed, fetch_sheet_data, 
                     export_to_csv, extract_spreadsheet_id_from_url,
                     DEFAULT_SPREADSHEET_ID)
    G2C_AVAILABLE = True
except ImportError as e:
    G2C_AVAILABLE = False
    print(f"Error importing g2c module: {e}")

class G2CWorkerThread(QThread):
    """Worker thread for running g2c operations without blocking the GUI"""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(object)  # Result data (DataFrame or None)
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, url, auto_convert=False):
        super().__init__()
        self.url = url
        self.auto_convert = auto_convert
        self.df = None
        
    def run(self):
        """Run the g2c process in a separate thread"""
        try:
            self.progress.emit("Extracting spreadsheet ID...")
            
            # Extract spreadsheet ID directly (bypass interactive detection)
            spreadsheet_id = extract_spreadsheet_id_from_url(self.url)
            self.progress.emit(f"📋 Using spreadsheet ID: {spreadsheet_id}")
            
            # First try to detect if this is an Excel file
            try:
                from sheets_type_detector import SheetsTypeDetector, detect_sheet_type
                from g2c import get_credentials
                
                self.progress.emit("🔍 Detecting file type...")
                
                # Get enhanced credentials for detection
                creds = get_credentials(enhanced_mode=True)
                
                # Initialize detector
                detector = SheetsTypeDetector(
                    client_secret_file='client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json',
                    token_file='token_drive_sheets.pickle'
                )
                
                # Try to detect file type
                file_info = detect_sheet_type(spreadsheet_id, detector)
                
                self.progress.emit(f"📄 File: {file_info['file_name']}")
                self.progress.emit(f"🏷️  Type: {file_info['mime_type']}")
                
                if file_info['is_excel']:
                    self.error.emit("❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data")
                    return
                elif not file_info['is_native_sheet']:
                    self.progress.emit(f"⚠️  Unknown file type: {file_info['mime_type']} - attempting to use as-is...")
                    
            except ImportError:
                # Detection modules not available, proceed normally
                self.progress.emit("📝 Detection modules not available - proceeding with original URL")
            except Exception as detection_error:
                # Handle detection errors
                error_str = str(detection_error).lower()
                if 'access denied' in error_str or 'permission' in error_str:
                    self.progress.emit("⚠️  File access issue - trying with current authentication...")
                elif 'operation is not supported' in error_str:
                    self.error.emit("❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data")
                    return
                else:
                    self.progress.emit(f"⚠️  Detection failed: {detection_error} - proceeding with original file ID...")
            
            self.progress.emit("Fetching data from Google Sheet...")
            
            # Fetch the data directly
            df = fetch_sheet_data(spreadsheet_id)
            
            if df is not None:
                self.progress.emit(f"✅ Data loaded successfully! ({len(df)} rows, {len(df.columns)} columns)")
                self.finished.emit(df)
            else:
                self.error.emit("Failed to load data from the Google Sheet.")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if "Excel Spreadsheet" in str(e) or "operation is not supported" in str(e).lower():
                error_msg = "❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data"
            elif "This operation is not supported for this document" in str(e):
                error_msg = "❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data"
            elif "Requested entity was not found" in str(e):
                error_msg = "❌ This is an Excel Spreadsheet and needs to be saved as a Google Sheet to process HSTL data"
            self.error.emit(error_msg)


class G2CExportThread(QThread):
    """Worker thread for CSV export operations"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool)  # Success/failure
    error = pyqtSignal(str)
    
    def __init__(self, df, filename='export.csv'):
        super().__init__()
        self.df = df
        self.filename = filename
        
    def run(self):
        """Export DataFrame to CSV"""
        try:
            self.progress.emit(f"Exporting data to {self.filename}...")
            success = export_to_csv(self.df, self.filename)
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Export error: {str(e)}")


class G2CMainWindow(QMainWindow):
    """Main GUI window for the g2c application"""
    
    def __init__(self):
        super().__init__()
        self.df = None  # Store the loaded DataFrame
        self.worker_thread = None
        self.export_thread = None
        
        self.init_ui()
        self.auto_detect_clipboard_url()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("G2C - Google Drive to CSV Converter")
        
        # Set application-wide larger font
        app_font = QFont()
        app_font.setPointSize(14)  # Doubled from typical 7pt to 14pt
        self.setFont(app_font)
        
        # Start maximized/full screen
        self.setWindowState(Qt.WindowMaximized)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)  # Increased spacing between elements
        
        # URL Input Section
        url_group = QGroupBox("📋 Spreadsheet URL")
        url_layout = QVBoxLayout(url_group)
        
        # URL input with auto-detect button
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Google Sheets or Drive URL (or auto-detect from clipboard)")
        self.url_input.textChanged.connect(self.validate_url)
        # Make input field bigger
        input_font = QFont()
        input_font.setPointSize(12)
        self.url_input.setFont(input_font)
        self.url_input.setMinimumHeight(35)
        
        self.auto_detect_btn = QPushButton("🔄 Auto-detect from Clipboard")
        self.auto_detect_btn.clicked.connect(self.auto_detect_clipboard_url)
        self.auto_detect_btn.setEnabled(CLIPBOARD_AVAILABLE)
        # Make button bigger
        button_font = QFont()
        button_font.setPointSize(12)
        self.auto_detect_btn.setFont(button_font)
        self.auto_detect_btn.setMinimumHeight(35)
        
        url_input_layout.addWidget(self.url_input)
        url_input_layout.addWidget(self.auto_detect_btn)
        url_layout.addLayout(url_input_layout)
        
        # URL status label
        self.url_status = QLabel("Enter a URL to get started")
        self.url_status.setStyleSheet("color: gray;")
        url_layout.addWidget(self.url_status)
        
        main_layout.addWidget(url_group)
        
        # Options Section
        options_group = QGroupBox("⚙️ Options")
        options_layout = QHBoxLayout(options_group)
        
        self.auto_convert_check = QCheckBox("Auto-convert Excel files")
        self.auto_convert_check.setChecked(False)
        self.auto_convert_check.setToolTip("Automatically convert Excel files to Google Sheets (requires enhanced permissions)")
        
        options_layout.addWidget(self.auto_convert_check)
        options_layout.addStretch()
        
        main_layout.addWidget(options_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📊 Load Data")
        self.load_btn.clicked.connect(self.load_data)
        self.load_btn.setEnabled(False)
        # Make load button bigger
        self.load_btn.setFont(button_font)
        self.load_btn.setMinimumHeight(45)
        
        self.export_btn = QPushButton("💾 Export to CSV (export.csv)")
        self.export_btn.clicked.connect(self.export_csv)
        self.export_btn.setEnabled(False)
        # Make export button bigger
        self.export_btn.setFont(button_font)
        self.export_btn.setMinimumHeight(45)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Progress Section
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status and Preview Section
        splitter = QSplitter(Qt.Vertical)
        
        # Status/Log area
        status_group = QGroupBox("📝 Status & Messages")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)  # Increased height
        self.status_text.setReadOnly(True)
        # Much larger status text font
        status_font = QFont("Consolas", 11)  # Increased from 9 to 11
        self.status_text.setFont(status_font)
        status_layout.addWidget(self.status_text)
        
        splitter.addWidget(status_group)
        
        # Data preview area
        preview_group = QGroupBox("👁️ Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        # Make table font bigger
        table_font = QFont()
        table_font.setPointSize(11)  # Increased table font size
        self.data_table.setFont(table_font)
        preview_layout.addWidget(self.data_table)
        
        splitter.addWidget(preview_group)
        
        # Set splitter proportions
        splitter.setSizes([150, 400])
        main_layout.addWidget(splitter)
        
        # Create status bar with version and timestamp
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add version and timestamp to status bar with smaller fonts
        version_label = QLabel("Ver 0.1")
        version_font = QFont()
        version_font.setPointSize(8)  # Small font size
        version_label.setFont(version_font)
        version_label.setStyleSheet("margin-right: 10px; color: #666666;")
        
        # Create timestamp that updates every second
        self.timestamp_label = QLabel()
        timestamp_font = QFont()
        timestamp_font.setPointSize(8)  # Small font size
        self.timestamp_label.setFont(timestamp_font)
        self.timestamp_label.setStyleSheet("color: #666666;")
        self.update_timestamp()
        
        # Timer to update timestamp every second
        self.timestamp_timer = QTimer()
        self.timestamp_timer.timeout.connect(self.update_timestamp)
        self.timestamp_timer.start(1000)  # Update every 1000ms (1 second)
        
        # Add labels to status bar (right side)
        self.status_bar.addPermanentWidget(version_label)
        self.status_bar.addPermanentWidget(self.timestamp_label)
        
        # Initialize status
        self.log_message("🚀 G2C GUI ready! Enter a Google Sheets URL to get started.")
        if not CLIPBOARD_AVAILABLE:
            self.log_message("⚠️ Clipboard detection unavailable. Install pyperclip for auto-detection.")
        if not G2C_AVAILABLE:
            self.log_message("❌ G2C module not available. Please ensure g2c.py is in the same directory.")
            self.load_btn.setEnabled(False)
    
    def update_timestamp(self):
        """Update the timestamp in the status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.setText(current_time)
    
    def log_message(self, message):
        """Add a message to the status log"""
        self.status_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def auto_detect_clipboard_url(self):
        """Automatically detect and validate URLs from clipboard"""
        if not CLIPBOARD_AVAILABLE:
            self.log_message("❌ Clipboard detection not available")
            return
            
        try:
            clipboard_text = pyperclip.paste().strip()
            
            if not clipboard_text:
                self.log_message("📋 Clipboard is empty")
                return
            
            # Check if it looks like a Google URL
            google_url_patterns = [
                r'https://docs\.google\.com/spreadsheets',
                r'https://drive\.google\.com/file',
                r'spreadsheets/d/',
                r'file/d/'
            ]
            
            is_google_url = any(re.search(pattern, clipboard_text) for pattern in google_url_patterns)
            
            if is_google_url:
                self.url_input.setText(clipboard_text)
                self.log_message(f"✅ Auto-detected Google Sheet URL from clipboard")
                self.validate_url()
            else:
                # Check if it's just a spreadsheet ID
                if re.match(r'^[a-zA-Z0-9_-]+$', clipboard_text) and len(clipboard_text) > 20:
                    self.url_input.setText(clipboard_text)
                    self.log_message(f"✅ Auto-detected spreadsheet ID from clipboard")
                    self.validate_url()
                else:
                    self.log_message(f"📋 Clipboard content doesn't appear to be a Google URL")
                    
        except Exception as e:
            self.log_message(f"❌ Error reading clipboard: {str(e)}")
    
    def validate_url(self):
        """Validate the entered URL and update UI accordingly"""
        url = self.url_input.text().strip()
        
        if not url:
            self.url_status.setText("Enter a URL to get started")
            self.url_status.setStyleSheet("color: gray;")
            self.load_btn.setEnabled(False)
            return
        
        try:
            # Try to extract spreadsheet ID to validate
            spreadsheet_id = extract_spreadsheet_id_from_url(url)
            self.url_status.setText(f"✅ Valid URL (ID: {spreadsheet_id[:20]}...)")
            self.url_status.setStyleSheet("color: green;")
            self.load_btn.setEnabled(G2C_AVAILABLE)
        except ValueError as e:
            self.url_status.setText(f"❌ Invalid URL format")
            self.url_status.setStyleSheet("color: red;")
            self.load_btn.setEnabled(False)
    
    def load_data(self):
        """Load data from the specified URL"""
        if not G2C_AVAILABLE:
            QMessageBox.critical(self, "Error", "G2C module not available!")
            return
            
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL first!")
            return
        
        # Disable UI during operation
        self.load_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.log_message(f"🔄 Starting data load from: {url}")
        
        # Start worker thread
        self.worker_thread = G2CWorkerThread(url, self.auto_convert_check.isChecked())
        self.worker_thread.progress.connect(self.log_message)
        self.worker_thread.finished.connect(self.on_data_loaded)
        self.worker_thread.error.connect(self.on_load_error)
        self.worker_thread.start()
    
    def on_data_loaded(self, df):
        """Handle successful data loading"""
        self.df = df
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        if df is not None:
            self.log_message(f"✅ Data loaded successfully! Shape: {df.shape}")
            self.update_data_preview(df)
        else:
            self.log_message("❌ No data received")
    
    def on_load_error(self, error_msg):
        """Handle data loading errors"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.log_message(f"❌ {error_msg}")
        QMessageBox.critical(self, "Load Error", error_msg)
    
    def update_data_preview(self, df):
        """Update the data preview table with DataFrame contents"""
        if df is None or df.empty:
            self.data_table.clear()
            return
        
        # Limit preview to first 100 rows and 20 columns for performance
        preview_rows = min(100, len(df))
        preview_cols = min(20, len(df.columns))
        
        self.data_table.setRowCount(preview_rows)
        self.data_table.setColumnCount(preview_cols)
        
        # Set column headers
        self.data_table.setHorizontalHeaderLabels([str(col)[:50] for col in df.columns[:preview_cols]])
        
        # Populate data
        for i in range(preview_rows):
            for j in range(preview_cols):
                value = str(df.iloc[i, j]) if df.iloc[i, j] is not None else ""
                # Limit cell content length for display
                if len(value) > 100:
                    value = value[:100] + "..."
                item = QTableWidgetItem(value)
                self.data_table.setItem(i, j, item)
        
        # Auto-resize columns
        self.data_table.resizeColumnsToContents()
        
        # Update status
        if len(df) > preview_rows or len(df.columns) > preview_cols:
            self.log_message(f"📊 Showing preview: {preview_rows}/{len(df)} rows, {preview_cols}/{len(df.columns)} columns")
        else:
            self.log_message(f"📊 Showing all data: {len(df)} rows, {len(df.columns)} columns")
    
    def export_csv(self):
        """Export the loaded data to CSV"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No data to export! Please load data first.")
            return
        
        # Disable UI during export
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.log_message("💾 Starting CSV export to 'export.csv'...")
        
        # Start export thread
        self.export_thread = G2CExportThread(self.df, 'export.csv')
        self.export_thread.progress.connect(self.log_message)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.error.connect(self.on_export_error)
        self.export_thread.start()
    
    def on_export_finished(self, success):
        """Handle successful export completion"""
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        
        if success:
            self.log_message("✅ Export completed successfully!")
            QMessageBox.information(self, "Export Complete", 
                                  "Data exported to 'export.csv' successfully!\n\n"
                                  "The file has been saved in the current directory.")
        else:
            self.log_message("❌ Export failed!")
            QMessageBox.warning(self, "Export Failed", "CSV export was not successful. Check the status log for details.")
    
    def on_export_error(self, error_msg):
        """Handle export errors"""
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        self.log_message(f"❌ Export error: {error_msg}")
        QMessageBox.critical(self, "Export Error", error_msg)
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop the timestamp timer
        if hasattr(self, 'timestamp_timer'):
            self.timestamp_timer.stop()
        
        # Clean up worker threads
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
        
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.terminate()
            self.export_thread.wait()
        
        event.accept()

def main():
    """Main function to run the GUI application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("G2C GUI")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("HST Metadata Tools")
    
    # Create and show main window
    window = G2CMainWindow()
    window.show()
    
    # Check for required dependencies
    if not G2C_AVAILABLE:
        QMessageBox.critical(window, "Missing Dependencies", 
                           "The g2c module is not available.\n\n"
                           "Please ensure g2c.py is in the same directory as this script.")
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
