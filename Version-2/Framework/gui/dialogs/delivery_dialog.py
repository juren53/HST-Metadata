"""
Delivery Dialog - Final Product Delivery

Creates the final delivery package after all 8 workflow steps are complete.
Copies final TIFFs and JPEGs to delivery/, moves intermediate files to trash/.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar,
    QGroupBox, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager
from core.delivery_service import DeliveryService


class DeliveryThread(QThread):
    """Worker thread for delivery package creation."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, service: DeliveryService):
        super().__init__()
        self.service = service

    def run(self):
        success, message = self.service.create_package(
            progress_callback=self.progress.emit
        )
        self.finished.emit(success, message)


class DeliveryDialog(QDialog):
    """Dialog for Final Product Delivery."""

    def __init__(self, batch_info: dict, parent=None):
        super().__init__(parent)

        self.batch_info = batch_info
        self.batch_id = batch_info.get("id", "")
        data_directory = batch_info.get("data_directory", "")
        self.data_dir = Path(data_directory) if data_directory else None
        self.log_manager = get_log_manager()
        self.delivery_thread = None

        self.service = DeliveryService(self.data_dir, self.log_manager) if self.data_dir else None

        self.setWindowTitle("Final Product Delivery")
        self.setMinimumWidth(680)
        self.setMinimumHeight(520)
        self.resize(780, 580)

        self.log_manager.debug("Opened Delivery dialog", batch_id=self.batch_id)
        self._init_ui()
        self._analyze()

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Title
        title = QLabel("<h2>Final Product Delivery</h2>")
        layout.addWidget(title)

        desc = QLabel(
            "<p>Creates the delivery package from completed workflow output. "
            "Final TIFFs and JPEGs are copied to <b>delivery/</b>. "
            "Intermediate JPEGs are moved to <b>trash/</b> for optional cleanup.</p>"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(8)

        # Batch info
        batch_name = self.batch_info.get("name", "Unknown")
        batch_label = QLabel(f"<b>Batch:</b> {batch_name}")
        layout.addWidget(batch_label)

        layout.addSpacing(8)

        # File counts summary
        self.summary_group = QGroupBox("Delivery Summary")
        summary_layout = QVBoxLayout(self.summary_group)

        self.tiff_count_label = QLabel("TIFFs to deliver: —")
        self.jpeg_count_label = QLabel("JPEGs to deliver: —")
        self.trash_jpeg_label = QLabel("Converted JPEGs to trash: —")
        self.trash_resized_label = QLabel("Resized JPEGs to trash: —")

        summary_layout.addWidget(self.tiff_count_label)
        summary_layout.addWidget(self.jpeg_count_label)
        summary_layout.addWidget(self.trash_jpeg_label)
        summary_layout.addWidget(self.trash_resized_label)

        layout.addWidget(self.summary_group)

        layout.addSpacing(8)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)

        # Status / log output
        status_label = QLabel("<b>Status &amp; Output:</b>")
        layout.addWidget(status_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(180)
        layout.addWidget(self.output_text)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Buttons — outside scroll area, always visible
        button_layout = QHBoxLayout()

        self.deliver_btn = QPushButton("Create Delivery Package")
        self.deliver_btn.setDefault(True)
        self.deliver_btn.setEnabled(False)
        self.deliver_btn.clicked.connect(self._on_deliver_clicked)
        button_layout.addWidget(self.deliver_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    # -------------------------------------------------------------------------
    # Pre-flight analysis
    # -------------------------------------------------------------------------

    def _analyze(self):
        """Validate preconditions and populate the summary."""
        if not self.service:
            self._log("❌ No data directory configured for this batch.")
            return

        valid, reason = self.service.validate()
        if not valid:
            self._log(f"❌ Cannot create delivery package:\n{reason}")
            return

        counts = self.service.get_file_counts()
        self.tiff_count_label.setText(f"TIFFs to deliver: {counts['tiff_delivery']}")
        self.jpeg_count_label.setText(f"JPEGs to deliver: {counts['jpeg_delivery']}")
        self.trash_jpeg_label.setText(f"Converted JPEGs to trash: {counts['jpeg_to_trash']}")
        self.trash_resized_label.setText(f"Resized JPEGs to trash: {counts['jpeg_resized_to_trash']}")

        if self.service.delivery_exists():
            self._log(
                "⚠️  A delivery package already exists for this batch.\n"
                "Click 'Create Delivery Package' to overwrite it."
            )
            self.deliver_btn.setText("Overwrite Delivery Package...")
        else:
            self._log("✓ All 8 steps complete. Ready to create delivery package.")

        self.deliver_btn.setEnabled(True)

    # -------------------------------------------------------------------------
    # Deliver button handler
    # -------------------------------------------------------------------------

    def _on_deliver_clicked(self):
        if self.service.delivery_exists():
            reply = QMessageBox.question(
                self,
                "Delivery Package Exists",
                "A delivery package already exists for this batch.\n\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            # Remove existing delivery before re-running
            import shutil
            shutil.rmtree(self.service.delivery_dir)

        self._start_delivery()

    def _start_delivery(self):
        self.deliver_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.output_text.clear()

        self.delivery_thread = DeliveryThread(self.service)
        self.delivery_thread.progress.connect(self._log)
        self.delivery_thread.finished.connect(self._on_delivery_finished)
        self.delivery_thread.start()

    def _on_delivery_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)

        if success:
            self.log_manager.success(
                f"Delivery package created for batch: {self.batch_info.get('name', '')}",
                batch_id=self.batch_id,
            )
            # Update button state — package now exists
            self.deliver_btn.setText("Overwrite Delivery Package...")
            self.deliver_btn.setEnabled(True)
        else:
            self.deliver_btn.setEnabled(True)
            QMessageBox.critical(self, "Delivery Failed", message)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _log(self, message: str):
        self.output_text.append(message)
