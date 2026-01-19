"""
Step 3 Dialog - Unicode Filtering (Mojibake Detection)

Scans export.csv for mojibake and allows users to review and fix problematic records.
"""

import csv
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager


class MojibakeDetectionThread(QThread):
    """Worker thread for mojibake detection."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, list)  # Success/failure, list of problematic records
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, csv_path):
        super().__init__()
        self.csv_path = csv_path
        
    def run(self):
        """Scan CSV for mojibake."""
        try:
            import ftfy
            
            self.progress.emit("Starting mojibake detection...")
            self.progress.emit(f"Scanning: {self.csv_path}")
            
            problematic_records = []
            
            with open(self.csv_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Fields to check for mojibake
                text_fields = ['Headline', 'Caption-Abstract', 'Source', 'By-line', 
                              'By-lineTitle', 'CopyrightNotice']
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                    issues = {}
                    
                    for field in text_fields:
                        if field in row and row[field]:
                            original_text = row[field]
                            fixed_text = ftfy.fix_text(original_text)
                            
                            # Check if fixing changed the text
                            if fixed_text != original_text:
                                issues[field] = {
                                    'original': original_text,
                                    'suggested': fixed_text
                                }
                    
                    if issues:
                        record = {
                            'row_num': row_num,
                            'object_name': row.get('ObjectName', 'Unknown'),
                            'issues': issues,
                            'full_row': row
                        }
                        problematic_records.append(record)
                        self.progress.emit(f"⚠️  Row {row_num}: {row.get('ObjectName', 'Unknown')} - {len(issues)} issue(s)")
            
            if problematic_records:
                self.progress.emit(f"\n✓ Scan complete: {len(problematic_records)} record(s) with mojibake detected")
            else:
                self.progress.emit("\n✓ Scan complete: No mojibake detected")
            
            self.finished.emit(True, problematic_records)
            
        except ImportError:
            self.error.emit("ftfy library not found. Install with: pip install ftfy")
        except Exception as e:
            self.error.emit(f"Error during mojibake detection: {str(e)}")


class Step3Dialog(QDialog):
    """Dialog for Step 3: Unicode Filtering (Mojibake Detection)."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.detection_thread = None
        self.problematic_records = []
        self.current_record_index = 0
        self.edits = {}  # Store user edits: {row_num: {field: new_value}}
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 3: Unicode Filtering")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.resize(900, 600)  # Default size - fits most screens

        self.log_manager.debug("Opened Step 3 dialog", batch_id=batch_id, step=3)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        from PyQt6.QtWidgets import QScrollArea
        
        # Create scroll area for the entire dialog content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Title and description
        title_label = QLabel("<h2>Step 3: Unicode Filtering</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step scans the CSV file for mojibake (character encoding issues) "
            "and allows you to review and fix problematic records.</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status section
        status_label = QLabel("<b>Scan Status:</b>")
        layout.addWidget(status_label)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        layout.addWidget(self.status_text)
        
        layout.addSpacing(10)
        
        # Review section (initially hidden)
        self.review_group = QGroupBox("Review and Fix Mojibake")
        self.review_group.setVisible(False)
        review_layout = QVBoxLayout(self.review_group)
        
        # Record navigation
        nav_layout = QHBoxLayout()
        self.record_label = QLabel("Record: 0 / 0")
        nav_layout.addWidget(self.record_label)
        
        nav_layout.addStretch()
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._prev_record)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._next_record)
        nav_layout.addWidget(self.next_btn)
        
        review_layout.addLayout(nav_layout)
        
        # Record details
        self.record_info_label = QLabel()
        review_layout.addWidget(self.record_info_label)
        
        # Issues table
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(4)
        self.issues_table.setHorizontalHeaderLabels(['Field', 'Original Text', 'Suggested Fix', 'Action'])
        self.issues_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.issues_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.issues_table.setMinimumHeight(150)
        self.issues_table.setMaximumHeight(250)
        review_layout.addWidget(self.issues_table)
        
        layout.addWidget(self.review_group)
        
        layout.addSpacing(10)
        
        # Set the container in the scroll area
        scroll.setWidget(container)
        
        # Main layout for dialog
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        
        # Buttons (outside scroll area, always visible)
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("Scan for Mojibake")
        self.scan_btn.setDefault(True)
        self.scan_btn.clicked.connect(self._start_scan)
        button_layout.addWidget(self.scan_btn)
        
        self.apply_btn = QPushButton("Apply Fixes and Complete")
        self.apply_btn.setVisible(False)
        self.apply_btn.clicked.connect(self._apply_fixes)
        button_layout.addWidget(self.apply_btn)
        
        self.skip_btn = QPushButton("Skip (No Fixes)")
        self.skip_btn.setVisible(False)
        self.skip_btn.clicked.connect(self._skip_fixes)
        button_layout.addWidget(self.skip_btn)
        
        close_btn = QPushButton("Cancel")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.status_text.append("Ready to scan export.csv for mojibake.")
        self.log_manager.info("Ready to scan export.csv for mojibake.", batch_id=self.batch_id, step=3)
        
    def _start_scan(self):
        """Start the mojibake detection scan."""
        self.log_manager.step_start(3, "Unicode Filtering", batch_id=self.batch_id)
        data_directory = self.config_manager.get('project.data_directory', '')
        if not data_directory:
            self.log_manager.error("Project data directory not set", batch_id=self.batch_id, step=3)
            QMessageBox.warning(self, "Error", "Project data directory not set")
            return
        
        csv_path = Path(data_directory) / 'output' / 'csv' / 'export.csv'
        
        if not csv_path.exists():
            self.log_manager.error(f"CSV file not found: {csv_path}", batch_id=self.batch_id, step=3)
            QMessageBox.warning(self, "Error", f"CSV file not found: {csv_path}")
            return
        
        # Disable button and show progress
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Clear previous output
        self.status_text.clear()
        self.status_text.append("="*50)
        self.status_text.append("Starting mojibake scan...")
        
        self.log_manager.info("="*50, batch_id=self.batch_id, step=3)
        self.log_manager.info("Starting mojibake scan...", batch_id=self.batch_id, step=3)
        
        # Start detection thread
        self.detection_thread = MojibakeDetectionThread(str(csv_path))
        self.detection_thread.progress.connect(self._on_progress)
        self.detection_thread.finished.connect(self._on_scan_finished)
        self.detection_thread.error.connect(self._on_error)
        self.detection_thread.start()
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.status_text.append(message)
        self.log_manager.info(message, batch_id=self.batch_id, step=3)
        
    def _on_scan_finished(self, success, problematic_records):
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if not success:
            return
        
        self.problematic_records = problematic_records
        
        if problematic_records:
            self.status_text.append("")
            self.status_text.append(f"⚠️  Found {len(problematic_records)} record(s) with mojibake.")
            self.status_text.append("Review and fix the issues below.")
            
            self.log_manager.warning(f"Found {len(problematic_records)} record(s) with mojibake.", batch_id=self.batch_id, step=3)
            self.log_manager.info("Review and fix the issues below.", batch_id=self.batch_id, step=3)
            
            # Show review section
            self.review_group.setVisible(True)
            self.apply_btn.setVisible(True)
            self.skip_btn.setVisible(True)
            
            self.current_record_index = 0
            self._display_current_record()
        else:
            self.status_text.append("")
            self.status_text.append("✓ No mojibake detected! CSV is clean.")
            
            self.log_manager.success("No mojibake detected! CSV is clean.", batch_id=self.batch_id, step=3)
            
            # Mark step as complete
            self.config_manager.update_step_status(3, True)
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(3, "Unicode Filtering", batch_id=self.batch_id)
            self.log_manager.info("Step 3: No mojibake detected", batch_id=self.batch_id, step=3)

            message = "No mojibake detected in the CSV file.\n\n" \
                      "Step 3 is now marked as complete."
            self.log_manager.info(f"Scan Complete: {message}", batch_id=self.batch_id, step=3)
            QMessageBox.information(
                self,
                "Scan Complete",
                message
            )

            self.accept()
    
    def _on_error(self, error_msg):
        """Handle scan errors."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)

        self.status_text.append("")
        self.status_text.append(f"❌ Error: {error_msg}")
        
        self.log_manager.step_error(3, error_msg, batch_id=self.batch_id)
        
        message = f"Mojibake scan failed:\n\n{error_msg}"
        self.log_manager.critical(f"Scan Error: {message}", batch_id=self.batch_id, step=3)
        QMessageBox.critical(self, "Scan Error", message)
    
    def _display_current_record(self):
        """Display the current problematic record."""
        if not self.problematic_records or self.current_record_index >= len(self.problematic_records):
            return
        
        record = self.problematic_records[self.current_record_index]
        
        # Update record label
        self.record_label.setText(
            f"Record: {self.current_record_index + 1} / {len(self.problematic_records)}"
        )
        
        # Update record info
        self.record_info_label.setText(
            f"<b>Row {record['row_num']}</b>: {record['object_name']}"
        )
        
        # Update navigation buttons
        self.prev_btn.setEnabled(self.current_record_index > 0)
        self.next_btn.setEnabled(self.current_record_index < len(self.problematic_records) - 1)
        
        # Populate issues table
        self.issues_table.setRowCount(0)
        
        for field, issue in record['issues'].items():
            row = self.issues_table.rowCount()
            self.issues_table.insertRow(row)
            
            # Field name
            self.issues_table.setItem(row, 0, QTableWidgetItem(field))
            
            # Original text
            orig_item = QTableWidgetItem(issue['original'])
            orig_item.setBackground(Qt.GlobalColor.yellow)
            self.issues_table.setItem(row, 1, orig_item)
            
            # Suggested fix
            sugg_item = QTableWidgetItem(issue['suggested'])
            sugg_item.setBackground(Qt.GlobalColor.lightGreen)
            self.issues_table.setItem(row, 2, sugg_item)
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            
            accept_btn = QPushButton("✓ Use Suggested")
            accept_btn.clicked.connect(
                lambda checked, r=record['row_num'], f=field, v=issue['suggested']: 
                self._accept_suggestion(r, f, v)
            )
            action_layout.addWidget(accept_btn)
            
            edit_btn = QPushButton("✎ Edit")
            edit_btn.clicked.connect(
                lambda checked, r=record['row_num'], f=field, orig=issue['original'], sugg=issue['suggested']: 
                self._custom_edit(r, f, orig, sugg)
            )
            action_layout.addWidget(edit_btn)
            
            self.issues_table.setCellWidget(row, 3, action_widget)
    
    def _prev_record(self):
        """Navigate to previous record."""
        if self.current_record_index > 0:
            self.current_record_index -= 1
            self._display_current_record()
    
    def _next_record(self):
        """Navigate to next record."""
        if self.current_record_index < len(self.problematic_records) - 1:
            self.current_record_index += 1
            self._display_current_record()
    
    def _accept_suggestion(self, row_num, field, suggested_value):
        """Accept the suggested fix."""
        if row_num not in self.edits:
            self.edits[row_num] = {}
        self.edits[row_num][field] = suggested_value
        
        message = f"Suggested fix for '{field}' in row {row_num} will be applied."
        self.log_manager.info(f"Suggestion Accepted: {message}", batch_id=self.batch_id, step=3)
        QMessageBox.information(
            self,
            "Suggestion Accepted",
            message
        )
    
    def _custom_edit(self, row_num, field, original, suggested):
        """Allow user to enter custom fix."""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getMultiLineText(
            self,
            f"Edit {field}",
            f"Original: {original}\n\nSuggested: {suggested}\n\nEnter your fix:",
            suggested
        )
        
        if ok and text:
            if row_num not in self.edits:
                self.edits[row_num] = {}
            self.edits[row_num][field] = text
            
            message = f"Your custom fix for '{field}' in row {row_num} will be applied."
            self.log_manager.info(f"Custom Edit Saved: {message}", batch_id=self.batch_id, step=3)
            QMessageBox.information(
                self,
                "Custom Edit Saved",
                message
            )
    
    def _apply_fixes(self):
        """Apply all fixes to the CSV file."""
        apply_message = f"Apply fixes to {len(self.edits)} record(s)?\n\nThis will update the export.csv file."
        self.log_manager.info(f"User confirmation requested for applying fixes: {apply_message}", batch_id=self.batch_id, step=3)
        reply = QMessageBox.question(
            self,
            "Apply Fixes",
            apply_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.log_manager.info("User cancelled applying fixes.", batch_id=self.batch_id, step=3)
            return
        
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            csv_path = Path(data_directory) / 'output' / 'csv' / 'export.csv'
            
            # Read all rows
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)
            
            # Apply edits
            for row_num, field_edits in self.edits.items():
                # row_num starts at 2 (1 is header), so data index is row_num - 2
                data_index = row_num - 2
                if 0 <= data_index < len(rows):
                    for field, new_value in field_edits.items():
                        rows[data_index][field] = new_value
            
            # Write back to CSV
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            # Generate report
            self._generate_report()
            
            # Mark step as complete
            self.config_manager.update_step_status(3, True)
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(3, "Unicode Filtering", batch_id=self.batch_id)
            self.log_manager.info(f"Step 3: Applied {len(self.edits)} mojibake fix(es)", batch_id=self.batch_id, step=3)

            success_message = f"Successfully applied {len(self.edits)} fix(es) to the CSV file.\n\nStep 3 is now marked as complete."
            self.log_manager.success(f"Fixes Applied: {success_message}", batch_id=self.batch_id, step=3)
            QMessageBox.information(
                self,
                "Fixes Applied",
                success_message
            )

            self.accept()

        except Exception as e:
            self.log_manager.step_error(3, str(e), batch_id=self.batch_id, exc_info=True)
            error_message = f"Failed to apply fixes:\n\n{str(e)}"
            self.log_manager.critical(f"Error applying fixes: {error_message}", batch_id=self.batch_id, step=3)
            QMessageBox.critical(
                self,
                "Error",
                error_message
            )
    
    def _skip_fixes(self):
        """Skip fixes and mark step complete."""
        skip_message = "Skip mojibake fixes and mark step as complete?\n\n" \
                       "The CSV file will not be modified."
        self.log_manager.info(f"User confirmation requested for skipping fixes: {skip_message}", batch_id=self.batch_id, step=3)
        reply = QMessageBox.question(
            self,
            "Skip Fixes",
            skip_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Mark step as complete
            self.config_manager.update_step_status(3, True)
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )

            self.log_manager.step_complete(3, "Unicode Filtering", batch_id=self.batch_id)
            self.log_manager.info("Step 3: Skipped mojibake fixes", batch_id=self.batch_id, step=3)
            self.accept()
        else:
            self.log_manager.info("User cancelled skipping fixes.", batch_id=self.batch_id, step=3)
    
    def _generate_report(self):
        """Generate a report of mojibake fixes."""
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            report_dir = Path(data_directory) / 'reports'
            report_dir.mkdir(parents=True, exist_ok=True)
            
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"REPORT_MOJIBAKE_FIXES-{formatted_datetime}.txt"
            report_path = report_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("MOJIBAKE DETECTION AND FIXES REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Report generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(f"Total records scanned: {len(self.problematic_records)}\n")
                f.write(f"Records with mojibake: {len(self.problematic_records)}\n")
                f.write(f"Fixes applied: {len(self.edits)}\n")
                f.write("\n")
                f.write("FIXES APPLIED:\n")
                f.write("-" * 70 + "\n")
                
                for row_num, field_edits in self.edits.items():
                    # Find the record
                    record = next((r for r in self.problematic_records if r['row_num'] == row_num), None)
                    if record:
                        f.write(f"\nRow {row_num}: {record['object_name']}\n")
                        for field, new_value in field_edits.items():
                            original = record['issues'][field]['original']
                            f.write(f"  {field}:\n")
                            f.write(f"    Original: {original}\n")
                            f.write(f"    Fixed to: {new_value}\n")
                
                f.write("\n" + "=" * 70 + "\n")
            
            self.log_manager.success(f"Report saved: {report_filename}", batch_id=self.batch_id, step=3)
            
        except Exception as e:
            self.log_manager.warning(f"Failed to generate report: {str(e)}", batch_id=self.batch_id, step=3)
