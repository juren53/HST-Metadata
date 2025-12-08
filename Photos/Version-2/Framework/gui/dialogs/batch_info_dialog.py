"""Batch Info Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QDialogButtonBox
)


class BatchInfoDialog(QDialog):
    """Dialog showing detailed batch information."""
    
    def __init__(self, batch_id, registry, parent=None):
        super().__init__(parent)
        
        self.batch_id = batch_id
        self.registry = registry
        
        self.setWindowTitle("Batch Information")
        self.setMinimumSize(600, 400)
        
        self._init_ui()
        self._load_info()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
    def _load_info(self):
        """Load and display batch information."""
        summary = self.registry.get_batch_summary(self.batch_id)
        
        if not summary:
            self.info_text.setText("Batch not found")
            return
            
        info = []
        info.append(f"<h2>{summary['name']}</h2>")
        info.append(f"<b>Batch ID:</b> {self.batch_id}<br>")
        info.append(f"<b>Status:</b> {summary.get('status', 'unknown')}<br>")
        info.append(f"<b>Created:</b> {summary.get('created', 'unknown')}<br>")
        info.append(f"<b>Last Accessed:</b> {summary.get('last_accessed', 'unknown')}<br>")
        info.append(f"<b>Data Directory:</b> {summary['data_directory']}<br>")
        info.append(f"<b>Config File:</b> {summary['config_path']}<br>")
        
        info.append("<br><b>Progress:</b><br>")
        completed = summary.get('completed_steps', 0)
        total = summary.get('total_steps', 8)
        percentage = summary.get('completion_percentage', 0)
        info.append(f"{completed}/{total} steps ({percentage:.0f}%)<br>")
        
        info.append("<br><b>Step Status:</b><br>")
        
        step_names = {
            'step1': "Google Worksheet Preparation",
            'step2': "CSV Conversion",
            'step3': "Unicode Filtering",
            'step4': "TIFF Bit Depth Conversion",
            'step5': "Metadata Embedding",
            'step6': "JPEG Conversion",
            'step7': "JPEG Resizing",
            'step8': "Watermark Addition"
        }
        
        if 'steps_completed' in summary:
            for step_key in sorted(summary['steps_completed'].keys()):
                step_num = step_key.replace('step', '')
                completed = summary['steps_completed'][step_key]
                status = "✅" if completed else "⭕"
                step_name = step_names.get(step_key, step_key)
                info.append(f"{status} Step {step_num}: {step_name}<br>")
        
        self.info_text.setHtml("".join(info))
