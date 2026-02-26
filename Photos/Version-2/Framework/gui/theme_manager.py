"""Theme Manager for HSTL Photo Framework

Provides centralized theme management with Light, Dark, and System Default themes.
"""

from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    DRACULA = "dracula"
    SOLARIZED_LIGHT = "solarized_light"
    SOLARIZED_DARK = "solarized_dark"
    GITHUB = "github"


@dataclass
class ThemeColors:
    """Color definitions for a theme."""
    # Base colors
    window_bg: str
    base_bg: str
    alt_base_bg: str
    text: str
    button_bg: str
    button_text: str
    highlight: str
    highlighted_text: str
    link: str
    disabled_text: str

    # Semantic status colors
    success: str
    warning: str
    error: str
    info: str

    # Batch status background colors
    active_bg: str
    completed_bg: str
    archived_bg: str


class ThemeManager(QObject):
    """Singleton theme manager for the application.

    Manages theme selection, color palettes, and application-wide theme changes.
    """

    # Signal emitted when theme changes
    theme_changed = pyqtSignal(object)  # ThemeMode

    _instance = None

    def __init__(self):
        """Initialize theme manager (use instance() instead)."""
        if ThemeManager._instance is not None:
            raise RuntimeError("Use ThemeManager.instance() instead")
        super().__init__()
        self.current_mode = ThemeMode.SYSTEM
        self._current_resolved_mode = ThemeMode.LIGHT  # Actual light or dark mode

    @classmethod
    def instance(cls):
        """Get the singleton instance of ThemeManager."""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def apply_saved_theme(self, app: QApplication):
        """Load theme preference from settings and apply to application.

        Args:
            app: The QApplication instance to apply theme to
        """
        settings = QSettings("HSTL", "PhotoFramework")
        theme_pref = settings.value("theme", "system")

        # Validate theme preference
        try:
            mode = ThemeMode(theme_pref)
        except ValueError:
            # Invalid theme preference, default to system
            mode = ThemeMode.SYSTEM

        self.apply_theme(app, mode)

    def save_theme_preference(self, mode: ThemeMode):
        """Save theme preference to settings.

        Args:
            mode: The theme mode to save
        """
        settings = QSettings("HSTL", "PhotoFramework")
        settings.setValue("theme", mode.value)

    def apply_theme(self, app: QApplication, mode: ThemeMode):
        """Apply theme to the application.

        Args:
            app: The QApplication instance
            mode: The theme mode to apply
        """
        self.current_mode = mode

        # Resolve system theme to actual light or dark
        if mode == ThemeMode.SYSTEM:
            self._current_resolved_mode = self._detect_system_theme()
        else:
            self._current_resolved_mode = mode

        # Create and apply palette
        palette = self._create_palette(self._current_resolved_mode)
        app.setPalette(palette)

        # Apply menu stylesheet to fix dropdown menu readability
        menu_stylesheet = self.get_menu_stylesheet(self._current_resolved_mode)
        app.setStyleSheet(menu_stylesheet)

        # Emit signal for widgets with custom stylesheets
        self.theme_changed.emit(mode)

    def _detect_system_theme(self) -> ThemeMode:
        """Detect if system uses dark or light theme.

        Returns:
            ThemeMode.DARK if system theme is dark, ThemeMode.LIGHT otherwise
        """
        try:
            system_palette = QApplication.palette()
            bg_color = system_palette.color(QPalette.ColorRole.Window)

            # Calculate luminance (perceived brightness)
            # Using ITU-R BT.709 coefficients
            luminance = (0.299 * bg_color.red() +
                        0.587 * bg_color.green() +
                        0.114 * bg_color.blue())

            # If luminance < 128, it's a dark theme
            return ThemeMode.DARK if luminance < 128 else ThemeMode.LIGHT
        except Exception:
            # If detection fails, default to light theme
            return ThemeMode.LIGHT

    def _create_palette(self, mode: ThemeMode) -> QPalette:
        """Create a QPalette for the given theme mode.

        Args:
            mode: ThemeMode.LIGHT or ThemeMode.DARK (not SYSTEM)

        Returns:
            Configured QPalette for the theme
        """
        palette = QPalette()
        colors = self.get_colors(mode)

        # Set window and base colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors.window_bg))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.text))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors.base_bg))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.alt_base_bg))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors.text))

        # Set button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(colors.button_bg))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.button_text))

        # Set highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.highlight))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.highlighted_text))

        # Set link color
        palette.setColor(QPalette.ColorRole.Link, QColor(colors.link))

        # Set disabled text color
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                        QColor(colors.disabled_text))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                        QColor(colors.disabled_text))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                        QColor(colors.disabled_text))

        return palette

    def get_menu_stylesheet(self, mode: ThemeMode = None) -> str:
        """Get stylesheet for menu widgets to ensure proper readability.

        Args:
            mode: The theme mode (if None, uses current resolved mode)

        Returns:
            CSS stylesheet string for menu widgets
        """
        if mode is None:
            mode = self._current_resolved_mode
        
        colors = self.get_colors(mode)
        
        return f"""
        QMenu {{
            background-color: {colors.window_bg};
            color: {colors.text};
            border: 1px solid {colors.button_bg};
            padding: 2px;
        }}
        
        QMenu::item {{
            background-color: transparent;
            color: {colors.text};
            padding: 5px 20px;
            border: none;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.highlight};
            color: {colors.highlighted_text};
        }}
        
        QMenu::item:disabled {{
            color: {colors.disabled_text};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors.button_bg};
            margin: 5px 10px;
        }}
        
        QMenuBar {{
            background-color: {colors.window_bg};
            color: {colors.text};
            border: none;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            color: {colors.text};
            padding: 5px 10px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors.button_bg};
            color: {colors.text};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {colors.highlight};
            color: {colors.highlighted_text};
        }}
        """

    def get_colors(self, mode: ThemeMode = None) -> ThemeColors:
        """Get color definitions for a theme mode.

        Args:
            mode: The theme mode (if None, uses current resolved mode)

        Returns:
            ThemeColors dataclass with color definitions
        """
        if mode is None:
            mode = self._current_resolved_mode

        _dispatch = {
            ThemeMode.DARK:            self._get_dark_colors,
            ThemeMode.DRACULA:         self._get_dracula_colors,
            ThemeMode.SOLARIZED_LIGHT: self._get_solarized_light_colors,
            ThemeMode.SOLARIZED_DARK:  self._get_solarized_dark_colors,
            ThemeMode.GITHUB:          self._get_github_colors,
        }
        return _dispatch.get(mode, self._get_light_colors)()

    def get_current_colors(self) -> ThemeColors:
        """Get current theme's color definitions.

        Returns:
            ThemeColors for the currently active theme
        """
        return self.get_colors(self._current_resolved_mode)

    def _get_light_colors(self) -> ThemeColors:
        """Get color definitions for light theme.

        Returns:
            ThemeColors for light theme
        """
        return ThemeColors(
            # Base colors
            window_bg="#FFFFFF",
            base_bg="#FFFFFF",
            alt_base_bg="#F5F5F5",
            text="#000000",
            button_bg="#E0E0E0",
            button_text="#000000",
            highlight="#0078D7",
            highlighted_text="#FFFFFF",
            link="#0066CC",
            disabled_text="#888888",

            # Semantic colors
            success="#28A745",
            warning="#FFA500",
            error="#DC3545",
            info="#0066CC",

            # Batch status colors
            active_bg="#00FFFF",      # Aqua
            completed_bg="#ADD8E6",   # Light blue
            archived_bg="#D3D3D3"     # Light gray
        )

    def _get_dark_colors(self) -> ThemeColors:
        """Get color definitions for dark theme.

        Returns:
            ThemeColors for dark theme
        """
        return ThemeColors(
            # Base colors
            window_bg="#1E1E1E",
            base_bg="#2D2D2D",
            alt_base_bg="#252525",
            text="#FFFFFF",
            button_bg="#3C3C3C",
            button_text="#FFFFFF",
            highlight="#0078D7",
            highlighted_text="#FFFFFF",
            link="#4A9EFF",
            disabled_text="#6D6D6D",

            # Semantic colors
            success="#4CAF50",
            warning="#FFB74D",
            error="#EF5350",
            info="#4A9EFF",

            # Batch status colors
            active_bg="#00CED1",      # Darker cyan for dark background
            completed_bg="#4682B4",   # Steel blue
            archived_bg="#696969"     # Dim gray
        )

    def _get_dracula_colors(self) -> ThemeColors:
        """Get color definitions for Dracula theme."""
        return ThemeColors(
            window_bg="#282A36",
            base_bg="#1E1F29",
            alt_base_bg="#44475A",
            text="#F8F8F2",
            button_bg="#44475A",
            button_text="#F8F8F2",
            highlight="#BD93F9",
            highlighted_text="#282A36",
            link="#8BE9FD",
            disabled_text="#6272A4",
            success="#50FA7B",
            warning="#FFB86C",
            error="#FF5555",
            info="#8BE9FD",
            active_bg="#006272",
            completed_bg="#1E6B2E",
            archived_bg="#44475A",
        )

    def _get_solarized_light_colors(self) -> ThemeColors:
        """Get color definitions for Solarized Light theme."""
        return ThemeColors(
            window_bg="#FDF6E3",
            base_bg="#EEE8D5",
            alt_base_bg="#FDF6E3",
            text="#657B83",
            button_bg="#EEE8D5",
            button_text="#586E75",
            highlight="#268BD2",
            highlighted_text="#FDF6E3",
            link="#268BD2",
            disabled_text="#93A1A1",
            success="#859900",
            warning="#B58900",
            error="#DC322F",
            info="#268BD2",
            active_bg="#C9DFF5",
            completed_bg="#D5E8C8",
            archived_bg="#E8DFCC",
        )

    def _get_solarized_dark_colors(self) -> ThemeColors:
        """Get color definitions for Solarized Dark theme."""
        return ThemeColors(
            window_bg="#002B36",
            base_bg="#073642",
            alt_base_bg="#002B36",
            text="#839496",
            button_bg="#073642",
            button_text="#93A1A1",
            highlight="#268BD2",
            highlighted_text="#002B36",
            link="#268BD2",
            disabled_text="#586E75",
            success="#859900",
            warning="#B58900",
            error="#DC322F",
            info="#268BD2",
            active_bg="#1B5C6B",
            completed_bg="#2F6B2F",
            archived_bg="#3D4E53",
        )

    def _get_github_colors(self) -> ThemeColors:
        """Get color definitions for GitHub theme."""
        return ThemeColors(
            window_bg="#FFFFFF",
            base_bg="#F6F8FA",
            alt_base_bg="#FFFFFF",
            text="#24292F",
            button_bg="#F6F8FA",
            button_text="#24292F",
            highlight="#0969DA",
            highlighted_text="#FFFFFF",
            link="#0969DA",
            disabled_text="#8C959F",
            success="#1A7F37",
            warning="#9A6700",
            error="#CF222E",
            info="#0550AE",
            active_bg="#DDF4FF",
            completed_bg="#DAFBE1",
            archived_bg="#EAEEF2",
        )
