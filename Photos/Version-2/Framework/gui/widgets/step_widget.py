"""
Step Execution Widget

Interface for executing and monitoring the 8 processing steps.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QProgressBar, QTextEdit, QGroupBox, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QColor, QPalette


STEP_NAMES = {
    1: "Google Worksheet Preparation",
    2: "CSV Conversion",
    3: "Unicode Filtering",
    4: "TIFF Bit Depth Conversion",
    5: "Metadata Embedding",
    6: "JPEG Conversion",
    7: "JPEG Resizing",
    8: "Watermark Addition"
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
        version_label = QLabel("<span style='font-size: 10pt;'>v0.0.3 | 2025-12-08 10:10</span>")
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
        
        # Batch action buttons
        action_layout = QHBoxLayout()
        
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
        
        # Step 5 has a special dialog
        if step_num == 5:
            self._run_step_5()
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
    
    def _review_step(self, step_num: int):
        """Show review information for a step."""
        if not self.framework:
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
        elif step_num == 5:
            review_text += f"<p><b>Generate Reports:</b> {step_config.get('generate_reports', False)}</p>"
            review_text += f"<p><b>Validate Embedding:</b> {step_config.get('validate_embedding', False)}</p>"
            review_text += f"<p><b>Backup on Error:</b> {step_config.get('backup_on_error', False)}</p>"
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
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Revert Step",
            f"Revert Step {step_num}: {STEP_NAMES[step_num]} to Pending?\n\n"
            f"This will mark the step as not completed. Output files will NOT be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.output_text.append(f"\n--- Reverting Step {step_num}: {STEP_NAMES[step_num]} ---\n")
            
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
