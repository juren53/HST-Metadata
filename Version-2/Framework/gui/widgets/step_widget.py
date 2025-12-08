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
        
        # Batch info section
        self.batch_label = QLabel("<h2>No batch selected</h2>")
        layout.addWidget(self.batch_label)
        
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
        
        completed = batch_info.get('completed_steps', 0)
        total = batch_info.get('total_steps', 8)
        percentage = batch_info.get('completion_percentage', 0)
        
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
            revert_btn = self.step_buttons[step_num]['revert_button']
            
            if completed:
                status_label.setText("✅ Completed")
                run_btn.setEnabled(True)  # Can re-run
                revert_btn.setEnabled(True)  # Can revert
            else:
                status_label.setText("⭕ Pending")
                run_btn.setEnabled(True)
                revert_btn.setEnabled(False)  # Cannot revert pending
                
    def _run_step(self, step_num: int):
        """Run a specific step."""
        if not self.framework:
            return
        
        # Step 1 has a special dialog
        if step_num == 1:
            self._run_step_1()
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
            
        # Update statuses
        self._update_step_statuses()
    
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
            
            # Update status
            self._update_step_statuses()
            
            # Emit signal
            self.step_executed.emit(1, True)
        else:
            # Dialog was cancelled
            self.output_text.append("❌ Step 1 cancelled by user\n")
        
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
            
            # Update statuses
            self._update_step_statuses()
            
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
