# Zoom In/Out Feature Implementation Plan

## Overview

Add zoom-in/out functionality to the HSTL Photo Framework GUI to aid readability on different systems. This feature will provide users with flexible scaling options for improved accessibility and usability across various display configurations.

## Requirements Confirmed

✅ **Zoom Range**: 75% to 200% maximum  
✅ **Persistence**: Remember last used zoom level across app restarts  
✅ **Global Zoom**: Same zoom level applied to all windows/tabs  
✅ **UI Feedback**: Status bar indicator for current zoom level  
✅ **Controls**: Both Ctrl+mouse-wheel and Ctrl+plus/minus enabled  

## Implementation Architecture

### Core Components

#### 1. ZoomManager Class (`gui/zoom_manager.py`)

```python
class ZoomManager(QObject):
    zoom_changed = pyqtSignal(float)  # Emitted when zoom changes
    
    # Zoom levels from 75% to 200%
    ZOOM_LEVELS = [0.75, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
    DEFAULT_ZOOM = 1.0
    MAX_ZOOM = 2.0
    MIN_ZOOM = 0.75
    
    def set_zoom_level(self, factor: float)
    def zoom_in(self)    # 0.15 increment
    def zoom_out(self)   # 0.15 decrement
    def reset_zoom(self) # Back to 1.0
    def get_zoom_percentage(self) -> int  # Return 75, 100, 150, etc.
```

**Key Features:**
- Singleton pattern using `instance()` method (like ThemeManager)
- Signal-based architecture for responsive UI updates
- Use existing `QSettings("HSTL", "PhotoFramework")` for persistence
- Store zoom level as `"ui/zoom_level"` key
- Emit `zoom_changed` signal for widget updates

#### 2. Enhanced MainWindow (`gui/main_window.py`)

**Additions:**
- **View menu** with Zoom In/Out/Reset actions
- **Keyboard shortcuts**: `Ctrl++`, `Ctrl+-`, `Ctrl+0`
- **Status bar integration**: Show current zoom as percentage
- **Mouse wheel support**: Capture Ctrl+wheel events
- **Settings persistence**: Load/save zoom level on startup/shutdown

**Integration Points:**
- Add View menu to `_create_menu_bar()` method
- Override `wheelEvent()` for Ctrl+wheel zoom
- Connect menu actions to ZoomManager methods
- Update status bar with zoom percentage changes

#### 3. Widget Updates

**BatchListWidget**: Scale table row heights and column widths
- Adjust `QTableWidget` row heights proportionally
- Scale column widths and maintain interactive resizing
- Scale progress bar dimensions and status indicators

**StepWidget**: Scale grid spacing, button dimensions
- Scale `QGridLayout` spacing and widget sizes
- Adjust button dimensions and padding
- Scale minimum height for output text area
- Maintain emoji size consistency

**ConfigWidget**: Scale tree indentation and row heights
- Scale `QTreeWidget` row heights and indentation
- Adjust column widths proportionally
- Maintain expand/collapse icon scaling

**LogWidget**: Scale text area and font size
- Scale `QTextEdit` font size and tab width
- Adjust minimum height proportionally
- Maintain text readability

## Detailed Implementation Steps

### Step 1: Create ZoomManager Singleton

1. **File Creation**: `gui/zoom_manager.py`
2. **Singleton Pattern**: 
   ```python
   _instance = None
   
   @classmethod
   def instance(cls):
       if cls._instance is None:
           cls._instance = cls()
       return cls._instance
   ```
3. **Settings Integration**: Use existing QSettings for persistence
4. **Signal System**: Implement `zoom_changed` signal for responsive updates

### Step 2: Menu and Keyboard Integration

1. **View Menu Addition**:
   ```python
   def _create_menu_bar(self):
       # ... existing menus ...
       
       # View menu
       view_menu = menubar.addMenu("&View")
       
       zoom_in_action = QAction("Zoom &In", self)
       zoom_in_action.setShortcut("Ctrl++")
       zoom_in_action.triggered.connect(self.zoom_manager.zoom_in)
       view_menu.addAction(zoom_in_action)
       
       zoom_out_action = QAction("Zoom &Out", self)
       zoom_out_action.setShortcut("Ctrl+-")
       zoom_out_action.triggered.connect(self.zoom_manager.zoom_out)
       view_menu.addAction(zoom_out_action)
       
       zoom_reset_action = QAction("&Reset Zoom", self)
       zoom_reset_action.setShortcut("Ctrl+0")
       zoom_reset_action.triggered.connect(self.zoom_manager.reset_zoom)
       view_menu.addAction(zoom_reset_action)
   ```

2. **Keyboard Shortcuts**: Add alternative Ctrl+= for zoom in
3. **Status Bar Updates**: Show zoom percentage when changed

### Step 3: Global Font Scaling

1. **Font Scaling Logic**:
   ```python
   def apply_font_scaling(self, factor: float):
       app = QApplication.instance()
       base_font = app.font()
       new_size = max(8, min(24, base_font.pointSize() * factor))
       base_font.setPointSize(int(new_size))
       app.setFont(base_font)
   ```

2. **Signal Integration**: Connect to ZoomManager signal
3. **Maintain Relationships**: Preserve relative font sizes (e.g., step names +2pt)

### Step 4: Mouse Wheel Support

1. **Custom ScrollArea**: Subclass for Ctrl+wheel capture
2. **Event Handling**:
   ```python
   def wheelEvent(self, event):
       if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
           delta = event.angleDelta().y()
           if delta > 0:
               self.zoom_manager.zoom_in()
           else:
               self.zoom_manager.zoom_out()
           event.accept()
       else:
           super().wheelEvent(event)
   ```

3. **Integration**: Update tab scroll areas in MainWindow

### Step 5: Widget-Specific Scaling

1. **Signal Connection Pattern**:
   ```python
   def __init__(self):
       # ... existing init code ...
       self.zoom_manager = ZoomManager.instance()
       self.zoom_manager.zoom_changed.connect(self._apply_zoom_scaling)
       
   def _apply_zoom_scaling(self, factor: float):
       # Widget-specific scaling logic
       self._scale_dimensions(factor)
       self._update_layout()
   ```

2. **Per-Widget Implementation**: Custom scaling for each widget type

### Step 6: Settings Integration

1. **Load Settings**:
   ```python
   def _load_window_state(self):
       # ... existing loading code ...
       
       zoom_level = self.settings.value("ui/zoom_level", 1.0, type=float)
       self.zoom_manager.set_zoom_level(zoom_level)
   ```

2. **Save Settings**:
   ```python
   def _save_window_state(self):
       # ... existing saving code ...
       
       self.settings.setValue("ui/zoom_level", self.zoom_manager.current_zoom)
   ```

## Code Integration Examples

### MainWindow Integration

```python
def __init__(self):
    # ... existing init code ...
    self.zoom_manager = ZoomManager.instance()
    self.zoom_manager.zoom_changed.connect(self._on_zoom_changed)
    self._load_zoom_settings()
    
def _on_zoom_changed(self, factor: float):
    zoom_percent = int(factor * 100)
    self.status_bar.showMessage(f"Zoom: {zoom_percent}%", 2000)
    
def _load_zoom_settings(self):
    zoom_level = self.settings.value("ui/zoom_level", 1.0, type=float)
    self.zoom_manager.set_zoom_level(zoom_level)
    
def closeEvent(self, event):
    self._save_window_state()
    self.settings.setValue("ui/zoom_level", self.zoom_manager.current_zoom)
    super().closeEvent(event)
```

### Widget Integration Pattern

```python
# In each widget __init__:
def __init__(self):
    super().__init__()
    # ... existing init code ...
    self.zoom_manager = ZoomManager.instance()
    self.zoom_manager.zoom_changed.connect(self._apply_zoom_scaling)
    self.original_dimensions = self._capture_original_dimensions()
    
def _apply_zoom_scaling(self, factor: float):
    # Apply font scaling (handled globally)
    # Apply dimension scaling
    self._scale_table_dimensions(factor)    # For BatchListWidget
    self._scale_grid_layout(factor)         # For StepWidget
    self._scale_tree_widget(factor)         # For ConfigWidget
    self._scale_text_area(factor)           # For LogWidget
```

## Testing Strategy

### Functional Tests

1. **Zoom Controls**:
   - Test zoom in/out increments of 0.15
   - Verify zoom levels: 75%, 85%, 100%, 115%, 130%, 150%, 175%, 200%
   - Test reset zoom returns to 100%

2. **Persistence**:
   - Set zoom to 150%, close app, restart - should remain 150%
   - Verify settings key "ui/zoom_level" is saved correctly

3. **Keyboard Shortcuts**:
   - `Ctrl++` and `Ctrl+=` should zoom in
   - `Ctrl+-` should zoom out
   - `Ctrl+0` should reset to 100%

4. **Mouse Wheel**:
   - `Ctrl+Wheel Up` should zoom in
   - `Ctrl+Wheel Down` should zoom out
   - Normal wheel scrolling should work without Ctrl

5. **Status Bar**:
   - Should show current zoom percentage
   - Should update on every zoom change
   - Should clear after 2 seconds

6. **Widget Scaling**:
   - Test all four widgets at each zoom level
   - Verify text readability at all zoom levels
   - Check layout integrity at minimum and maximum zoom

### Edge Cases

1. **Maximum/Minimum**: Verify zoom stops at 75% and 200%
2. **Window Resizing**: Ensure zoom works with window size changes
3. **Tab Switching**: Verify consistent zoom across tabs
4. **Theme Changes**: Confirm zoom works with light/dark themes
5. **Font Size Limits**: Verify min 8pt and max 24pt constraints

## Files to Modify/Created

### New Files
- `gui/zoom_manager.py` - Core zoom management singleton

### Modified Files  
- `gui/main_window.py` - Menu, shortcuts, status bar, mouse wheel, settings
- `gui/widgets/batch_list_widget.py` - Table scaling implementation
- `gui/widgets/step_widget.py` - Grid and button scaling implementation
- `gui/widgets/config_widget.py` - Tree scaling implementation  
- `gui/widgets/log_widget.py` - Text area scaling implementation

## Implementation Schedule

### Phase 1: Core Infrastructure (High Priority)
1. ✅ Create `ZoomManager` singleton class
2. ✅ Add View menu with keyboard shortcuts
3. ✅ Implement global font scaling

### Phase 2: User Interface (Medium Priority)
1. ✅ Add Ctrl+wheel zoom support
2. ✅ Add zoom level indicator to status bar
3. ✅ Update all four main widgets with scaling support

### Phase 3: Integration & Polish (Low Priority)
1. ✅ Add zoom persistence to QSettings
2. ✅ Test zoom functionality across all widgets
3. ✅ Performance optimization and edge case handling

## Benefits Summary

- **Accessibility**: Improves readability for users with visual impairments
- **User Experience**: Standard zoom controls familiar from other applications
- **Consistency**: Global zoom applied uniformly across all interface elements
- **Performance**: Efficient font-based scaling with minimal lag
- **Integration**: Seamless integration with existing theme and settings systems
- **Maintainability**: Centralized zoom management following existing patterns

## Success Criteria

- Users can zoom from 75% to 200% using keyboard shortcuts or mouse wheel
- Zoom level persists across application restarts
- All widgets scale properly without layout breakage
- Status bar shows current zoom level
- Performance remains smooth with no noticeable lag
- Integration works seamlessly with existing theme system

---

**Created**: 2026-01-03  
**Status**: Planning Complete - Ready for Implementation  
**Priority**: High - User Requested Feature for Accessibility