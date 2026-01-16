"""
Step 1 Dialog - Excel Spreadsheet Preparation

Allows user to select an Excel spreadsheet file, validate it, copy it to the project,
and marks Step 1 as complete.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QFileDialog,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager
from file_manager import FileManager


class Step1Dialog(QDialog):
    """Dialog for Step 1: Excel Spreadsheet Preparation."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 1: Excel Spreadsheet Preparation")
        self.setMinimumWidth(700)

        # Initialize file manager
        self.file_manager = None
        self.excel_target_path = None

        self.log_manager.debug("Opened Step 1 dialog", batch_id=batch_id, step=1)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Title and description
        title_label = QLabel("<h2>Step 1: Excel Spreadsheet Preparation</h2>")
        layout.addWidget(title_label)

        desc_label = QLabel(
            "<p>Select the Excel spreadsheet that contains the metadata for this batch. "
            "The file will be validated and copied to the project directory.</p>"
            "<p><b>Requirements:</b></p>"
            "<ul>"
            "<li>The spreadsheet must be in .xlsx or .xls format</li>"
            "<li>Row 1: Data headers</li>"
            "<li>Row 2: Must be blank</li>"
            "<li>Row 3: Required mapping headers (Title, Accession Number, Restrictions, Scopenote, Related Collection, Source Photographer, Institutional Creator)</li>"
            "<li>Row 4+: Metadata data</li>"
            "</ul>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addSpacing(20)

        # File selection section
        file_label = QLabel("<b>Excel Spreadsheet File:</b>")
        layout.addWidget(file_label)

        # File input with browse button
        file_layout = QHBoxLayout()

        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Select an Excel file (.xlsx or .xls)")
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(self.file_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_excel_file)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        # Progress and status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Copied file info
        self.copied_to_label = QLabel("")
        self.copied_to_label.setStyleSheet("color: #2E8B57; font-weight: bold;")
        self.copied_to_label.setWordWrap(True)
        layout.addWidget(self.copied_to_label)

        layout.addSpacing(20)

        # Buttons
        button_box = QDialogButtonBox()

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._validate_and_copy_excel)
        button_box.addButton(save_btn, QDialogButtonBox.ButtonRole.AcceptRole)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_box.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)

        layout.addWidget(button_box)

    def _browse_excel_file(self):
        """Open file browser to select Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel Spreadsheet",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)",
        )

        if file_path:
            self.file_edit.setText(file_path)
            self._validate_and_copy_excel()

    def _validate_and_copy_excel(self):
        """Validate Excel file and copy to project directory."""
        source_path = self.file_edit.text().strip()

        # Validate file selection
        if not source_path:
            self.log_manager.warning(
                "Step 1: Excel file is required but was empty",
                batch_id=self.batch_id,
                step=1,
            )
            QMessageBox.warning(
                self, "File Required", "Please select an Excel spreadsheet file."
            )
            return

        # Validate file extension
        if not source_path.lower().endswith((".xlsx", ".xls")):
            self.log_manager.warning(
                f"Step 1: Invalid file format - {source_path}",
                batch_id=self.batch_id,
                step=1,
            )
            QMessageBox.warning(
                self,
                "Invalid File Format",
                "Please select an Excel file with .xlsx or .xls extension.",
            )
            return

        # Initialize file manager if needed
        if not self.file_manager:
            if not self.config_manager.get_data_directory():
                self.log_manager.error(
                    "Step 1: No data directory found", batch_id=self.batch_id, step=1
                )
                QMessageBox.critical(
                    self,
                    "Configuration Error",
                    "No project data directory found. Please create or select a project first.",
                )
                return

            self.file_manager = FileManager(self.config_manager.get_data_directory())

        # Show progress
        self.status_label.setText("Validating Excel file...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Validate file structure
        self.log_manager.step_start(
            1, "Excel Spreadsheet Preparation", batch_id=self.batch_id
        )

        try:
            is_valid, message = self.file_manager.validate_hpm_excel_structure(
                source_path
            )

            if not is_valid:
                self.progress_bar.setVisible(False)
                self.log_manager.warning(
                    f"Step 1: Excel validation failed - {message}",
                    batch_id=self.batch_id,
                    step=1,
                )
                QMessageBox.critical(
                    self,
                    "Validation Error",
                    f"The selected Excel file is not valid for HPM processing:\n\n{message}",
                )
                return

            # Copy file to project directory
            self.status_label.setText("Copying Excel file to project...")
            success, message, target_path = self.file_manager.copy_excel_to_input(
                source_path
            )

            self.progress_bar.setVisible(False)

            if not success:
                self.log_manager.error(
                    f"Step 1: File copy failed - {message}",
                    batch_id=self.batch_id,
                    step=1,
                )
                QMessageBox.critical(
                    self, "File Copy Error", f"Failed to copy Excel file:\n\n{message}"
                )
                return

            # Success!
            self.excel_target_path = target_path
            self.copied_to_label.setText(f"Copied to: {target_path}")
            self.status_label.setText("Excel file successfully validated and copied!")

            # Update configuration
            if not self.config_manager.get("step_configurations.step1"):
                self.config_manager.set("step_configurations.step1", {})

            # Save file paths
            self.config_manager.set(
                "step_configurations.step1.excel_source_path", source_path
            )
            self.config_manager.set(
                "step_configurations.step1.excel_target_path", target_path
            )

            # Mark step 1 as completed
            self.config_manager.update_step_status(1, True)

            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(), self.config_manager.config_path
                )

                self.log_manager.step_complete(
                    1, "Excel Spreadsheet Preparation", batch_id=self.batch_id
                )
                self.log_manager.info(
                    f"Step 1: Excel file processed successfully",
                    batch_id=self.batch_id,
                    step=1,
                )

                QMessageBox.information(
                    self,
                    "Step 1 Complete",
                    f"Excel spreadsheet processed successfully!\n\n"
                    f"Step 1 is now marked as complete.\n\n"
                    f"Source: {source_path}\n"
                    f"Target: {target_path}",
                )

                self.accept()
            else:
                self.log_manager.error(
                    "Step 1: No config file path found", batch_id=self.batch_id, step=1
                )
                QMessageBox.warning(
                    self,
                    "Save Error",
                    "Could not save configuration: No config file path found.",
                )

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.log_manager.step_error(
                1, str(e), batch_id=self.batch_id, exc_info=True
            )
            QMessageBox.critical(
                self, "Error", f"Failed to process Excel file:\n{str(e)}"
            )

    def get_excel_paths(self):
        """Get the source and target Excel file paths."""
        if self.excel_target_path:
            return {
                "source_path": self.config_manager.get(
                    "step_configurations.step1.excel_source_path"
                ),
                "target_path": self.excel_target_path,
            }
        return None
