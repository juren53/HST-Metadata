"""Zoom Manager for HSTL Photo Framework

Provides centralized zoom/font scaling management.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont


class ZoomManager(QObject):
    """Singleton zoom manager for application font scaling.

    Manages zoom level and applies font scaling globally.
    Follows the same pattern as ThemeManager.
    """

    # Signal emitted when zoom changes
    zoom_changed = pyqtSignal(float)  # Emits zoom factor (e.g., 1.0, 1.5)

    # Zoom levels from 75% to 200%
    ZOOM_LEVELS = [0.75, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
    DEFAULT_ZOOM = 1.0
    MIN_ZOOM = 0.75
    MAX_ZOOM = 2.0

    _instance = None

    def __init__(self):
        """Initialize zoom manager (use instance() instead)."""
        if ZoomManager._instance is not None:
            raise RuntimeError("Use ZoomManager.instance() instead")
        super().__init__()

        self._current_zoom = self.DEFAULT_ZOOM
        self._base_font_size = None  # Store base font size

    @classmethod
    def instance(cls):
        """Get the singleton instance of ZoomManager."""
        if cls._instance is None:
            cls._instance = ZoomManager()
        return cls._instance

    def initialize_base_font(self, app: QApplication):
        """Capture the base font size from the application.

        Call this once during app startup before applying any zoom.

        Args:
            app: The QApplication instance
        """
        if self._base_font_size is None:
            base_font = app.font()
            self._base_font_size = base_font.pointSize()

    def apply_saved_zoom(self, app: QApplication):
        """Load zoom preference from settings and apply to application.

        Args:
            app: The QApplication instance to apply zoom to
        """
        settings = QSettings("HSTL", "PhotoFramework")
        zoom_level = settings.value("ui/zoom_level", self.DEFAULT_ZOOM, type=float)

        # Validate and clamp zoom level
        zoom_level = max(self.MIN_ZOOM, min(self.MAX_ZOOM, zoom_level))

        self.set_zoom_level(app, zoom_level)

    def save_zoom_preference(self):
        """Save current zoom preference to settings."""
        settings = QSettings("HSTL", "PhotoFramework")
        settings.setValue("ui/zoom_level", self._current_zoom)

    def set_zoom_level(self, app: QApplication, factor: float):
        """Set absolute zoom level.

        Args:
            app: The QApplication instance
            factor: Zoom factor (0.75 to 2.0)
        """
        # Clamp to valid range
        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))

        if factor == self._current_zoom:
            return  # No change

        self._current_zoom = factor
        self._apply_font_scaling(app)
        self.zoom_changed.emit(factor)

    def zoom_in(self, app: QApplication):
        """Increase zoom to next level.

        Args:
            app: The QApplication instance
        """
        # Find next higher zoom level
        current_index = self._get_nearest_zoom_index()
        if current_index < len(self.ZOOM_LEVELS) - 1:
            next_zoom = self.ZOOM_LEVELS[current_index + 1]
            self.set_zoom_level(app, next_zoom)

    def zoom_out(self, app: QApplication):
        """Decrease zoom to previous level.

        Args:
            app: The QApplication instance
        """
        # Find next lower zoom level
        current_index = self._get_nearest_zoom_index()
        if current_index > 0:
            prev_zoom = self.ZOOM_LEVELS[current_index - 1]
            self.set_zoom_level(app, prev_zoom)

    def reset_zoom(self, app: QApplication):
        """Reset zoom to 100% (1.0).

        Args:
            app: The QApplication instance
        """
        self.set_zoom_level(app, self.DEFAULT_ZOOM)

    def get_zoom_percentage(self) -> int:
        """Get current zoom as percentage (75, 100, 150, etc.).

        Returns:
            Zoom percentage as integer
        """
        return int(self._current_zoom * 100)

    def get_current_zoom(self) -> float:
        """Get current zoom factor.

        Returns:
            Current zoom factor (0.75 to 2.0)
        """
        return self._current_zoom

    def _get_nearest_zoom_index(self) -> int:
        """Find index of nearest zoom level to current zoom.

        Returns:
            Index in ZOOM_LEVELS list
        """
        # Find closest zoom level
        min_diff = float('inf')
        nearest_index = 0

        for i, level in enumerate(self.ZOOM_LEVELS):
            diff = abs(level - self._current_zoom)
            if diff < min_diff:
                min_diff = diff
                nearest_index = i

        return nearest_index

    def _apply_font_scaling(self, app: QApplication):
        """Apply font scaling to the application.

        Args:
            app: The QApplication instance
        """
        if self._base_font_size is None:
            # Capture base font size on first call
            self._base_font_size = app.font().pointSize()

        # Calculate new font size
        new_size = int(self._base_font_size * self._current_zoom)

        # Clamp to reasonable limits (8pt to 24pt)
        # 8pt minimum: Below this, text becomes unreadable
        # 24pt maximum: Above this, UI becomes unwieldy
        new_size = max(8, min(24, new_size))

        # Create a new font with the scaled size
        font = QFont()
        font.setPointSize(new_size)
        app.setFont(font)

        # Force all widgets to update by processing font change events
        # This ensures existing widgets pick up the new font
        for widget in app.allWidgets():
            widget.setFont(font)
