"""
Main Window for HSTL Photo Framework GUI

Provides the primary interface for batch management, step execution, and configuration.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QAction

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent.parent
sys.path.insert(0, str(framework_dir))

from hstl_framework import HSLTFramework
from utils.batch_registry import BatchRegistry
from gui.widgets.batch_list_widget import BatchListWidget
from gui.widgets.step_widget import StepWidget
from gui.widgets.config_widget import ConfigWidget
from gui.widgets.log_widget import LogWidget
from gui.dialogs.new_batch_dialog import NewBatchDialog
from gui.dialogs.settings_dialog import SettingsDialog
from gui.dialogs.set_data_location_dialog import SetDataLocationDialog


class MainWindow(QMainWindow):
    """Main window for the HSTL Photo Framework GUI."""
    
    batch_changed = pyqtSignal(str, dict)  # batch_id, batch_info
    
    def __init__(self):
        super().__init__()
        
        self.framework = HSLTFramework()
        self.registry = BatchRegistry()
        self.current_batch_id = None
        self.settings = QSettings("HSTL", "PhotoFramework")
        
        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._load_window_state()
        self._refresh_batch_list()
        
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("HSTL Photo Framework")
        self.setMinimumSize(800, 600)  # Reduced minimum size for better resizability
        self.resize(1200, 800)  # Default size
        
        # Create central widget with tab interface
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self._create_batches_tab()
        self._create_current_batch_tab()
        self._create_config_tab()
        self._create_logs_tab()
        
        # Connect signals
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
    def _create_batches_tab(self):
        """Create the batches management tab."""
        self.batch_list_widget = BatchListWidget(self.registry)
        self.batch_list_widget.batch_selected.connect(self._on_batch_selected)
        self.batch_list_widget.batch_action_requested.connect(self._handle_batch_action)
        
        self.tabs.addTab(self.batch_list_widget, "Batches")
        
    def _create_current_batch_tab(self):
        """Create the current batch/step execution tab."""
        self.step_widget = StepWidget()
        self.step_widget.step_executed.connect(self._on_step_executed)
        
        # Wrap in scroll area to handle small window sizes
        scroll = QScrollArea()
        scroll.setWidget(self.step_widget)
        scroll.setWidgetResizable(True)  # Important: allows content to resize
        
        self.tabs.addTab(scroll, "Current Batch")
        
    def _create_config_tab(self):
        """Create the configuration editor tab."""
        self.config_widget = ConfigWidget()
        self.config_widget.config_changed.connect(self._on_config_changed)
        
        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.config_widget)
        scroll.setWidgetResizable(True)
        
        self.tabs.addTab(scroll, "Configuration")
        
    def _create_logs_tab(self):
        """Create the logs viewer tab."""
        self.log_widget = LogWidget()
        
        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.log_widget)
        scroll.setWidgetResizable(True)
        
        self.tabs.addTab(scroll, "Logs")
        
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_batch_action = QAction("&New Batch...", self)
        new_batch_action.setShortcut("Ctrl+N")
        new_batch_action.triggered.connect(self._new_batch)
        file_menu.addAction(new_batch_action)
        
        open_config_action = QAction("&Open Config...", self)
        open_config_action.setShortcut("Ctrl+O")
        open_config_action.triggered.connect(self._open_config)
        file_menu.addAction(open_config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        set_location_action = QAction("Set &Location of Data Files...", self)
        set_location_action.triggered.connect(self._set_data_location)
        edit_menu.addAction(set_location_action)
        
        # Batch menu
        batch_menu = menubar.addMenu("&Batch")
        
        refresh_action = QAction("&Refresh Batches", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_batch_list)
        batch_menu.addAction(refresh_action)
        
        batch_menu.addSeparator()
        
        complete_action = QAction("Mark as &Complete", self)
        complete_action.triggered.connect(lambda: self._batch_action("complete"))
        batch_menu.addAction(complete_action)
        
        archive_action = QAction("&Archive", self)
        archive_action.triggered.connect(lambda: self._batch_action("archive"))
        batch_menu.addAction(archive_action)
        
        reactivate_action = QAction("&Reactivate", self)
        reactivate_action.triggered.connect(lambda: self._batch_action("reactivate"))
        batch_menu.addAction(reactivate_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        validate_action = QAction("&Validate Project", self)
        validate_action.setShortcut("Ctrl+V")
        validate_action.triggered.connect(self._validate_project)
        tools_menu.addAction(validate_action)
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        quickstart_action = QAction("Quick Start &Guide", self)
        quickstart_action.setShortcut("F1")
        quickstart_action.triggered.connect(self._show_quickstart)
        help_menu.addAction(quickstart_action)
        
        changelog_action = QAction("&Change Log", self)
        changelog_action.triggered.connect(self._show_changelog)
        help_menu.addAction(changelog_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def _new_batch(self):
        """Show dialog to create a new batch."""
        dialog = NewBatchDialog(self)
        if dialog.exec():
            project_name, data_dir = dialog.get_values()
            
            # Initialize the batch
            success = self.framework.init_project(data_dir, project_name)
            
            if success:
                self.status_bar.showMessage(f"Created batch: {project_name}", 3000)
                self._refresh_batch_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to create batch")
                
    def _open_config(self):
        """Open a configuration file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Configuration",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if file_name:
            config_path = Path(file_name)
            if self.framework.initialize(config_path):
                self.status_bar.showMessage(f"Loaded: {config_path.name}", 3000)
                self._load_current_batch(config_path)
            else:
                QMessageBox.warning(self, "Error", f"Failed to load config: {config_path}")
                
    def _refresh_batch_list(self):
        """Refresh the batch list."""
        # Reload main window's registry as well
        self.registry.batches = self.registry._load_registry()
        self.batch_list_widget.refresh()
        
    def _on_batch_selected(self, batch_id: str, batch_info: dict):
        """Handle batch selection."""
        self.current_batch_id = batch_id
        config_path = Path(batch_info['config_path'])
        
        # Initialize framework with this batch
        if self.framework.initialize(config_path):
            self.batch_changed.emit(batch_id, batch_info)
            
            # Update last accessed timestamp
            self.registry.update_last_accessed(batch_id)
            
            # Update widgets
            self.step_widget.set_batch(self.framework, batch_id, batch_info)
            self.config_widget.set_config(self.framework.config_manager)
            
            # Update status bar
            self.status_bar.showMessage(f"Current batch: {batch_info['name']}")
            
            # Switch to current batch tab
            self.tabs.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", f"Failed to load batch: {batch_info['name']}")
            
    def _handle_batch_action(self, action: str, batch_id: str):
        """Handle batch action requests."""
        batch = self.registry.get_batch(batch_id)
        if not batch:
            return
            
        if action == "complete":
            self.framework.complete_batch(batch_id)
        elif action == "archive":
            self.framework.archive_batch(batch_id)
        elif action == "reactivate":
            self.framework.reactivate_batch(batch_id)
        elif action == "remove":
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Remove batch '{batch['name']}' from registry?\n\n"
                f"Files will NOT be deleted.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.framework.remove_batch(batch_id, confirm=True)
        elif action == "info":
            from gui.dialogs.batch_info_dialog import BatchInfoDialog
            dialog = BatchInfoDialog(batch_id, self.registry, self)
            dialog.exec()
            
        # Refresh list after action
        self._refresh_batch_list()
        
    def _batch_action(self, action: str):
        """Execute batch action on current batch."""
        if not self.current_batch_id:
            QMessageBox.information(self, "No Batch", "Please select a batch first")
            return
            
        self._handle_batch_action(action, self.current_batch_id)
        
    def _on_step_executed(self, step_num: int, success: bool):
        """Handle step execution completion."""
        if success:
            self.status_bar.showMessage(f"Step {step_num} completed", 3000)
            # Refresh batch list to update progress
            self._refresh_batch_list()
        else:
            self.status_bar.showMessage(f"Step {step_num} failed", 3000)
            
    def _on_config_changed(self):
        """Handle configuration changes."""
        self.status_bar.showMessage("Configuration updated", 2000)
        
    def _on_tab_changed(self, index: int):
        """Handle tab changes."""
        tab_names = ["Batches", "Current Batch", "Configuration", "Logs"]
        if index < len(tab_names):
            self.status_bar.showMessage(f"Viewing: {tab_names[index]}", 2000)
            
    def _validate_project(self):
        """Validate current project."""
        if not self.framework.config_manager:
            QMessageBox.information(self, "No Project", "Please select a batch first")
            return
            
        success = self.framework.validate()
        if success:
            QMessageBox.information(self, "Validation", "Project validation completed successfully")
        else:
            QMessageBox.warning(self, "Validation", "Project validation found issues")
            
    def _set_data_location(self):
        """Show dialog to set default data files location."""
        dialog = SetDataLocationDialog(self)
        if dialog.exec():
            new_location = dialog.get_location()
            self.status_bar.showMessage(f"Default batch location set to: {new_location}", 5000)
            QMessageBox.information(
                self,
                "Location Updated",
                f"Default batch location has been updated to:\n\n{new_location}\n\n"
                "This will be used for new batches created from the File → New Batch menu."
            )
    
    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def _show_quickstart(self):
        """Open the Quick Start Guide."""
        import os
        import subprocess
        
        # Get path to GUI_QUICKSTART.md
        quickstart_path = Path(__file__).parent.parent / 'GUI_QUICKSTART.md'
        
        if quickstart_path.exists():
            # Try to open with default markdown viewer or text editor
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(str(quickstart_path))
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(quickstart_path)])
                
                self.status_bar.showMessage("Opening Quick Start Guide...", 2000)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Cannot Open File",
                    f"Could not open Quick Start Guide.\n\n"
                    f"Please open manually:\n{quickstart_path}\n\n"
                    f"Error: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Quick Start Guide not found at:\n{quickstart_path}"
            )
    
    def _show_changelog(self):
        """Open the Change Log."""
        import os
        import subprocess
        
        # Get path to CHANGELOG.md
        changelog_path = Path(__file__).parent.parent / 'CHANGELOG.md'
        
        if changelog_path.exists():
            # Try to open with default markdown viewer or text editor
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(str(changelog_path))
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(changelog_path)])
                
                self.status_bar.showMessage("Opening Change Log...", 2000)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Cannot Open File",
                    f"Could not open Change Log.\n\n"
                    f"Please open manually:\n{changelog_path}\n\n"
                    f"Error: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Change Log not found at:\n{changelog_path}"
            )
        
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About HSTL Photo Framework",
            "<h3>HSTL Photo Framework GUI</h3>"
                f"<p><b>Version:</b> 0.0.10</p>"
                f"<p><b>Commit Date:</b> 2025-12-14 14:20</p>"
            "<br>"
            "<p>A comprehensive framework for managing photo metadata processing workflows.</p>"
            "<p>Orchestrates 8 steps of photo metadata processing from Google Worksheet "
            "preparation through final watermarked JPEG creation.</p>"
            "<br>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Multi-batch management with progress tracking</li>"
            "<li>Visual step execution interface</li>"
            "<li>Configuration management</li>"
            "<li>Step revert capability</li>"
            "</ul>"
        )
        
    def _load_current_batch(self, config_path: Path):
        """Load current batch from config path."""
        # Find batch by config path
        result = self.registry.find_batch_by_config(str(config_path))
        if result:
            batch_id, batch_info = result
            self._on_batch_selected(batch_id, batch_info)
            
    def _load_window_state(self):
        """Load window state from settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
            
        # Load last opened batch
        last_batch = self.settings.value("lastBatch")
        if last_batch:
            batch = self.registry.get_batch(last_batch)
            if batch:
                self._on_batch_selected(last_batch, batch)
                
    def _save_window_state(self):
        """Save window state to settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        if self.current_batch_id:
            self.settings.setValue("lastBatch", self.current_batch_id)
            
    def closeEvent(self, event):
        """Handle window close event."""
        self._save_window_state()
        event.accept()
