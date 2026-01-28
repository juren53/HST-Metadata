"""
Step 2 Dialog - CSV Conversion

Converts Excel spreadsheet (from Step 1) to a CSV file (export.csv) using g2c functionality.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

from utils.log_manager import get_log_manager


class CSVConversionThread(QThread):
    """Worker thread for CSV conversion."""

    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, object)  # Success/failure, CSVExportResult
    error = pyqtSignal(str)  # Error messages

    def __init__(self, excel_path, output_path):
        super().__init__()
        self.excel_path = excel_path
        self.output_path = output_path

    def run(self):
        """Run the CSV conversion."""
        import os

        original_dir = os.getcwd()

        try:
            self.progress.emit("Starting CSV conversion...")
            self.progress.emit(f"Source: {self.excel_path}")
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

                from g2c import read_excel_file, export_to_csv

                self.progress.emit("✓ g2c module loaded")

            except ImportError as e:
                os.chdir(original_dir)
                self.error.emit(f"Failed to import g2c module: {e}")
                return

            # Read Excel file
            self.progress.emit("Reading Excel file...")
            df = read_excel_file(self.excel_path)

            if df is None:
                self.error.emit("Failed to read Excel file")
                return

            self.progress.emit(
                f"✓ Data loaded: {len(df)} rows, {len(df.columns)} columns"
            )

            # Export to CSV
            self.progress.emit(f"Exporting to {self.output_path}...")
            result = export_to_csv(df, self.output_path)

            if result.success:
                self.progress.emit("✓ CSV export completed successfully")
                # Report date counts
                if result.production_count > 0:
                    self.progress.emit(f"  - {result.production_count} dates from productionDate columns")
                if result.coverage_count > 0:
                    self.progress.emit(f"  - {result.coverage_count} dates from coverageStartDate columns (fallback)")
                if result.nonstandard_dates:
                    partial_count = sum(1 for d in result.nonstandard_dates if d.date_type == "partial")
                    placeholder_count = sum(1 for d in result.nonstandard_dates if d.date_type == "placeholder")
                    self.progress.emit(f"  - Non-standard dates: {len(result.nonstandard_dates)} ({partial_count} partial, {placeholder_count} placeholder)")
                self.finished.emit(True, result)
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
            "<p>This step converts the Excel spreadsheet (from Step 1) to a CSV file "
            "that will be used for metadata processing.</p>"
            "<p><b>Output:</b> export.csv in the output/csv directory</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addSpacing(20)

        # Excel file display
        excel_label = QLabel("<b>Excel Spreadsheet File:</b>")
        layout.addWidget(excel_label)

        excel_paths = self._get_excel_paths()
        excel_target_path = (
            excel_paths.get("target_path", "Not set") if excel_paths else "Not set"
        )

        self.url_display = QLabel(excel_target_path)
        self.url_display.setWordWrap(True)
        # Use theme-aware colors
        from gui.theme_manager import ThemeManager, ThemeMode

        theme = ThemeManager.instance()
        colors = theme.get_current_colors()
        bg_color = (
            colors.base_bg
            if theme._current_resolved_mode == ThemeMode.DARK
            else "#f0f0f0"
        )
        self.url_display.setStyleSheet(
            f"color: {colors.link}; padding: 5px; background-color: {bg_color}; border-radius: 3px;"
        )
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

        # Check if Excel file is set
        if excel_target_path == "Not set":
            self.output_text.append("⚠️  Excel file is not set. Please complete Step 1 first.")
            self.log_manager.warning("Excel file is not set. Please complete Step 1 first.", batch_id=self.batch_id, step=2)
            self.convert_btn.setEnabled(False)
        else:
            self.output_text.append("Ready to convert Excel spreadsheet to CSV.")
            self.output_text.append(f"Target: {excel_target_path}")
            self.log_manager.info("Ready to convert Excel spreadsheet to CSV.", batch_id=self.batch_id, step=2)
            self.log_manager.info(f"Target: {excel_target_path}", batch_id=self.batch_id, step=2)

    def _start_conversion(self):
        """Start the CSV conversion process."""
        self.log_manager.step_start(2, "CSV Conversion", batch_id=self.batch_id)

        excel_paths = self._get_excel_paths()
        excel_target_path = excel_paths.get("target_path") if excel_paths else None

        if not excel_target_path:
            message = "Excel file is not set. Please complete Step 1 first."
            self.log_manager.warning(f"Missing Excel File: {message}", batch_id=self.batch_id, step=2)
            QMessageBox.warning(
                self,
                "Missing Excel File",
                message,
            )
            return

        # Create and start conversion thread
        data_dir = self.config_manager.get('project.data_directory')
        output_csv_path = str(Path(data_dir) / "output" / "csv" / "export.csv")
        self.conversion_thread = CSVConversionThread(
            excel_target_path, output_csv_path
        )
        self.conversion_thread.progress.connect(self._on_progress)
        self.conversion_thread.finished.connect(self._on_finished)
        self.conversion_thread.error.connect(self._on_error)

        # Enable convert button, disable close during conversion
        self.convert_btn.setEnabled(False)

        # Clear previous output
        self.output_text.clear()

        self.conversion_thread.start()

    def _on_progress(self, message):
        """Handle progress messages."""
        self.output_text.append(message)
        self.log_manager.info(message, batch_id=self.batch_id, step=2)

    def _on_finished(self, success, result=None):
        """Handle conversion completion.

        Args:
            success: Whether the conversion was successful
            result: CSVExportResult object with conversion details
        """
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)

        if success:
            self.output_text.append("")
            self.output_text.append("✓ CSV conversion completed successfully!")

            self.log_manager.step_complete(2, "CSV Conversion", batch_id=self.batch_id)
            self.config_manager.update_step_status(2, True)

            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(), self.config_manager.config_path
                )

            self.log_manager.success("CSV conversion completed successfully!", batch_id=self.batch_id, step=2)

            # Add batch title to cell A2 of export.csv
            try:
                # Get the batch title (project name)
                batch_title = self.config_manager.get("project.name", "")

                if batch_title:
                    import pandas as pd

                    csv_path = (
                        Path(self.config_manager.get('project.data_directory'))
                        / "output"
                        / "csv"
                        / "export.csv"
                    )
                    if csv_path.exists():
                        df = pd.read_csv(csv_path)
                        if len(df) > 1:  # Check if there are rows beyond header
                            df.iloc[1, 0] = (
                                batch_title  # Set cell A2 (index 1, column 0)
                            )
                            df.to_csv(csv_path, index=False)
                            self.output_text.append(f"Added batch title '{batch_title}' to CSV")
                            self.log_manager.info(
                                f"Added batch title '{batch_title}' to CSV",
                                batch_id=self.batch_id,
                                step=2
                            )
            except Exception as e:
                self.output_text.append(f"⚠️  Error adding batch title to CSV: {e}")
                self.log_manager.error(
                    f"Error adding batch title to CSV: {e}",
                    batch_id=self.batch_id,
                    step=2,
                )

            # Display and log non-standard dates if present
            if result and result.nonstandard_dates:
                self._display_nonstandard_dates(result.nonstandard_dates)
                self._log_nonstandard_dates(result.nonstandard_dates)

            # Show completion message
            QMessageBox.information(
                self,
                "Conversion Complete",
                "CSV conversion completed successfully!\n\nStep 2 is now marked as complete."
            )

            # Close dialog to update UI
            self.accept()

    def _display_nonstandard_dates(self, nonstandard_dates):
        """Display non-standard dates report in the output text area.

        Args:
            nonstandard_dates: List of NonStandardDateRecord objects
        """
        if not nonstandard_dates:
            return

        partial_dates = [d for d in nonstandard_dates if d.date_type == "partial"]
        placeholder_dates = [d for d in nonstandard_dates if d.date_type == "placeholder"]

        self.output_text.append("")
        self.output_text.append("=" * 50)
        self.output_text.append("NON-STANDARD DATES REPORT")
        self.output_text.append("=" * 50)

        if partial_dates:
            self.output_text.append(f"\nPartial Dates ({len(partial_dates)}):")
            for d in partial_dates:
                self.output_text.append(f"  Row {d.row_num}: {d.object_name} - \"{d.date_value}\" (from {d.source})")

        if placeholder_dates:
            self.output_text.append(f"\nPlaceholder Dates ({len(placeholder_dates)}):")
            for d in placeholder_dates:
                self.output_text.append(f"  Row {d.row_num}: {d.object_name} - \"{d.date_value}\"")

    def _log_nonstandard_dates(self, nonstandard_dates):
        """Log non-standard dates to the batch log file.

        Args:
            nonstandard_dates: List of NonStandardDateRecord objects
        """
        if not nonstandard_dates:
            return

        # Log summary
        self.log_manager.warning(
            f"Non-standard dates found: {len(nonstandard_dates)} records",
            batch_id=self.batch_id,
            step=2
        )

        # Log each non-standard date
        for d in nonstandard_dates:
            self.log_manager.warning(
                f"Non-standard date - Row {d.row_num}: {d.object_name} = \"{d.date_value}\" ({d.date_type}, source: {d.source})",
                batch_id=self.batch_id,
                step=2
            )

    def _on_error(self, error_msg):
        """Handle conversion errors."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        
        self.output_text.append("")
        self.output_text.append(f"❌ Error: {error_msg}")
        
        self.log_manager.error(error_msg, batch_id=self.batch_id, step=2)

    def _get_excel_paths(self):
        """Get Excel file paths from Step 1 configuration."""
        try:
            if not self.config_manager.get("step_configurations.step1"):
                return {}

            excel_paths = {
                "source_path": self.config_manager.get(
                    "step_configurations.step1.excel_source_path"
                ),
                "target_path": self.config_manager.get(
                    "step_configurations.step1.excel_target_path"
                ),
            }
            return excel_paths
        except Exception as e:
            self.log_manager.error(
                f"Error getting Excel paths: {e}", batch_id=self.batch_id, step=2
            )
            return {}
