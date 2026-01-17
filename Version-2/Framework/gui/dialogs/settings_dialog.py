"""Settings Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox,
    QGroupBox, QPushButton, QComboBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import QSettings

from utils.log_manager import LogManager


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumSize(450, 400)

        self.settings = QSettings("HSTL", "PhotoFramework")
        self.log_manager = LogManager.instance()

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)

        label = QLabel("<h2>Application Settings</h2>")
        layout.addWidget(label)

        # Theme Settings Group
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout(theme_group)

        theme_desc = QLabel("Customize the application's visual theme:")
        theme_layout.addWidget(theme_desc)

        theme_btn = QPushButton("Change Theme...")
        theme_btn.clicked.connect(self._open_theme_dialog)
        theme_layout.addWidget(theme_btn)

        layout.addWidget(theme_group)

        # Logging Settings Group
        logging_group = QGroupBox("Logging")
        logging_layout = QVBoxLayout(logging_group)

        # Enable logging checkbox
        self.logging_enabled_check = QCheckBox("Enable logging")
        self.logging_enabled_check.setToolTip(
            "Master switch for logging.\n"
            "When disabled, no log messages are recorded or displayed."
        )
        self.logging_enabled_check.stateChanged.connect(self._on_logging_enabled_changed)
        logging_layout.addWidget(self.logging_enabled_check)

        # Verbosity level
        verbosity_layout = QHBoxLayout()
        verbosity_layout.addWidget(QLabel("Verbosity Level:"))

        self.verbosity_combo = QComboBox()
        self.verbosity_combo.addItem("Minimal (Errors and warnings only)", "minimal")
        self.verbosity_combo.addItem("Normal (Key actions)", "normal")
        self.verbosity_combo.addItem("Detailed (All operations)", "detailed")
        self.verbosity_combo.setToolTip(
            "Controls how much detail is shown in the log viewer.\n"
            "Minimal: Only errors and warnings\n"
            "Normal: Key actions and status messages\n"
            "Detailed: All operations including debug info"
        )
        verbosity_layout.addWidget(self.verbosity_combo, 1)
        logging_layout.addLayout(verbosity_layout)

        # Per-batch logging
        self.per_batch_check = QCheckBox("Enable per-batch log files")
        self.per_batch_check.setToolTip(
            "When enabled, each batch gets its own log file in its data directory.\n"
            "Useful for troubleshooting specific batch issues."
        )
        logging_layout.addWidget(self.per_batch_check)

        # Console capture
        self.console_capture_check = QCheckBox("Capture console output")
        self.console_capture_check.setToolTip(
            "When enabled, all print() statements and console output\n"
            "are captured and routed to the logging system.\n"
            "Useful for capturing output from external tools."
        )
        logging_layout.addWidget(self.console_capture_check)

        # Log buffer size
        buffer_layout = QHBoxLayout()
        buffer_layout.addWidget(QLabel("GUI Log Buffer:"))

        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(100, 10000)
        self.buffer_spin.setSingleStep(100)
        self.buffer_spin.setSuffix(" lines")
        self.buffer_spin.setToolTip(
            "Maximum number of log entries to keep in the log viewer.\n"
            "Higher values use more memory but preserve more history."
        )
        buffer_layout.addWidget(self.buffer_spin)
        buffer_layout.addStretch()
        logging_layout.addLayout(buffer_layout)

        layout.addWidget(logging_group)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_settings(self):
        """Load current settings values."""
        # Logging enabled
        logging_enabled = self.settings.value("logging/enabled", True, type=bool)
        self.logging_enabled_check.setChecked(logging_enabled)
        self._on_logging_enabled_changed(None)  # Update control states

        # Verbosity
        verbosity = self.settings.value("logging/verbosity", "normal")
        index = self.verbosity_combo.findData(verbosity)
        if index >= 0:
            self.verbosity_combo.setCurrentIndex(index)

        # Per-batch logging
        per_batch = self.settings.value("logging/per_batch", True, type=bool)
        self.per_batch_check.setChecked(per_batch)

        # Console capture
        console_capture = self.settings.value("logging/console_capture", False, type=bool)
        self.console_capture_check.setChecked(console_capture)

        # Buffer size
        buffer_size = self.settings.value("logging/buffer_size", 1000, type=int)
        self.buffer_spin.setValue(buffer_size)

    def _save_and_accept(self):
        """Save settings and close dialog."""
        # Get values
        logging_enabled = self.logging_enabled_check.isChecked()
        verbosity = self.verbosity_combo.currentData()
        per_batch = self.per_batch_check.isChecked()
        console_capture = self.console_capture_check.isChecked()
        buffer_size = self.buffer_spin.value()

        # Save to QSettings
        self.settings.setValue("logging/enabled", logging_enabled)
        self.settings.setValue("logging/verbosity", verbosity)
        self.settings.setValue("logging/per_batch", per_batch)
        self.settings.setValue("logging/console_capture", console_capture)
        self.settings.setValue("logging/buffer_size", buffer_size)

        # Apply to LogManager
        self.log_manager.set_enabled(logging_enabled)
        self.log_manager.set_verbosity(verbosity)
        self.log_manager.set_per_batch_logging(per_batch)

        # Apply console capture
        if console_capture:
            self.log_manager.enable_console_capture()
        else:
            self.log_manager.disable_console_capture()

        self.accept()

    def _open_theme_dialog(self):
        """Open theme selection dialog."""
        from gui.dialogs.theme_dialog import ThemeDialog
        dialog = ThemeDialog(self)
        dialog.exec()

    def _on_logging_enabled_changed(self, state):
        """Enable/disable logging controls based on master switch."""
        enabled = self.logging_enabled_check.isChecked()
        self.verbosity_combo.setEnabled(enabled)
        self.per_batch_check.setEnabled(enabled)
        self.console_capture_check.setEnabled(enabled)
        self.buffer_spin.setEnabled(enabled)
