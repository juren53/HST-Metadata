"""
Step 2 Dialog - CSV Conversion

Converts Google Worksheet to CSV (export.csv) using g2c functionality.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

from utils.log_manager import get_log_manager


class CSVConversionThread(QThread):
    """Worker thread for CSV conversion."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool)  # Success/failure
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, worksheet_url, output_path):
        super().__init__()
        self.worksheet_url = worksheet_url
        self.output_path = output_path
        
    def run(self):
        """Run the CSV conversion."""
        import os
        original_dir = os.getcwd()
        
        try:
            self.progress.emit("Starting CSV conversion...")
            self.progress.emit(f"Source: {self.worksheet_url}")
            self.progress.emit(f"Output: {self.output_path}")
            
            # Import g2c functionality
            try:
                import sys
                # Change to Framework directory where g2c.py and credentials are located
                framework_path = Path(__file__).parent.parent.parent
                os.chdir(str(framework_path))
                
                # Ensure framework directory is in path for g2c import
                if str(framework_path) not in sys.path:
                    sys.path.insert(0, str(framework_path))
                
                self.progress.emit(f"Working directory: {framework_path}")
                
                from g2c import (fetch_sheet_data, export_to_csv, 
                               extract_spreadsheet_id_from_url)
                
                self.progress.emit("✓ g2c module loaded")
                
            except ImportError as e:
                os.chdir(original_dir)
                self.error.emit(f"Failed to import g2c module: {e}")
                return
            
            # Extract spreadsheet ID
            self.progress.emit("Extracting spreadsheet ID...")
            spreadsheet_id = extract_spreadsheet_id_from_url(self.worksheet_url)
            self.progress.emit(f"✓ Spreadsheet ID: {spreadsheet_id}")
            
            # Fetch data from Google Sheet
            self.progress.emit("Fetching data from Google Sheet...")
            df = fetch_sheet_data(spreadsheet_id)
            
            if df is None:
                self.error.emit("Failed to fetch data from Google Sheet")
                return
            
            self.progress.emit(f"✓ Data loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Export to CSV
            self.progress.emit(f"Exporting to {self.output_path}...")
            success = export_to_csv(df, self.output_path)
            
            if success:
                self.progress.emit("✓ CSV export completed successfully")
                self.finished.emit(True)
            else:
                self.error.emit("CSV export failed")
                
        except Exception as e:
            self.error.emit(f"Error during conversion: {str(e)}")
        finally:
            # Restore original working directory
            os.chdir(original_dir)


class Step2Dialog(QDialog):
    """Dialog for Step 2: CSV Conversion."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.conversion_thread = None
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 2: CSV Conversion")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)  # Increased by 20% (500 * 1.2 = 600)

        self.log_manager.debug("Opened Step 2 dialog", batch_id=batch_id, step=2)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("<h2>Step 2: CSV Conversion</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step converts the Google Worksheet (from Step 1) to a CSV file "
            "that will be used for metadata processing.</p>"
            "<p><b>Output:</b> export.csv in the output/csv directory</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Worksheet URL display
        url_label = QLabel("<b>Google Worksheet URL:</b>")
        layout.addWidget(url_label)
        
        worksheet_url = self.config_manager.get('step_configurations.step1.worksheet_url', 'Not set')
        self.url_display = QLabel(worksheet_url)
        self.url_display.setWordWrap(True)
        # Use theme-aware colors
        from gui.theme_manager import ThemeManager, ThemeMode
        theme = ThemeManager.instance()
        colors = theme.get_current_colors()
        bg_color = colors.base_bg if theme._current_resolved_mode == ThemeMode.DARK else "#f0f0f0"
        self.url_display.setStyleSheet(f"color: {colors.link}; padding: 5px; background-color: {bg_color}; border-radius: 3px;")
        layout.addWidget(self.url_display)
        
        layout.addSpacing(20)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Output/Status section
        status_label = QLabel("<b>Status & Output:</b>")
        layout.addWidget(status_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        layout.addWidget(self.output_text)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("Convert to CSV")
        self.convert_btn.setDefault(True)
        self.convert_btn.clicked.connect(self._start_conversion)
        button_layout.addWidget(self.convert_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Check if worksheet URL is set
        if worksheet_url == 'Not set':
            self.output_text.append("⚠️ Warning: Google Worksheet URL is not set. Please complete Step 1 first.")
            self.convert_btn.setEnabled(False)
        else:
            self.output_text.append("Ready to convert Google Worksheet to CSV.")
            self.output_text.append(f"Source: {worksheet_url}")
            
    def _start_conversion(self):
        """Start the CSV conversion process."""
        self.log_manager.step_start(2, "CSV Conversion", batch_id=self.batch_id)
        worksheet_url = self.config_manager.get('step_configurations.step1.worksheet_url', '')

        if not worksheet_url:
            QMessageBox.warning(
                self,
                "Missing URL",
                "Google Worksheet URL is not set. Please complete Step 1 first."
            )
            return
        
        # Get output path
        data_directory = self.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "Configuration Error",
                "Project data directory is not set."
            )
            return
        
        output_filename = self.config_manager.get('step_configurations.step2.output_filename', 'export.csv')
        output_dir = Path(data_directory) / 'output' / 'csv'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_filename
        
        # Disable button and show progress
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.output_text.append("\n" + "="*50)
        self.output_text.append("Starting CSV conversion...")
        
        # Start conversion thread
        self.conversion_thread = CSVConversionThread(worksheet_url, str(output_path))
        self.conversion_thread.progress.connect(self._on_progress)
        self.conversion_thread.finished.connect(self._on_finished)
        self.conversion_thread.error.connect(self._on_error)
        self.conversion_thread.start()
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.output_text.append(message)
        
    def _on_finished(self, success):
        """Handle conversion completion."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        
        if success:
            self.output_text.append("\n✅ CSV conversion completed successfully!")
            
            # Add batch title to cell A2 of export.csv
            try:
                # Get the batch title (project name)
                batch_title = self.config_manager.get('project.name', '')
                
                if batch_title:
                    # Get the CSV file path
                    data_directory = self.config_manager.get('project.data_directory', '')
                    output_filename = self.config_manager.get('step_configurations.step2.output_filename', 'export.csv')
                    csv_path = Path(data_directory) / 'output' / 'csv' / output_filename
                    
                    if csv_path.exists():
                        import csv
                        
                        # Read the CSV file
                        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                            reader = csv.reader(f)
                            rows = list(reader)
                        
                        # Modify cell A2 to append batch title in brackets
                        if len(rows) > 1 and len(rows[1]) > 0:
                            original_a2 = rows[1][0]
                            rows[1][0] = f"{original_a2} [{batch_title}]"
                            
                            # Write back to CSV
                            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerows(rows)
                            
                            self.output_text.append(f"✓ Appended batch title '[{batch_title}]' to cell A2")
                        else:
                            self.output_text.append("⚠️  Warning: CSV file has less than 2 rows, could not add batch title")
                    else:
                        self.output_text.append("⚠️  Warning: CSV file not found, could not add batch title")
                else:
                    self.output_text.append("⚠️  Warning: Batch title not set, skipping A2 modification")
                    
            except Exception as e:
                self.output_text.append(f"⚠️  Error adding batch title to A2: {str(e)}")
            
            # Mark step 2 as completed
            self.config_manager.update_step_status(2, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(2, "CSV Conversion", batch_id=self.batch_id)

            QMessageBox.information(
                self,
                "Conversion Complete",
                "CSV conversion completed successfully!\n\n"
                "Step 2 is now marked as complete."
            )

            self.accept()
        else:
            self.log_manager.step_error(2, "CSV conversion failed", batch_id=self.batch_id)
            self.output_text.append("\n❌ CSV conversion failed.")
            
    def _on_error(self, error_msg):
        """Handle conversion errors."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)

        self.log_manager.step_error(2, error_msg, batch_id=self.batch_id)
        self.output_text.append(f"\n❌ Error: {error_msg}")

        QMessageBox.critical(
            self,
            "Conversion Error",
            f"CSV conversion failed:\n\n{error_msg}"
        )
