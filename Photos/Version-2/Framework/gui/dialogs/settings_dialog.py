"""Settings Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QGroupBox, QPushButton
)


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)

        self._init_ui()

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

        layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

    def _open_theme_dialog(self):
        """Open theme selection dialog."""
        from gui.dialogs.theme_dialog import ThemeDialog
        dialog = ThemeDialog(self)
        dialog.exec()
