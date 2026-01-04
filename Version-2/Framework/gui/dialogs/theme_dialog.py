"""Theme Selection Dialog

Allows users to choose between Light, Dark, and System Default themes.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QButtonGroup, QDialogButtonBox, QWidget, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from gui.theme_manager import ThemeManager, ThemeMode


class ThemeDialog(QDialog):
    """Dialog for selecting application theme."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Theme Selection")
        self.setMinimumWidth(450)

        # Get current theme
        self.theme_manager = ThemeManager.instance()
        self.selected_mode = self.theme_manager.current_mode

        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>Choose Theme</h2>")
        layout.addWidget(title)

        description = QLabel("Select your preferred visual theme for the application:")
        layout.addWidget(description)

        layout.addSpacing(10)

        # Radio buttons for theme selection
        self.button_group = QButtonGroup(self)

        # System Default option
        self.system_radio = QRadioButton("System Default")
        self.system_radio.setToolTip("Automatically match your operating system's theme")
        self.button_group.addButton(self.system_radio, 0)
        layout.addWidget(self.system_radio)

        system_desc = QLabel("  Automatically matches your operating system theme")
        system_desc.setStyleSheet("color: gray; font-size: 9pt; margin-left: 20px;")
        layout.addWidget(system_desc)

        layout.addSpacing(8)

        # Light Theme option
        self.light_radio = QRadioButton("Light Theme")
        self.light_radio.setToolTip("Use light colors with dark text")
        self.button_group.addButton(self.light_radio, 1)
        layout.addWidget(self.light_radio)

        light_desc = QLabel("  Light background with dark text")
        light_desc.setStyleSheet("color: gray; font-size: 9pt; margin-left: 20px;")
        layout.addWidget(light_desc)

        layout.addSpacing(8)

        # Dark Theme option
        self.dark_radio = QRadioButton("Dark Theme")
        self.dark_radio.setToolTip("Use dark colors with light text")
        self.button_group.addButton(self.dark_radio, 2)
        layout.addWidget(self.dark_radio)

        dark_desc = QLabel("  Dark background with light text")
        dark_desc.setStyleSheet("color: gray; font-size: 9pt; margin-left: 20px;")
        layout.addWidget(dark_desc)

        layout.addSpacing(15)

        # Preview section
        preview_label = QLabel("<b>Preview:</b>")
        layout.addWidget(preview_label)

        self.preview_widget = self._create_preview_widget()
        layout.addWidget(self.preview_widget)

        layout.addSpacing(15)

        # OK/Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set current theme selected
        if self.selected_mode == ThemeMode.SYSTEM:
            self.system_radio.setChecked(True)
        elif self.selected_mode == ThemeMode.LIGHT:
            self.light_radio.setChecked(True)
        else:
            self.dark_radio.setChecked(True)

        # Connect radio button signals
        self.system_radio.toggled.connect(self._on_theme_selected)
        self.light_radio.toggled.connect(self._on_theme_selected)
        self.dark_radio.toggled.connect(self._on_theme_selected)

        # Initial preview update
        self._update_preview()

    def _create_preview_widget(self) -> QWidget:
        """Create the theme preview widget.

        Returns:
            Widget showing sample theme colors
        """
        preview = QFrame()
        preview.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        preview.setMinimumHeight(120)

        layout = QVBoxLayout(preview)

        # Title
        self.preview_title = QLabel("Sample Text")
        self.preview_title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(self.preview_title)

        # Normal text
        self.preview_text = QLabel("This is how normal text will appear")
        layout.addWidget(self.preview_text)

        # Disabled text
        self.preview_disabled = QLabel("This is how disabled text will appear")
        layout.addWidget(self.preview_disabled)

        # Link text
        self.preview_link = QLabel('<a href="#">This is a link</a>')
        self.preview_link.setOpenExternalLinks(False)
        layout.addWidget(self.preview_link)

        # Status colors row
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status indicators:"))

        # Success indicator
        self.preview_success = QLabel(" Success ")
        self.preview_success.setFrameStyle(QFrame.Shape.Box)
        status_layout.addWidget(self.preview_success)

        # Warning indicator
        self.preview_warning = QLabel(" Warning ")
        self.preview_warning.setFrameStyle(QFrame.Shape.Box)
        status_layout.addWidget(self.preview_warning)

        # Active indicator
        self.preview_active = QLabel(" Active ")
        self.preview_active.setFrameStyle(QFrame.Shape.Box)
        status_layout.addWidget(self.preview_active)

        status_layout.addStretch()
        layout.addLayout(status_layout)

        layout.addStretch()

        return preview

    def _on_theme_selected(self):
        """Handle theme radio button selection."""
        if self.system_radio.isChecked():
            self.selected_mode = ThemeMode.SYSTEM
        elif self.light_radio.isChecked():
            self.selected_mode = ThemeMode.LIGHT
        else:
            self.selected_mode = ThemeMode.DARK

        self._update_preview()

    def _update_preview(self):
        """Update the preview widget to show selected theme colors."""
        # Get colors for the selected theme
        if self.selected_mode == ThemeMode.SYSTEM:
            # For system theme, detect what it would be
            resolved_mode = self.theme_manager._detect_system_theme()
            colors = self.theme_manager.get_colors(resolved_mode)
        else:
            colors = self.theme_manager.get_colors(self.selected_mode)

        # Apply colors to preview widget
        self.preview_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.window_bg};
                color: {colors.text};
            }}
        """)
        
        # Also apply menu stylesheets for consistency
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            menu_stylesheet = self.theme_manager.get_menu_stylesheet(
                ThemeMode.SYSTEM if self.selected_mode == ThemeMode.SYSTEM else self.selected_mode
            )
            app.setStyleSheet(menu_stylesheet)

        # Update text colors
        self.preview_title.setStyleSheet(f"""
            color: {colors.text};
            font-weight: bold;
            font-size: 11pt;
        """)

        self.preview_text.setStyleSheet(f"color: {colors.text};")

        self.preview_disabled.setStyleSheet(f"color: {colors.disabled_text};")

        self.preview_link.setStyleSheet(f"""
            color: {colors.link};
            text-decoration: underline;
        """)

        # Update status indicators
        self.preview_success.setStyleSheet(f"""
            background-color: {colors.success};
            color: #000000;
            padding: 2px 8px;
            border: 1px solid #333333;
        """)

        self.preview_warning.setStyleSheet(f"""
            background-color: {colors.warning};
            color: #000000;
            padding: 2px 8px;
            border: 1px solid #333333;
        """)

        self.preview_active.setStyleSheet(f"""
            background-color: {colors.active_bg};
            color: #000000;
            padding: 2px 8px;
            border: 1px solid #333333;
        """)

    def accept(self):
        """Save selected theme and close dialog."""
        # Save theme preference
        self.theme_manager.save_theme_preference(self.selected_mode)

        # Apply theme to application
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        self.theme_manager.apply_theme(app, self.selected_mode)

        super().accept()

    def get_selected_theme(self) -> ThemeMode:
        """Get the currently selected theme mode.

        Returns:
            Selected ThemeMode
        """
        return self.selected_mode
