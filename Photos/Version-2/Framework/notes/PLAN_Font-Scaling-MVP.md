# Font Scaling Implementation Plan (MVP)

**Created**: 2026-01-03
**Approach**: Minimum Viable Product - Font Scaling Only
**Status**: Planning

---

## Overview

Implement zoom functionality using **font scaling only** as a simple, maintainable MVP. This approach avoids complex widget-specific dimension scaling and leverages Qt's automatic layout system to handle size adjustments.

### Why Font Scaling Only?

1. **Simplicity**: Single scaling mechanism vs. multiple per-widget implementations
2. **Qt Layouts**: Layouts automatically adjust to font changes
3. **Maintainability**: No custom code per widget
4. **Testing**: Easy to verify - just check font sizes
5. **MVP Philosophy**: Test if this satisfies user needs before adding complexity

---

## Requirements (Same as Full Plan)

✅ **Zoom Range**: 75% to 200% maximum
✅ **Persistence**: Remember last used zoom level across app restarts
✅ **Global Zoom**: Same zoom level applied to all windows/tabs
✅ **UI Feedback**: Status bar indicator for current zoom level
✅ **Controls**: Both Ctrl+mouse-wheel and Ctrl+plus/minus enabled

---

## Architecture

### Component 1: ZoomManager Singleton

**File**: `gui/zoom_manager.py`

Follows existing `ThemeManager` pattern for consistency.

**Responsibilities**:
- Manage zoom level state (0.75 to 2.0)
- Apply font scaling to QApplication
- Emit signals when zoom changes
- Persist zoom level via QSettings
- Provide zoom increment/decrement methods

**Key Design**:
```python
class ZoomManager(QObject):
    """Singleton zoom manager for font scaling."""

    # Signal emitted when zoom changes
    zoom_changed = pyqtSignal(float)  # zoom factor (e.g., 1.0, 1.5)

    # Zoom configuration
    ZOOM_LEVELS = [0.75, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
    DEFAULT_ZOOM = 1.0
    MIN_ZOOM = 0.75
    MAX_ZOOM = 2.0

    _instance = None

    @classmethod
    def instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ZoomManager()
        return cls._instance
```

### Component 2: MainWindow Integration

**File**: `gui/main_window.py`

**Additions**:
1. View menu with zoom actions
2. Keyboard shortcuts (Ctrl+Plus, Ctrl+Minus, Ctrl+0)
3. Mouse wheel event handler (Ctrl+Wheel)
4. Status bar zoom indicator
5. Load/save zoom settings

---

## Detailed Implementation

### Step 1: Create ZoomManager Class

**File**: `gui/zoom_manager.py`

```python
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

        # Apply to application
        font = app.font()
        font.setPointSize(new_size)
        app.setFont(font)
```

**Key Features**:
- Singleton pattern matching ThemeManager
- Discrete zoom levels for predictable behavior
- Settings persistence via QSettings
- Base font size capture for accurate scaling
- Signal emission for UI updates
- Robust validation and clamping

---

### Step 2: Integrate into MainWindow

**File**: `gui/main_window.py`

#### 2a. Import and Initialize

```python
# Add to imports
from gui.zoom_manager import ZoomManager

# In __init__ method, after existing initialization:
def __init__(self):
    super().__init__()

    self.framework = HSLTFramework()
    self.registry = BatchRegistry()
    self.current_batch_id = None
    self.settings = QSettings("HSTL", "PhotoFramework")

    # NEW: Initialize zoom manager
    self.zoom_manager = ZoomManager.instance()
    self.zoom_manager.zoom_changed.connect(self._on_zoom_changed)

    self._init_ui()
    self._create_menu_bar()
    self._create_status_bar()
    self._load_window_state()
    self._refresh_batch_list()
```

#### 2b. Add View Menu to Menu Bar

```python
# In _create_menu_bar method, add after Edit menu:
def _create_menu_bar(self):
    menubar = self.menuBar()

    # ... existing File menu code ...
    # ... existing Edit menu code ...

    # View menu - NEW
    view_menu = menubar.addMenu("&View")

    # Zoom In action
    zoom_in_action = QAction("Zoom &In", self)
    zoom_in_action.setShortcut("Ctrl++")
    zoom_in_action.setStatusTip("Increase zoom level")
    zoom_in_action.triggered.connect(self._zoom_in)
    view_menu.addAction(zoom_in_action)

    # Zoom In alternate shortcut (Ctrl+=)
    zoom_in_alt_action = QAction(self)
    zoom_in_alt_action.setShortcut("Ctrl+=")
    zoom_in_alt_action.triggered.connect(self._zoom_in)
    self.addAction(zoom_in_alt_action)  # Add to window, not menu

    # Zoom Out action
    zoom_out_action = QAction("Zoom &Out", self)
    zoom_out_action.setShortcut("Ctrl+-")
    zoom_out_action.setStatusTip("Decrease zoom level")
    zoom_out_action.triggered.connect(self._zoom_out)
    view_menu.addAction(zoom_out_action)

    # Reset Zoom action
    view_menu.addSeparator()
    zoom_reset_action = QAction("&Reset Zoom", self)
    zoom_reset_action.setShortcut("Ctrl+0")
    zoom_reset_action.setStatusTip("Reset zoom to 100%")
    zoom_reset_action.triggered.connect(self._reset_zoom)
    view_menu.addAction(zoom_reset_action)
```

#### 2c. Add Zoom Action Methods

```python
# Add these methods to MainWindow class:

def _zoom_in(self):
    """Handle zoom in action."""
    app = QApplication.instance()
    self.zoom_manager.zoom_in(app)

def _zoom_out(self):
    """Handle zoom out action."""
    app = QApplication.instance()
    self.zoom_manager.zoom_out(app)

def _reset_zoom(self):
    """Handle reset zoom action."""
    app = QApplication.instance()
    self.zoom_manager.reset_zoom(app)

def _on_zoom_changed(self, factor: float):
    """Handle zoom level changes.

    Args:
        factor: New zoom factor
    """
    zoom_percent = self.zoom_manager.get_zoom_percentage()
    self.statusBar().showMessage(f"Zoom: {zoom_percent}%", 2000)
```

#### 2d. Add Mouse Wheel Support

```python
# Add wheelEvent override to MainWindow class:

def wheelEvent(self, event):
    """Handle mouse wheel events for zoom control.

    Args:
        event: QWheelEvent
    """
    # Check if Ctrl key is pressed
    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
        # Ctrl+Wheel for zoom
        app = QApplication.instance()
        delta = event.angleDelta().y()

        if delta > 0:
            # Scroll up = zoom in
            self.zoom_manager.zoom_in(app)
        elif delta < 0:
            # Scroll down = zoom out
            self.zoom_manager.zoom_out(app)

        event.accept()  # Mark event as handled
    else:
        # Normal wheel scrolling - pass to parent
        super().wheelEvent(event)
```

#### 2e. Load/Save Zoom Settings

```python
# Modify existing _load_window_state method:
def _load_window_state(self):
    """Load window geometry and state from settings."""
    # ... existing geometry loading code ...

    # NEW: Load zoom level
    app = QApplication.instance()
    self.zoom_manager.initialize_base_font(app)
    self.zoom_manager.apply_saved_zoom(app)

# Modify existing closeEvent method:
def closeEvent(self, event):
    """Handle window close event."""
    self._save_window_state()

    # NEW: Save zoom level
    self.zoom_manager.save_zoom_preference()

    super().closeEvent(event)
```

---

### Step 3: Update Application Startup

**File**: `gui/hstl_gui.py`

Ensure zoom is initialized early in application lifecycle:

```python
def main():
    app = QApplication(sys.argv)

    # Set application metadata
    app.setOrganizationName("HSTL")
    app.setApplicationName("PhotoFramework")

    # Apply theme (existing code)
    from gui.theme_manager import ThemeManager
    theme_manager = ThemeManager.instance()
    theme_manager.apply_saved_theme(app)

    # NEW: Initialize zoom manager with base font
    from gui.zoom_manager import ZoomManager
    zoom_manager = ZoomManager.instance()
    zoom_manager.initialize_base_font(app)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
```

---

## Testing Strategy

### Manual Testing Checklist

#### 1. Basic Zoom Controls
- [ ] Ctrl++ zooms in
- [ ] Ctrl+= zooms in (alternate shortcut)
- [ ] Ctrl+- zooms out
- [ ] Ctrl+0 resets to 100%
- [ ] View menu → Zoom In works
- [ ] View menu → Zoom Out works
- [ ] View menu → Reset Zoom works

#### 2. Mouse Wheel
- [ ] Ctrl+Wheel Up zooms in
- [ ] Ctrl+Wheel Down zooms out
- [ ] Wheel without Ctrl scrolls normally

#### 3. Zoom Levels
- [ ] Zoom stops at 75% minimum
- [ ] Zoom stops at 200% maximum
- [ ] All discrete levels work: 75%, 85%, 100%, 115%, 130%, 150%, 175%, 200%
- [ ] Reset always returns to 100%

#### 4. Persistence
- [ ] Set zoom to 150%, close app, restart → zoom still 150%
- [ ] Set zoom to 75%, close app, restart → zoom still 75%
- [ ] Delete settings, restart → defaults to 100%

#### 5. Status Bar
- [ ] Status bar shows "Zoom: 75%" when at 75%
- [ ] Status bar shows "Zoom: 100%" when at 100%
- [ ] Status bar shows "Zoom: 200%" when at 200%
- [ ] Message clears after 2 seconds

#### 6. UI Layout Behavior
- [ ] All tabs scale correctly at 75%
- [ ] All tabs scale correctly at 200%
- [ ] Batches tab: Table text and rows scale
- [ ] Current Batch tab: Buttons and text scale
- [ ] Configuration tab: Tree text scales
- [ ] Logs tab: Log text scales
- [ ] No layout breakage at any zoom level
- [ ] Window can be resized at all zoom levels

#### 7. Theme Integration
- [ ] Zoom works in Light theme
- [ ] Zoom works in Dark theme
- [ ] Switch theme while zoomed → zoom persists
- [ ] Zoom persists when switching between themes

#### 8. Edge Cases
- [ ] Rapid Ctrl+Wheel scrolling doesn't crash
- [ ] Zoom while tab switching works
- [ ] Zoom while dialog open doesn't affect dialog
- [ ] Window resize + zoom doesn't break layout

### Automated Tests

**File**: `tests/test_zoom_manager.py`

```python
import pytest
from PyQt6.QtWidgets import QApplication
from gui.zoom_manager import ZoomManager

@pytest.fixture
def app(qtbot):
    """Provide QApplication instance."""
    return QApplication.instance()

@pytest.fixture
def zoom_manager():
    """Provide fresh ZoomManager instance."""
    # Reset singleton for testing
    ZoomManager._instance = None
    return ZoomManager.instance()

def test_singleton_pattern(zoom_manager):
    """Test ZoomManager follows singleton pattern."""
    zm2 = ZoomManager.instance()
    assert zoom_manager is zm2

def test_default_zoom(zoom_manager):
    """Test default zoom is 1.0."""
    assert zoom_manager.get_current_zoom() == 1.0

def test_zoom_in(app, zoom_manager):
    """Test zoom in increments correctly."""
    zoom_manager.set_zoom_level(app, 1.0)
    zoom_manager.zoom_in(app)
    assert zoom_manager.get_current_zoom() == 1.15

def test_zoom_out(app, zoom_manager):
    """Test zoom out decrements correctly."""
    zoom_manager.set_zoom_level(app, 1.0)
    zoom_manager.zoom_out(app)
    assert zoom_manager.get_current_zoom() == 0.85

def test_zoom_clamps_at_max(app, zoom_manager):
    """Test zoom doesn't exceed 2.0."""
    zoom_manager.set_zoom_level(app, 2.0)
    zoom_manager.zoom_in(app)
    assert zoom_manager.get_current_zoom() == 2.0

def test_zoom_clamps_at_min(app, zoom_manager):
    """Test zoom doesn't go below 0.75."""
    zoom_manager.set_zoom_level(app, 0.75)
    zoom_manager.zoom_out(app)
    assert zoom_manager.get_current_zoom() == 0.75

def test_reset_zoom(app, zoom_manager):
    """Test reset returns to 1.0."""
    zoom_manager.set_zoom_level(app, 1.5)
    zoom_manager.reset_zoom(app)
    assert zoom_manager.get_current_zoom() == 1.0

def test_zoom_percentage(zoom_manager):
    """Test percentage conversion."""
    zoom_manager._current_zoom = 1.5
    assert zoom_manager.get_zoom_percentage() == 150

def test_zoom_signal_emission(app, zoom_manager, qtbot):
    """Test zoom_changed signal is emitted."""
    with qtbot.waitSignal(zoom_manager.zoom_changed, timeout=1000):
        zoom_manager.set_zoom_level(app, 1.5)

def test_settings_validation(app, zoom_manager):
    """Test invalid settings values are clamped."""
    # Simulate corrupted settings
    zoom_manager.set_zoom_level(app, 10.0)  # Way too high
    assert zoom_manager.get_current_zoom() == 2.0  # Clamped to max

    zoom_manager.set_zoom_level(app, 0.1)  # Way too low
    assert zoom_manager.get_current_zoom() == 0.75  # Clamped to min
```

---

## Files to Create/Modify

### New Files
- `gui/zoom_manager.py` - ZoomManager singleton class
- `tests/test_zoom_manager.py` - Unit tests

### Modified Files
- `gui/main_window.py` - Add View menu, shortcuts, wheel events, zoom methods
- `gui/hstl_gui.py` - Initialize zoom manager on startup

---

## What Gets Scaled (Automatically)

With font scaling, Qt layouts automatically adjust:

✅ **Text Elements**:
- All button text
- All label text
- Table cell text
- Tree item text
- Menu text
- Status bar text
- Log output text

✅ **Layout Elements** (Qt adjusts automatically):
- Button sizes (expand to fit text)
- Table row heights (expand for taller text)
- Tree item heights (expand for taller text)
- Widget minimum sizes (based on content)
- Spacing between elements (proportional to font metrics)

✅ **What Works Out of the Box**:
- QTableWidget automatically adjusts row heights for font size
- QTreeWidget automatically adjusts item heights for font size
- QPushButton automatically resizes to fit text
- QLabel automatically wraps/resizes based on font
- QTextEdit automatically handles larger fonts

---

## What Might Need Future Attention

⚠️ **Elements That May Not Scale** (defer to later if needed):
- Fixed-size icons (if any)
- Custom-drawn elements
- Fixed pixel dimensions in stylesheets
- Progress bar sizes
- Spacer pixel values

**MVP Approach**: Only add custom scaling if users report issues.

---

## Advantages of Font-Only Scaling

1. **Simple**: ~150 lines of code total
2. **Maintainable**: No per-widget custom code
3. **Testable**: Easy to verify font sizes
4. **Qt-Native**: Leverages Qt's built-in layout system
5. **Robust**: Layouts automatically adapt to font changes
6. **Extensible**: Can add dimension scaling later if needed

---

## Success Criteria

- [ ] Users can zoom from 75% to 200% using all input methods
- [ ] Zoom level persists across application restarts
- [ ] UI remains functional and readable at all zoom levels
- [ ] No layout breakage or overlapping elements
- [ ] Status bar shows current zoom level
- [ ] Performance is smooth (no lag)
- [ ] Integration works with existing theme system

---

## Next Steps After MVP

**If font scaling alone is sufficient**:
- ✅ Ship it! No further work needed.
- Document success and close feature request.

**If users report issues**:
1. Collect specific feedback on what doesn't scale well
2. Evaluate whether Qt stylesheet dimension scaling would help
3. Only then consider widget-specific scaling for problem areas

**Do NOT**:
- Pre-optimize for theoretical issues
- Add complexity before validating user needs
- Implement widget-specific scaling unless absolutely necessary

---

## Implementation Time Estimate

- **ZoomManager class**: 1-2 hours
- **MainWindow integration**: 1-2 hours
- **Testing**: 1-2 hours
- **Total**: 3-6 hours

Compare to full plan with widget-specific scaling: 15-20 hours

---

**Priority**: High
**Risk**: Low (simple, well-understood approach)
**Recommendation**: Implement as MVP, evaluate, iterate if needed
