"""
Step Execution Widget

Interface for executing and monitoring the 8 processing steps.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QProgressBar, QTextEdit, QGroupBox, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QUrl
from PyQt6.QtGui import QColor, QPalette, QDesktopServices


STEP_NAMES = {
    1: "Google Worksheet Completed",
    2: "Create export.csv file",
    3: "Test for Unicode scrabbling",
    4: "Test/Convert 16 Bit TIFFs",
    5: "Metadata Embedding of TIFF images",
    6: "JPEG Conversion",
    7: "JPEG Resizing",
    8: "Watermark Restricted JPEGs"
}


class StepWidget(QWidget):
    """Widget for executing processing steps."""
    
    step_executed = pyqtSignal(int, bool)  # step_num, success
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.framework = None
        self.batch_id = None
        self.batch_info = None
        self.step_buttons = {}
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Batch info section with version/date on same line
        batch_header_layout = QHBoxLayout()
        
        self.batch_label = QLabel("<h2>No batch selected</h2>")
        batch_header_layout.addWidget(self.batch_label)
        
        batch_header_layout.addStretch()
        
        # Version and date/time stamp (right-aligned, 10pt font)
        version_label = QLabel("<span style='font-size: 10pt;'>v0.1.3d | 2026-01-03 19:10 CST</span>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        batch_header_layout.addWidget(version_label)
        
        layout.addLayout(batch_header_layout)
        
        self.batch_status_label = QLabel("Select a batch from the Batches tab to begin")
        layout.addWidget(self.batch_status_label)
        
        layout.addSpacing(20)
        
        # Steps section
        steps_group = QGroupBox("Processing Steps")
        steps_layout = QVBoxLayout(steps_group)
        
        # Create grid for step buttons
        # Steps arranged vertically: column 1 has steps 1-4, column 2 has steps 5-8
        grid_layout = QGridLayout()
        
        # Set column stretch so both columns expand equally
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        
        for step_num in range(1, 9):
            # Steps 1-4 go in column 0, steps 5-8 go in column 1
            if step_num <= 4:
                row = step_num - 1  # 0, 1, 2, 3
                col = 0
            else:
                row = step_num - 5  # 0, 1, 2, 3
                col = 1
            
            step_widget = self._create_step_button(step_num)
            grid_layout.addWidget(step_widget, row, col)
            
        steps_layout.addLayout(grid_layout)
        
        # Batch action buttons - centered
        action_layout = QHBoxLayout()
        
        # Add stretch before buttons to center them
        action_layout.addStretch()
        
        self.run_all_btn = QPushButton("Run All Steps")
        self.run_all_btn.setEnabled(False)
        self.run_all_btn.clicked.connect(self._run_all_steps)
        action_layout.addWidget(self.run_all_btn)
        
        self.run_next_btn = QPushButton("Run Next Step")
        self.run_next_btn.setEnabled(False)
        self.run_next_btn.clicked.connect(self._run_next_step)
        action_layout.addWidget(self.run_next_btn)
        
        self.validate_btn = QPushButton("Validate All")
        self.validate_btn.setEnabled(False)
        self.validate_btn.clicked.connect(self._validate_all)
        action_layout.addWidget(self.validate_btn)
        
        self.reports_btn = QPushButton("Reports")
        self.reports_btn.setEnabled(False)
        self.reports_btn.setToolTip("Open reports directory")
        self.reports_btn.clicked.connect(self._open_reports_directory)
        action_layout.addWidget(self.reports_btn)
        
        # Add stretch after buttons to center them
        action_layout.addStretch()
        
        steps_layout.addLayout(action_layout)
        
        layout.addWidget(steps_group)
        
        # Output section
        output_group = QGroupBox("Output / Logs")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        output_layout.addWidget(self.output_text)
        
        layout.addWidget(output_group)
        
    def _create_step_button(self, step_num: int):
        """Create a step button widget."""
        widget = QWidget()
        # Set size policy to expand horizontally and vertically
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Step header
        header_layout = QHBoxLayout()
        
        step_label = QLabel(f"<b>Step {step_num}</b>")
        header_layout.addWidget(step_label)
        
        status_label = QLabel("⭕ Pending")
        status_label.setObjectName(f"status_{step_num}")
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Step name - larger and bold
        name_label = QLabel(f"<b>{STEP_NAMES[step_num]}</b>")
        name_label.setWordWrap(True)
        # Increase font size by 2 points
        font = name_label.font()
        font.setPointSize(font.pointSize() + 2)
        name_label.setFont(font)
        layout.addWidget(name_label)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Run button
        run_btn = QPushButton("Run")
        run_btn.setEnabled(False)
        run_btn.clicked.connect(lambda: self._run_step(step_num))
        buttons_layout.addWidget(run_btn)
        
        # Review button
        review_btn = QPushButton("Review")
        review_btn.setEnabled(False)
        review_btn.setToolTip("Review information about this step")
        review_btn.clicked.connect(lambda: self._review_step(step_num))
        buttons_layout.addWidget(review_btn)
        
        # Revert button
        revert_btn = QPushButton("Revert")
        revert_btn.setEnabled(False)
        revert_btn.setToolTip("Reset this step to Pending status")
        revert_btn.clicked.connect(lambda: self._revert_step(step_num))
        buttons_layout.addWidget(revert_btn)
        
        layout.addLayout(buttons_layout)
        
        # Store button references
        self.step_buttons[step_num] = {
            'widget': widget,
            'button': run_btn,
            'review_button': review_btn,
            'revert_button': revert_btn,
            'status': status_label
        }
        
        return widget
        
    def set_batch(self, framework, batch_id: str, batch_info: dict):
        """Set the current batch."""
        self.framework = framework
        self.batch_id = batch_id
        self.batch_info = batch_info
        
        # Update UI
        self.batch_label.setText(f"<h2>{batch_info['name']}</h2>")
        
        # Count completed steps directly from config instead of relying on batch_info
        completed = 0
        for step_num in range(1, 9):
            if self.framework.config_manager.get_step_status(step_num):
                completed += 1
        
        total = 8
        percentage = (completed / total * 100) if total > 0 else 0
        
        self.batch_status_label.setText(
            f"Progress: {completed}/{total} steps ({percentage:.0f}%) | "
            f"Status: {batch_info.get('status', 'unknown')}"
        )
        
        # Enable buttons
        self.run_all_btn.setEnabled(True)
        self.run_next_btn.setEnabled(True)
        self.validate_btn.setEnabled(True)
        self.reports_btn.setEnabled(True)
        
        # Update step statuses
        self._update_step_statuses()
        
        # Clear output
        self.output_text.clear()
        self.output_text.append(f"Loaded batch: {batch_info['name']}\n")
        
    def _update_step_statuses(self):
        """Update the status of all steps."""
        if not self.framework:
            return
            
        for step_num in range(1, 9):
            completed = self.framework.config_manager.get_step_status(step_num)
            
            status_label = self.step_buttons[step_num]['status']
            run_btn = self.step_buttons[step_num]['button']
            review_btn = self.step_buttons[step_num]['review_button']
            revert_btn = self.step_buttons[step_num]['revert_button']
            
            if completed:
                status_label.setText("✅ Completed")
                run_btn.setEnabled(True)  # Can re-run
                review_btn.setEnabled(True)  # Can review
                revert_btn.setEnabled(True)  # Can revert
            else:
                status_label.setText("⭕ Pending")
                run_btn.setEnabled(True)
                review_btn.setEnabled(True)  # Can always review
                revert_btn.setEnabled(False)  # Cannot revert pending
    
    def _update_batch_progress(self):
        """Update the batch progress display."""
        if not self.framework or not self.batch_info:
            return
        
        # Count completed steps from config
        completed = 0
        for step_num in range(1, 9):
            if self.framework.config_manager.get_step_status(step_num):
                completed += 1
        
        total = 8
        percentage = (completed / total * 100) if total > 0 else 0
        
        self.batch_status_label.setText(
            f"Progress: {completed}/{total} steps ({percentage:.0f}%) | "
            f"Status: {self.batch_info.get('status', 'unknown')}"
        )
                
    def _run_step(self, step_num: int):
        """Run a specific step."""
        if not self.framework:
            return
        
        # Step 1 has a special dialog
        if step_num == 1:
            self._run_step_1()
            return
        
        # Step 2 has a special dialog
        if step_num == 2:
            self._run_step_2()
            return
        
        # Step 3 has a special dialog
        if step_num == 3:
            self._run_step_3()
            return
        
        # Step 4 has a special dialog
        if step_num == 4:
            self._run_step_4()
            return
        
        # Step 5 has a special dialog
        if step_num == 5:
            self._run_step_5()
            return
        
        # Step 6 has a special dialog
        if step_num == 6:
            self._run_step_6()
            return
        
        # Step 7 has a special dialog
        if step_num == 7:
            self._run_step_7()
            return
        
        # Step 8 has a special dialog
        if step_num == 8:
            self._run_step_8()
            return
            
        self.output_text.append(f"\n--- Running Step {step_num}: {STEP_NAMES[step_num]} ---\n")
        
        # Update status to running
        status_label = self.step_buttons[step_num]['status']
        status_label.setText("🔄 Running...")
        
        # Run the step
        try:
            success = self.framework.run_steps([step_num], dry_run=False)
            
            if success:
                self.output_text.append(f"✅ Step {step_num} completed successfully\n")
                status_label.setText("✅ Completed")
                
                # Update config
                self.framework.config_manager.update_step_status(step_num, True)
                
                # Save config
                if self.framework.config_manager.config_path:
                    self.framework.config_manager.save_config(
                        self.framework.config_manager.to_dict(),
                        self.framework.config_manager.config_path
                    )
                
                self.step_executed.emit(step_num, True)
            else:
                self.output_text.append(f"❌ Step {step_num} failed\n")
                status_label.setText("❌ Failed")
                self.step_executed.emit(step_num, False)
                
        except Exception as e:
            self.output_text.append(f"❌ Error: {str(e)}\n")
            status_label.setText("❌ Error")
            self.step_executed.emit(step_num, False)
            
        # Update statuses and progress
        self._update_step_statuses()
        self._update_batch_progress()
    
    def _run_step_1(self):
        """Run Step 1: Google Worksheet Preparation (special dialog)."""
        from gui.dialogs.step1_dialog import Step1Dialog
        
        self.output_text.append(f"\n--- Running Step 1: {STEP_NAMES[1]} ---\n")
        
        # Open the Step 1 dialog
        dialog = Step1Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (Save clicked)
            url = dialog.get_url()
            self.output_text.append(f"✅ Google Worksheet URL saved: {url}\n")
            self.output_text.append("✅ Step 1 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(1, True)
        else:
            # Dialog was cancelled
            self.output_text.append("❌ Step 1 cancelled by user\n")
    
    def _run_step_2(self):
        """Run Step 2: CSV Conversion (special dialog)."""
        from gui.dialogs.step2_dialog import Step2Dialog
        
        self.output_text.append(f"\n--- Running Step 2: {STEP_NAMES[2]} ---\n")
        
        # Open the Step 2 dialog
        dialog = Step2Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (conversion succeeded)
            self.output_text.append("✅ CSV conversion completed\n")
            self.output_text.append("✅ Step 2 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(2, True)
        else:
            # Dialog was cancelled or conversion failed
            self.output_text.append("❌ Step 2 cancelled or failed\n")
    
    def _run_step_3(self):
        """Run Step 3: Unicode Filtering (special dialog)."""
        from gui.dialogs.step3_dialog import Step3Dialog
        
        self.output_text.append(f"\n--- Running Step 3: {STEP_NAMES[3]} ---\n")
        
        # Open the Step 3 dialog
        dialog = Step3Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (mojibake fixes applied or skipped)
            self.output_text.append("✅ Unicode filtering completed\n")
            self.output_text.append("✅ Step 3 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(3, True)
        else:
            # Dialog was cancelled
            self.output_text.append("❌ Step 3 cancelled by user\n")
    
    def _run_step_4(self):
        """Run Step 4: TIFF Bit Depth Conversion (special dialog)."""
        from gui.dialogs.step4_dialog import Step4Dialog
        
        self.output_text.append(f"\n--- Running Step 4: {STEP_NAMES[4]} ---\n")
        
        # Open the Step 4 dialog
        dialog = Step4Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (conversion succeeded)
            self.output_text.append("✅ Bit depth conversion completed\n")
            self.output_text.append("✅ Step 4 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(4, True)
        else:
            # Dialog was cancelled or conversion failed
            self.output_text.append("❌ Step 4 cancelled or failed\n")
    
    def _run_step_5(self):
        """Run Step 5: Metadata Embedding (special dialog)."""
        from gui.dialogs.step5_dialog import Step5Dialog
        
        self.output_text.append(f"\n--- Running Step 5: {STEP_NAMES[5]} ---\n")
        
        # Open the Step 5 dialog
        dialog = Step5Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (embedding succeeded)
            self.output_text.append("✅ Metadata embedding completed\n")
            self.output_text.append("✅ Step 5 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(5, True)
        else:
            # Dialog was cancelled or embedding failed
            self.output_text.append("❌ Step 5 cancelled or failed\n")
    
    def _run_step_6(self):
        """Run Step 6: JPEG Conversion (special dialog)."""
        from gui.dialogs.step6_dialog import Step6Dialog
        
        self.output_text.append(f"\n--- Running Step 6: {STEP_NAMES[6]} ---\n")
        
        # Open the Step 6 dialog
        dialog = Step6Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (conversion succeeded)
            self.output_text.append("✅ JPEG conversion completed\n")
            self.output_text.append("✅ Step 6 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(6, True)
        else:
            # Dialog was cancelled or conversion failed
            self.output_text.append("❌ Step 6 cancelled or failed\n")
    
    def _run_step_7(self):
        """Run Step 7: JPEG Resizing (special dialog)."""
        from gui.dialogs.step7_dialog import Step7Dialog
        
        self.output_text.append(f"\n--- Running Step 7: {STEP_NAMES[7]} ---\n")
        
        # Open the Step 7 dialog
        dialog = Step7Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (resize succeeded)
            self.output_text.append("✅ JPEG resizing completed\n")
            self.output_text.append("✅ Step 7 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(7, True)
        else:
            # Dialog was cancelled or resize failed
            self.output_text.append("❌ Step 7 cancelled or failed\n")
    
    def _run_step_8(self):
        """Run Step 8: Watermark Addition (special dialog)."""
        from gui.dialogs.step8_dialog import Step8Dialog
        
        self.output_text.append(f"\n--- Running Step 8: {STEP_NAMES[8]} ---\n")
        
        # Open the Step 8 dialog
        dialog = Step8Dialog(self.framework.config_manager, self)
        
        if dialog.exec():
            # Dialog was accepted (watermarking succeeded)
            self.output_text.append("✅ Watermarking completed\n")
            self.output_text.append("✅ Step 8 marked as complete\n")
            
            # Update status and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal
            self.step_executed.emit(8, True)
        else:
            # Dialog was cancelled or watermarking failed
            self.output_text.append("❌ Step 8 cancelled or failed\n")
    
    def _review_step(self, step_num: int):
        """Show review information for a step."""
        if not self.framework:
            return
        
        # Special handling for Step 2 - Open CSV directory
        if step_num == 2:
            self._review_step_2_open_directory()
            return
        
        # Special handling for Step 4 - Open TIFF directory
        if step_num == 4:
            self._review_step_4_open_directory()
            return
        
        # Special handling for Step 5 - Launch TagWriter
        if step_num == 5:
            self._review_step_5_with_tagwriter()
            return
        
        # Special handling for Step 6 - Open JPEG directory
        if step_num == 6:
            self._review_step_6_open_directory()
            return
        
        # Special handling for Step 7 - Open resized JPEG directory
        if step_num == 7:
            self._review_step_7_open_directory()
            return
        
        # Special handling for Step 8 - Open watermarked JPEG directory
        if step_num == 8:
            self._review_step_8_open_directory()
            return
        
        # Get step configuration
        step_config = self.framework.config_manager.get(f'step_configurations.step{step_num}', {})
        completed = self.framework.config_manager.get_step_status(step_num)
        
        # Build review information
        review_text = f"<h3>Step {step_num}: {STEP_NAMES[step_num]}</h3>"
        review_text += f"<p><b>Status:</b> {'✅ Completed' if completed else '⭕ Pending'}</p>"
        
        # Add step-specific information
        if step_num == 1:
            worksheet_url = step_config.get('worksheet_url', 'Not set')
            required_fields = step_config.get('required_fields', [])
            review_text += f"<p><b>Google Worksheet URL:</b><br>{worksheet_url}</p>"
            review_text += f"<p><b>Required Fields:</b><br>" + ', '.join(required_fields) + "</p>"
        elif step_num == 2:
            output_file = step_config.get('output_filename', 'export.csv')
            review_text += f"<p><b>Output File:</b> {output_file}</p>"
            review_text += f"<p><b>Validate Row Count:</b> {step_config.get('validate_row_count', False)}</p>"
        elif step_num == 3:
            review_text += f"<p><b>Generate Reports:</b> {step_config.get('generate_reports', False)}</p>"
            review_text += f"<p><b>Backup Original:</b> {step_config.get('backup_original', False)}</p>"
            review_text += f"<p><b>Encoding:</b> {step_config.get('encoding', 'utf-8')}</p>"
        elif step_num == 4:
            review_text += f"<p><b>Target Bit Depth:</b> {step_config.get('target_bit_depth', 8)}</p>"
            review_text += f"<p><b>Backup Original:</b> {step_config.get('backup_original', False)}</p>"
            review_text += f"<p><b>Quality Check:</b> {step_config.get('quality_check', False)}</p>"
        elif step_num == 6:
            review_text += f"<p><b>Quality:</b> {step_config.get('quality', 85)}</p>"
            review_text += f"<p><b>Validate Count:</b> {step_config.get('validate_count', False)}</p>"
            review_text += f"<p><b>Preserve Metadata:</b> {step_config.get('preserve_metadata', False)}</p>"
        elif step_num == 7:
            review_text += f"<p><b>Max Dimension:</b> {step_config.get('max_dimension', 800)}px</p>"
            review_text += f"<p><b>Maintain Aspect Ratio:</b> {step_config.get('maintain_aspect_ratio', False)}</p>"
            review_text += f"<p><b>Quality:</b> {step_config.get('quality', 85)}</p>"
        elif step_num == 8:
            review_text += f"<p><b>Watermark Opacity:</b> {step_config.get('watermark_opacity', 0.3)}</p>"
            review_text += f"<p><b>Watermark Position:</b> {step_config.get('watermark_position', 'bottom_right')}</p>"
            review_text += f"<p><b>Only Restricted:</b> {step_config.get('only_restricted', False)}</p>"
        
        # Show in message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Review Step {step_num}")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(review_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def _review_step_2_open_directory(self):
        """Open CSV directory to review export.csv file."""
        from pathlib import Path
        
        # Get the CSV output directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        csv_dir = Path(data_directory) / 'output' / 'csv'
        
        # Check if directory exists
        if not csv_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"CSV output directory not found:\n\n{csv_dir}\n\n"
                "Have you run Step 2 yet?"
            )
            return
        
        # Open directory in File Explorer using QDesktopServices
        try:
            url = QUrl.fromLocalFile(str(csv_dir))
            if QDesktopServices.openUrl(url):
                self.output_text.append(f"✓ Opened CSV directory: {csv_dir}\n")
            else:
                QMessageBox.warning(
                    self,
                    "Failed to Open",
                    f"Could not open directory:\n\n{csv_dir}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open directory:\n\n{str(e)}"
            )
    
    def _review_step_4_open_directory(self):
        """Open TIFF input directory to review converted files."""
        from pathlib import Path
        
        # Get the TIFF input directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        tiff_dir = Path(data_directory) / 'input' / 'tiff'
        
        # Check if directory exists
        if not tiff_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"TIFF input directory not found:\n\n{tiff_dir}\n\n"
                "Have you set up the input directory?"
            )
            return
        
        # Open directory in File Explorer using QDesktopServices
        try:
            url = QUrl.fromLocalFile(str(tiff_dir))
            if QDesktopServices.openUrl(url):
                self.output_text.append(f"✓ Opened TIFF directory: {tiff_dir}\n")
            else:
                QMessageBox.warning(
                    self,
                    "Failed to Open",
                    f"Could not open directory:\n\n{tiff_dir}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open directory:\n\n{str(e)}"
            )
    
    def _review_step_5_with_tagwriter(self):
        """Launch TagWriter to review metadata in processed TIFF files."""
        import subprocess
        from pathlib import Path
        
        # Get the processed TIFF directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        tiff_processed_dir = Path(data_directory) / 'output' / 'tiff_processed'
        
        # Check if directory exists
        if not tiff_processed_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"Processed TIFF directory not found:\n\n{tiff_processed_dir}\n\n"
                "Have you run Step 5 yet?"
            )
            return
        
        # Get TagWriter path from config, or use default
        tagwriter_path = self.framework.config_manager.get('tools.tagwriter', None)
        
        # If not configured, try to find TagWriter in common locations
        if not tagwriter_path:
            # Common installation locations for TagWriter
            possible_paths = [
                Path("C:/Program Files/TagWriter/TagWriter.exe"),
                Path("C:/Program Files (x86)/TagWriter/TagWriter.exe"),
                Path("C:/TagWriter/TagWriter.exe"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    tagwriter_path = str(path)
                    break
        
        # If still not found, ask user
        if not tagwriter_path or not Path(tagwriter_path).exists():
            reply = QMessageBox.question(
                self,
                "TagWriter Not Found",
                f"TagWriter executable not found.\n\n"
                f"Would you like to open the processed TIFF directory in File Explorer instead?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Open directory in File Explorer using QDesktopServices
                try:
                    url = QUrl.fromLocalFile(str(tiff_processed_dir))
                    if QDesktopServices.openUrl(url):
                        self.output_text.append(f"✓ Opened directory: {tiff_processed_dir}\n")
                    else:
                        QMessageBox.warning(
                            self,
                            "Failed to Open",
                            f"Could not open directory:\n\n{tiff_processed_dir}"
                        )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to open directory:\n\n{str(e)}"
                    )
            return
        
        # Launch TagWriter with the processed TIFF directory
        try:
            # Launch TagWriter with directory as working directory
            subprocess.Popen([tagwriter_path], cwd=str(tiff_processed_dir))
            self.output_text.append(f"✓ Launched TagWriter in: {tiff_processed_dir}\n")
            
            QMessageBox.information(
                self,
                "TagWriter Launched",
                f"TagWriter has been launched to review metadata tags.\n\n"
                f"Directory: {tiff_processed_dir}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch TagWriter:\n\n{str(e)}\n\n"
                f"TagWriter path: {tagwriter_path}"
            )
    
    def _review_step_6_open_directory(self):
        """Open JPEG output directory to review converted files."""
        from pathlib import Path
        
        # Get the JPEG output directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
        
        # Check if directory exists
        if not jpeg_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"JPEG output directory not found:\n\n{jpeg_dir}\n\n"
                "Have you run Step 6 yet?"
            )
            return
        
        # Open directory in File Explorer using QDesktopServices
        try:
            url = QUrl.fromLocalFile(str(jpeg_dir))
            if QDesktopServices.openUrl(url):
                self.output_text.append(f"✓ Opened JPEG directory: {jpeg_dir}\n")
            else:
                QMessageBox.warning(
                    self,
                    "Failed to Open",
                    f"Could not open directory:\n\n{jpeg_dir}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open directory:\n\n{str(e)}"
            )
    
    def _review_step_7_open_directory(self):
        """Open resized JPEG output directory to review resized files."""
        from pathlib import Path
        
        # Get the resized JPEG output directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        resized_jpeg_dir = Path(data_directory) / 'output' / 'jpeg_resized'
        
        # Check if directory exists
        if not resized_jpeg_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"Resized JPEG output directory not found:\n\n{resized_jpeg_dir}\n\n"
                "Have you run Step 7 yet?"
            )
            return
        
        # Open directory in File Explorer using QDesktopServices
        try:
            url = QUrl.fromLocalFile(str(resized_jpeg_dir))
            if QDesktopServices.openUrl(url):
                self.output_text.append(f"✓ Opened resized JPEG directory: {resized_jpeg_dir}\n")
            else:
                QMessageBox.warning(
                    self,
                    "Failed to Open",
                    f"Could not open directory:\n\n{resized_jpeg_dir}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open directory:\n\n{str(e)}"
            )
    
    def _review_step_8_open_directory(self):
        """Open watermarked JPEG output directory to review watermarked files."""
        from pathlib import Path
        
        # Get the watermarked JPEG output directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        watermarked_jpeg_dir = Path(data_directory) / 'output' / 'jpeg_watermarked'
        
        # Check if directory exists
        if not watermarked_jpeg_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"Watermarked JPEG output directory not found:\n\n{watermarked_jpeg_dir}\n\n"
                "Have you run Step 8 yet?"
            )
            return
        
        # Open directory in File Explorer using QDesktopServices
        try:
            url = QUrl.fromLocalFile(str(watermarked_jpeg_dir))
            if QDesktopServices.openUrl(url):
                self.output_text.append(f"✓ Opened watermarked JPEG directory: {watermarked_jpeg_dir}\n")
            else:
                QMessageBox.warning(
                    self,
                    "Failed to Open",
                    f"Could not open directory:\n\n{watermarked_jpeg_dir}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open directory:\n\n{str(e)}"
            )
        
    def _run_all_steps(self):
        """Run all steps in sequence."""
        reply = QMessageBox.question(
            self,
            "Run All Steps",
            "This will run all 8 processing steps in sequence.\n\n"
            "This may take a while. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.output_text.append("\n=== Running All Steps ===\n")
            
            for step_num in range(1, 9):
                self._run_step(step_num)
                
            self.output_text.append("\n=== All Steps Completed ===\n")
            
    def _run_next_step(self):
        """Run the next pending step."""
        if not self.framework:
            return
            
        next_step = self.framework.config_manager.get_next_step()
        
        if next_step:
            self._run_step(next_step)
        else:
            QMessageBox.information(
                self,
                "All Steps Complete",
                "All steps have been completed for this batch."
            )
    
    def _revert_step(self, step_num: int):
        """Revert a completed step back to pending."""
        if not self.framework:
            return
        
        # Special handling for Steps 2, 4, 5, 6, 7, and 8 - offer to delete files
        if step_num == 2:
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed and DELETE the\n"
                f"export.csv file in the output/csv directory.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        elif step_num == 4:
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed and DELETE all files\n"
                f"in the input/tiff directory.\n\n"
                f"WARNING: Step 4 overwrites original 16-bit files with 8-bit versions.\n"
                f"Those original files cannot be recovered.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        elif step_num == 5:
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed and DELETE all files\n"
                f"in the output/tiff_processed directory.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        elif step_num == 6:
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed and DELETE all files\n"
                f"in the output/jpeg directory.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        elif step_num == 7:
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed and DELETE all files\n"
                f"in the output/jpeg_resized directory.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        elif step_num == 8:
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed and DELETE all files\n"
                f"in the output/jpeg_watermarked directory.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        else:
            # Confirm with user for other steps
            reply = QMessageBox.question(
                self,
                "Revert Step",
                f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
                f"This will mark the step as not completed. Output files will NOT be deleted.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.output_text.append(f"\n--- Reverting Step {step_num}: {STEP_NAMES[step_num]} ---\n")
            
            # Special handling for Steps 2, 4, 5, 6, 7, and 8 - delete files in output directories
            if step_num == 2:
                from pathlib import Path
                
                data_directory = self.framework.config_manager.get('project.data_directory', '')
                if data_directory:
                    csv_file = Path(data_directory) / 'output' / 'csv' / 'export.csv'
                    
                    if csv_file.exists():
                        try:
                            # Delete the export.csv file
                            csv_file.unlink()
                            self.output_text.append(f"✅ Deleted {csv_file}\n")
                        except Exception as e:
                            self.output_text.append(f"⚠️ Error deleting file: {str(e)}\n")
                            QMessageBox.warning(
                                self,
                                "Delete Error",
                                f"Failed to delete export.csv:\n\n{str(e)}"
                            )
            elif step_num == 4:
                from pathlib import Path
                
                data_directory = self.framework.config_manager.get('project.data_directory', '')
                if data_directory:
                    tiff_dir = Path(data_directory) / 'input' / 'tiff'
                    
                    if tiff_dir.exists():
                        try:
                            # Delete all files in the directory
                            file_count = 0
                            for file_path in tiff_dir.iterdir():
                                if file_path.is_file():
                                    file_path.unlink()
                                    file_count += 1
                            
                            self.output_text.append(f"✅ Deleted {file_count} files from {tiff_dir}\n")
                        except Exception as e:
                            self.output_text.append(f"⚠️ Error deleting files: {str(e)}\n")
                            QMessageBox.warning(
                                self,
                                "Delete Error",
                                f"Failed to delete some files:\n\n{str(e)}"
                            )
            elif step_num == 5:
                from pathlib import Path
                
                data_directory = self.framework.config_manager.get('project.data_directory', '')
                if data_directory:
                    tiff_processed_dir = Path(data_directory) / 'output' / 'tiff_processed'
                    
                    if tiff_processed_dir.exists():
                        try:
                            # Delete all files in the directory
                            file_count = 0
                            for file_path in tiff_processed_dir.iterdir():
                                if file_path.is_file():
                                    file_path.unlink()
                                    file_count += 1
                            
                            self.output_text.append(f"✅ Deleted {file_count} files from {tiff_processed_dir}\n")
                        except Exception as e:
                            self.output_text.append(f"⚠️ Error deleting files: {str(e)}\n")
                            QMessageBox.warning(
                                self,
                                "Delete Error",
                                f"Failed to delete some files:\n\n{str(e)}"
                            )
            elif step_num == 6:
                from pathlib import Path
                
                data_directory = self.framework.config_manager.get('project.data_directory', '')
                if data_directory:
                    jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
                    
                    if jpeg_dir.exists():
                        try:
                            # Delete all files in the directory
                            file_count = 0
                            for file_path in jpeg_dir.iterdir():
                                if file_path.is_file():
                                    file_path.unlink()
                                    file_count += 1
                            
                            self.output_text.append(f"✅ Deleted {file_count} files from {jpeg_dir}\n")
                        except Exception as e:
                            self.output_text.append(f"⚠️ Error deleting files: {str(e)}\n")
                            QMessageBox.warning(
                                self,
                                "Delete Error",
                                f"Failed to delete some files:\n\n{str(e)}"
                            )
            elif step_num == 7:
                from pathlib import Path
                
                data_directory = self.framework.config_manager.get('project.data_directory', '')
                if data_directory:
                    resized_jpeg_dir = Path(data_directory) / 'output' / 'jpeg_resized'
                    
                    if resized_jpeg_dir.exists():
                        try:
                            # Delete all files in the directory
                            file_count = 0
                            for file_path in resized_jpeg_dir.iterdir():
                                if file_path.is_file():
                                    file_path.unlink()
                                    file_count += 1
                            
                            self.output_text.append(f"✅ Deleted {file_count} files from {resized_jpeg_dir}\n")
                        except Exception as e:
                            self.output_text.append(f"⚠️ Error deleting files: {str(e)}\n")
                            QMessageBox.warning(
                                self,
                                "Delete Error",
                                f"Failed to delete some files:\n\n{str(e)}"
                            )
            elif step_num == 8:
                from pathlib import Path
                
                data_directory = self.framework.config_manager.get('project.data_directory', '')
                if data_directory:
                    watermarked_jpeg_dir = Path(data_directory) / 'output' / 'jpeg_watermarked'
                    
                    if watermarked_jpeg_dir.exists():
                        try:
                            # Delete all files in the directory
                            file_count = 0
                            for file_path in watermarked_jpeg_dir.iterdir():
                                if file_path.is_file():
                                    file_path.unlink()
                                    file_count += 1
                            
                            self.output_text.append(f"✅ Deleted {file_count} files from {watermarked_jpeg_dir}\n")
                        except Exception as e:
                            self.output_text.append(f"⚠️ Error deleting files: {str(e)}\n")
                            QMessageBox.warning(
                                self,
                                "Delete Error",
                                f"Failed to delete some files:\n\n{str(e)}"
                            )
            
            # Update status to pending
            status_label = self.step_buttons[step_num]['status']
            status_label.setText("⭕ Pending")
            
            # Update config
            self.framework.config_manager.update_step_status(step_num, False)
            
            # Save config
            if self.framework.config_manager.config_path:
                self.framework.config_manager.save_config(
                    self.framework.config_manager.to_dict(),
                    self.framework.config_manager.config_path
                )
            
            self.output_text.append(f"✅ Step {step_num} reverted to Pending\n")
            if step_num not in [2, 4, 5, 6, 7, 8]:
                self.output_text.append("Note: Output files were not deleted. Re-run the step to regenerate.\n")
            
            # Update statuses and progress
            self._update_step_statuses()
            self._update_batch_progress()
            
            # Emit signal to update batch list
            self.step_executed.emit(step_num, False)
            
    def _validate_all(self):
        """Validate all completed steps."""
        if not self.framework:
            return
            
        self.output_text.append("\n--- Running Validation ---\n")
        
        success = self.framework.validate()
        
        if success:
            self.output_text.append("✅ Validation passed\n")
            QMessageBox.information(self, "Validation", "All validations passed successfully")
        else:
            self.output_text.append("⚠️ Validation found issues\n")
            QMessageBox.warning(self, "Validation", "Validation found some issues. Check the output.")
    
    def _open_reports_directory(self):
        """Open the reports directory for the current batch."""
        if not self.framework:
            return
        
        from pathlib import Path
        
        # Get the reports directory
        data_directory = self.framework.config_manager.get('project.data_directory', '')
        if not data_directory:
            QMessageBox.warning(
                self,
                "No Data Directory",
                "Data directory is not configured for this batch."
            )
            return
        
        reports_dir = Path(data_directory) / 'reports'
        
        # Check if directory exists
        if not reports_dir.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"Reports directory not found:\n\n{reports_dir}\n\n"
                "Reports will be created when steps generate them."
            )
            return
        
        # Open directory in File Explorer using QDesktopServices
        try:
            url = QUrl.fromLocalFile(str(reports_dir))
            if QDesktopServices.openUrl(url):
                self.output_text.append(f"✓ Opened reports directory: {reports_dir}\n")
            else:
                QMessageBox.warning(
                    self,
                    "Failed to Open",
                    f"Could not open directory:\n\n{reports_dir}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open directory:\n\n{str(e)}"
            )
