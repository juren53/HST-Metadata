"""
GUI tests for Theme and Zoom managers.

Tests theme switching and zoom functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

# Skip all tests if PyQt6 is not available
pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

from gui.theme_manager import ThemeManager, ThemeMode, ThemeColors
from gui.zoom_manager import ZoomManager


# Reset singleton instances between tests
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test."""
    ThemeManager._instance = None
    ZoomManager._instance = None
    yield
    ThemeManager._instance = None
    ZoomManager._instance = None


class TestThemeMode:
    """Tests for ThemeMode enum."""

    @pytest.mark.gui
    def test_theme_mode_values(self):
        """ThemeMode has expected values."""
        assert ThemeMode.LIGHT.value == "light"
        assert ThemeMode.DARK.value == "dark"
        assert ThemeMode.SYSTEM.value == "system"

    @pytest.mark.gui
    def test_theme_mode_from_string(self):
        """Can create ThemeMode from string."""
        assert ThemeMode("light") == ThemeMode.LIGHT
        assert ThemeMode("dark") == ThemeMode.DARK
        assert ThemeMode("system") == ThemeMode.SYSTEM


class TestThemeColors:
    """Tests for ThemeColors dataclass."""

    @pytest.mark.gui
    def test_theme_colors_light(self):
        """Light theme colors are correct."""
        tm = ThemeManager.instance()
        colors = tm._get_light_colors()

        assert colors.window_bg == "#FFFFFF"
        assert colors.text == "#000000"
        assert isinstance(colors.success, str)
        assert isinstance(colors.error, str)

    @pytest.mark.gui
    def test_theme_colors_dark(self):
        """Dark theme colors are correct."""
        tm = ThemeManager.instance()
        colors = tm._get_dark_colors()

        assert colors.window_bg == "#1E1E1E"
        assert colors.text == "#FFFFFF"
        assert isinstance(colors.success, str)
        assert isinstance(colors.error, str)

    @pytest.mark.gui
    def test_theme_colors_have_all_fields(self):
        """ThemeColors has all required fields."""
        tm = ThemeManager.instance()
        colors = tm.get_colors(ThemeMode.LIGHT)

        # Base colors
        assert hasattr(colors, 'window_bg')
        assert hasattr(colors, 'text')
        assert hasattr(colors, 'button_bg')
        assert hasattr(colors, 'highlight')

        # Semantic colors
        assert hasattr(colors, 'success')
        assert hasattr(colors, 'warning')
        assert hasattr(colors, 'error')
        assert hasattr(colors, 'info')

        # Batch status colors
        assert hasattr(colors, 'active_bg')
        assert hasattr(colors, 'completed_bg')
        assert hasattr(colors, 'archived_bg')


class TestThemeManager:
    """Tests for ThemeManager class."""

    @pytest.mark.gui
    def test_theme_manager_singleton(self):
        """ThemeManager is singleton."""
        tm1 = ThemeManager.instance()
        tm2 = ThemeManager.instance()
        assert tm1 is tm2

    @pytest.mark.gui
    def test_theme_manager_direct_init_raises(self):
        """Direct instantiation raises error after singleton created."""
        ThemeManager.instance()
        with pytest.raises(RuntimeError):
            ThemeManager()

    @pytest.mark.gui
    def test_theme_manager_get_colors(self):
        """get_colors returns ThemeColors."""
        tm = ThemeManager.instance()
        colors = tm.get_colors(ThemeMode.LIGHT)
        assert isinstance(colors, ThemeColors)

    @pytest.mark.gui
    def test_theme_manager_get_menu_stylesheet(self):
        """get_menu_stylesheet returns CSS string."""
        tm = ThemeManager.instance()
        stylesheet = tm.get_menu_stylesheet(ThemeMode.LIGHT)

        assert isinstance(stylesheet, str)
        assert "QMenu" in stylesheet
        assert "QMenuBar" in stylesheet


class TestThemeManagerWithApp:
    """Tests that require QApplication."""

    @pytest.mark.gui
    def test_apply_theme_light(self, qtbot):
        """Apply light theme changes palette."""
        app = QApplication.instance()
        tm = ThemeManager.instance()

        tm.apply_theme(app, ThemeMode.LIGHT)

        assert tm.current_mode == ThemeMode.LIGHT
        palette = app.palette()
        # Light theme should have light window color
        window_color = palette.color(QPalette.ColorRole.Window)
        assert window_color.lightness() > 200

    @pytest.mark.gui
    def test_apply_theme_dark(self, qtbot):
        """Apply dark theme changes palette."""
        app = QApplication.instance()
        tm = ThemeManager.instance()

        tm.apply_theme(app, ThemeMode.DARK)

        assert tm.current_mode == ThemeMode.DARK
        palette = app.palette()
        # Dark theme should have dark window color
        window_color = palette.color(QPalette.ColorRole.Window)
        assert window_color.lightness() < 100

    @pytest.mark.gui
    def test_theme_changed_signal(self, qtbot):
        """theme_changed signal emitted on theme change."""
        app = QApplication.instance()
        tm = ThemeManager.instance()

        with qtbot.waitSignal(tm.theme_changed, timeout=1000):
            tm.apply_theme(app, ThemeMode.DARK)


class TestZoomManager:
    """Tests for ZoomManager class."""

    @pytest.mark.gui
    def test_zoom_manager_singleton(self):
        """ZoomManager is singleton."""
        zm1 = ZoomManager.instance()
        zm2 = ZoomManager.instance()
        assert zm1 is zm2

    @pytest.mark.gui
    def test_zoom_manager_direct_init_raises(self):
        """Direct instantiation raises error after singleton created."""
        ZoomManager.instance()
        with pytest.raises(RuntimeError):
            ZoomManager()

    @pytest.mark.gui
    def test_zoom_levels_defined(self):
        """Zoom levels are properly defined."""
        zm = ZoomManager.instance()

        assert zm.MIN_ZOOM == 0.75
        assert zm.MAX_ZOOM == 2.0
        assert zm.DEFAULT_ZOOM == 1.0
        assert len(zm.ZOOM_LEVELS) > 0

    @pytest.mark.gui
    def test_get_zoom_percentage(self):
        """get_zoom_percentage returns correct value."""
        zm = ZoomManager.instance()
        zm._current_zoom = 1.5

        assert zm.get_zoom_percentage() == 150

    @pytest.mark.gui
    def test_get_current_zoom(self):
        """get_current_zoom returns current factor."""
        zm = ZoomManager.instance()
        zm._current_zoom = 1.3

        assert zm.get_current_zoom() == 1.3


class TestZoomManagerWithApp:
    """Tests that require QApplication."""

    @pytest.mark.gui
    def test_set_zoom_level(self, qtbot):
        """set_zoom_level changes zoom."""
        app = QApplication.instance()
        zm = ZoomManager.instance()
        zm.initialize_base_font(app)

        zm.set_zoom_level(app, 1.5)

        assert zm.get_current_zoom() == 1.5

    @pytest.mark.gui
    def test_set_zoom_level_clamps(self, qtbot):
        """Zoom level is clamped to valid range."""
        app = QApplication.instance()
        zm = ZoomManager.instance()
        zm.initialize_base_font(app)

        # Try to set beyond max
        zm.set_zoom_level(app, 5.0)
        assert zm.get_current_zoom() == zm.MAX_ZOOM

        # Try to set below min
        zm.set_zoom_level(app, 0.1)
        assert zm.get_current_zoom() == zm.MIN_ZOOM

    @pytest.mark.gui
    def test_zoom_in(self, qtbot):
        """zoom_in increases zoom level."""
        app = QApplication.instance()
        zm = ZoomManager.instance()
        zm.initialize_base_font(app)
        zm._current_zoom = 1.0

        zm.zoom_in(app)

        assert zm.get_current_zoom() > 1.0

    @pytest.mark.gui
    def test_zoom_out(self, qtbot):
        """zoom_out decreases zoom level."""
        app = QApplication.instance()
        zm = ZoomManager.instance()
        zm.initialize_base_font(app)
        zm._current_zoom = 1.5

        zm.zoom_out(app)

        assert zm.get_current_zoom() < 1.5

    @pytest.mark.gui
    def test_reset_zoom(self, qtbot):
        """reset_zoom returns to 100%."""
        app = QApplication.instance()
        zm = ZoomManager.instance()
        zm.initialize_base_font(app)
        zm._current_zoom = 1.5

        zm.reset_zoom(app)

        assert zm.get_current_zoom() == 1.0

    @pytest.mark.gui
    def test_zoom_changed_signal(self, qtbot):
        """zoom_changed signal emitted on zoom change."""
        app = QApplication.instance()
        zm = ZoomManager.instance()
        zm.initialize_base_font(app)

        with qtbot.waitSignal(zm.zoom_changed, timeout=1000):
            zm.set_zoom_level(app, 1.5)
