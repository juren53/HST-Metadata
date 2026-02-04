"""
Main Window for HSTL Photo Framework GUI

Provides the primary interface for batch management, step execution, and configuration.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QMenuBar,
    QMenu,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QScrollArea,
    QApplication,
    QDialog,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QThread
from PyQt6.QtGui import QAction

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent.parent
sys.path.insert(0, str(framework_dir))

from hstl_framework import HSLTFramework
from utils.batch_registry import BatchRegistry
from utils.github_version_checker import GitHubVersionChecker, VersionCheckResult
from utils.git_updater import GitUpdater, GitUpdateResult
from gui.widgets.batch_list_widget import BatchListWidget
from gui.widgets.step_widget import StepWidget
from gui.widgets.config_widget import ConfigWidget
from gui.widgets.enhanced_log_widget import EnhancedLogWidget
from gui.dialogs.new_batch_dialog import NewBatchDialog
from gui.dialogs.log_viewer_dialog import LogViewerDialog
from utils.log_manager import LogManager
from pyqt_app_info import AppIdentity, ToolSpec, ToolRegistry, gather_info
from pyqt_app_info.qt import AboutDialog
from gui.dialogs.settings_dialog import SettingsDialog
from gui.dialogs.set_data_location_dialog import SetDataLocationDialog
from gui.zoom_manager import ZoomManager
from __init__ import __version__, __commit_date__


class MainWindow(QMainWindow):
    """Main window for the HSTL Photo Framework GUI."""

    batch_changed = pyqtSignal(str, dict)  # batch_id, batch_info

    def __init__(self):
        super().__init__()

        self.framework = HSLTFramework()
        self.registry = BatchRegistry()
        self.current_batch_id = None
        self.settings = QSettings("HSTL", "PhotoFramework")

        # Initialize zoom manager
        self.zoom_manager = ZoomManager.instance()
        self.zoom_manager.zoom_changed.connect(self._on_zoom_changed)

        # Initialize version checker
        self.version_checker = GitHubVersionChecker(
            repo_url="juren53/HST-Metadata", current_version=__version__, timeout=10
        )

        # Initialize git updater
        try:
            self.git_updater = GitUpdater()
        except ValueError:
            self.git_updater = None  # Not in a git repository

        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._load_window_state()
        self._refresh_batch_list()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"HSTL Photo Framework v{__version__}")
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
        # Initialize log manager
        self.log_manager = LogManager.instance()

        # Apply saved logging enabled setting BEFORE setup to prevent early messages
        logging_enabled = self.settings.value("logging/enabled", True, type=bool)
        self.log_manager.set_enabled(logging_enabled)

        # Set up session logging to capture all log messages
        from pathlib import Path

        log_dir = Path.home() / ".hstl_photo_framework" / "logs"
        self.log_manager.setup_session_logging(log_dir, verbosity="normal")

        # Apply saved console capture setting
        console_capture = self.settings.value("logging/console_capture", False, type=bool)
        if console_capture:
            self.log_manager.enable_console_capture()

        # Create enhanced log widget
        self.log_widget = EnhancedLogWidget()
        self.log_widget.pop_out_requested.connect(self._pop_out_logs)

        # Connect log manager's GUI handler to the widget
        gui_handler = self.log_manager.get_gui_handler()
        gui_handler.log_emitted.connect(self.log_widget.append_log)

        # Pop-out dialog reference
        self.log_viewer_dialog = None

        # Log application start
        self.log_manager.info("HPM application started")

        self.tabs.addTab(self.log_widget, "Logs")

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

        # Theme selection menu item
        theme_action = QAction("&Theme Selection...", self)
        theme_action.triggered.connect(self._show_theme_dialog)
        edit_menu.addAction(theme_action)

        # View menu
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

        # Log viewer
        view_menu.addSeparator()
        pop_out_logs_action = QAction("Pop Out &Logs", self)
        pop_out_logs_action.setShortcut("Ctrl+L")
        pop_out_logs_action.setStatusTip("Open logs in a separate window")
        pop_out_logs_action.triggered.connect(self._pop_out_logs)
        view_menu.addAction(pop_out_logs_action)

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

        browse_files_action = QAction('&Browse Files...', self)
        browse_files_action.setShortcut('Ctrl+B')
        browse_files_action.triggered.connect(self._browse_files)
        tools_menu.addAction(browse_files_action)

        batch_summary_action = QAction('Batch &Data Summary...', self)
        batch_summary_action.setShortcut('Ctrl+D')
        batch_summary_action.triggered.connect(self._show_batch_data_summary)
        tools_menu.addAction(batch_summary_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        user_guide_action = QAction("&User Guide", self)
        user_guide_action.setShortcut("F1")
        user_guide_action.triggered.connect(self._show_user_guide)
        help_menu.addAction(user_guide_action)

        changelog_action = QAction("&Change Log", self)
        changelog_action.triggered.connect(self._show_changelog)
        help_menu.addAction(changelog_action)

        help_menu.addSeparator()

        issue_tracker_action = QAction("HPM &Issue Tracker", self)
        issue_tracker_action.triggered.connect(self._show_issue_tracker)
        help_menu.addAction(issue_tracker_action)

        help_menu.addSeparator()

        # Get latest updates menu item
        get_updates_action = QAction("Get &Latest Updates", self)
        get_updates_action.triggered.connect(self._on_get_latest_updates)
        help_menu.addAction(get_updates_action)

        help_menu.addSeparator()

        about_action = QAction("\u0026About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add permanent version label to right side of status bar
        version_label = QLabel(f"v{__version__} | {__commit_date__}")
        version_label.setStyleSheet("QLabel { color: gray; }")
        self.status_bar.addPermanentWidget(version_label)

    def _new_batch(self):
        """Show dialog to create a new batch."""
        dialog = NewBatchDialog(self)
        if dialog.exec():
            project_name, data_dir = dialog.get_values()

            self.log_manager.info(f"Creating new batch: {project_name}")

            # Initialize the batch
            success = self.framework.init_project(data_dir, project_name)

            if success:
                self.log_manager.info(
                    f"Batch created successfully: {project_name} at {data_dir}"
                )
                self.status_bar.showMessage(f"Created batch: {project_name}", 3000)
                self._refresh_batch_list()
            else:
                self.log_manager.error(f"Failed to create batch: {project_name}")
                QMessageBox.warning(self, "Error", "Failed to create batch")

    def _open_config(self):
        """Open a configuration file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration", "", "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if file_name:
            config_path = Path(file_name)
            if self.framework.initialize(config_path):
                self.status_bar.showMessage(f"Loaded: {config_path.name}", 3000)
                self._load_current_batch(config_path)
            else:
                QMessageBox.warning(
                    self, "Error", f"Failed to load config: {config_path}"
                )

    def _refresh_batch_list(self):
        """Refresh the batch list."""
        # Reload main window's registry as well
        self.registry.batches = self.registry._load_registry()
        self.batch_list_widget.refresh()

    def _on_batch_selected(self, batch_id: str, batch_info: dict):
        """Handle batch selection."""
        self.current_batch_id = batch_id
        config_path = Path(batch_info["config_path"])

        # Initialize framework with this batch
        if self.framework.initialize(config_path):
            self.batch_changed.emit(batch_id, batch_info)

            # Update last accessed timestamp
            self.registry.update_last_accessed(batch_id)

            # Update widgets
            self.step_widget.set_batch(self.framework, batch_id, batch_info)
            self.config_widget.set_config(self.framework.config_manager)

            # Set up per-batch logging
            data_dir = Path(batch_info.get("data_directory", ""))
            if data_dir.exists():
                self.log_manager.setup_batch_logging(batch_id, data_dir)

            # Add batch to log filter dropdown and update batch name display
            self.log_widget.add_batch_option(batch_id, batch_info["name"])
            self.log_widget.set_batch_name(batch_info["name"])
            if self.log_viewer_dialog:
                self.log_viewer_dialog.add_batch_option(batch_id, batch_info["name"])
                self.log_viewer_dialog.set_batch_name(batch_info["name"])

            # Log batch selection
            self.log_manager.info(
                f"Selected batch: {batch_info['name']}", batch_id=batch_id
            )

            # Update status bar
            self.status_bar.showMessage(f"Current batch: {batch_info['name']}")

            # Switch to current batch tab
            self.tabs.setCurrentIndex(1)
        else:
            QMessageBox.warning(
                self, "Error", f"Failed to load batch: {batch_info['name']}"
            )

    def _handle_batch_action(self, action: str, batch_id: str):
        """Handle batch action requests."""
        batch = self.registry.get_batch(batch_id)
        if not batch:
            return

        if action == "complete":
            self.log_manager.info(
                f"Marking batch as complete: {batch['name']}", batch_id=batch_id
            )
            self.framework.complete_batch(batch_id)
        elif action == "archive":
            self.log_manager.info(
                f"Archiving batch: {batch['name']}", batch_id=batch_id
            )
            self.framework.archive_batch(batch_id)
        elif action == "reactivate":
            self.log_manager.info(
                f"Reactivating batch: {batch['name']}", batch_id=batch_id
            )
            self.framework.reactivate_batch(batch_id)
        elif action == "remove":
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Remove batch '{batch['name']}' from registry?\n\n"
                f"Files will NOT be deleted.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.log_manager.info(
                    f"Removing batch from registry: {batch['name']}", batch_id=batch_id
                )
                self.framework.remove_batch(batch_id, confirm=True)
                self.log_manager.info(f"Batch removed from registry: {batch['name']}")
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
        self.status_bar.showMessage(f"Zoom: {zoom_percent}%", 2000)

    def _pop_out_logs(self):
        """Open logs in a separate window."""
        if self.log_viewer_dialog is None:
            # Create new dialog
            self.log_viewer_dialog = LogViewerDialog(self)
            self.log_viewer_dialog.closed.connect(self._on_log_viewer_closed)

            # Connect log manager to pop-out dialog as well
            gui_handler = self.log_manager.get_gui_handler()
            gui_handler.log_emitted.connect(self.log_viewer_dialog.append_log)

            # Copy existing records to the pop-out
            for record in self.log_widget.get_records():
                self.log_viewer_dialog.append_log(record)

            # Set the current batch name in the title bar
            if self.current_batch_id:
                batch_info = self.registry.get_batch(self.current_batch_id)
                if batch_info:
                    self.log_viewer_dialog.set_batch_name(batch_info.get("name", ""))

        self.log_viewer_dialog.show_and_raise()
        self.status_bar.showMessage("Log viewer opened in separate window", 2000)

    def _on_log_viewer_closed(self):
        """Handle log viewer dialog close."""
        self.log_viewer_dialog = None

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

    def _validate_project(self):
        """Validate current project."""
        if not self.framework.config_manager:
            QMessageBox.information(self, "No Project", "Please select a batch first")
            return

        success = self.framework.validate()
        if success:
            QMessageBox.information(
                self, "Validation", "Project validation completed successfully"
            )
        else:
            QMessageBox.warning(self, "Validation", "Project validation found issues")

    def _browse_files(self):
        '''Open file browser for current batch data directory.'''
        if not self.current_batch_id:
            QMessageBox.information(self, 'No Batch', 'Please select a batch first')
            return
        
        # Get current batch info
        batch_info = self.registry.get_batch(self.current_batch_id)
        data_directory = batch_info.get('data_directory', '')
        
        if not data_directory:
            QMessageBox.warning(
                self,
                'No Data Directory',
                'Data directory is not configured for this batch.',
            )
            return

        # Convert to Path object
        target_dir = Path(data_directory)
        
        # Check if directory exists
        if not target_dir.exists():
            QMessageBox.warning(
                self,
                'Directory Not Found',
                f'Data directory not found:\n\n{target_dir}\n\n'
                'Please check if the directory exists.',
            )
            return

        # Open directory in File Explorer using QDesktopServices
        try:
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            
            url = QUrl.fromLocalFile(str(target_dir))
            if QDesktopServices.openUrl(url):
                self.status_bar.showMessage(f'Opened data directory: {target_dir.name}', 3000)
            else:
                QMessageBox.warning(
                    self, 'Failed to Open', f'Could not open directory:\n\n{target_dir}'
                )
        except Exception as e:
            QMessageBox.critical(
                self, 'Error', f'Failed to open directory:\n\n{str(e)}'
            )

    def _show_batch_data_summary(self):
        """Show batch data directory summary dialog."""
        if not self.current_batch_id:
            QMessageBox.information(self, 'No Batch', 'Please select a batch first')
            return
        
        # Get current batch info
        batch_info = self.registry.get_batch(self.current_batch_id)
        
        if not batch_info:
            QMessageBox.warning(self, 'Error', 'Could not retrieve batch information')
            return
        
        # Import dialog
        from gui.dialogs.batch_data_summary_dialog import BatchDataSummaryDialog
        
        # Show dialog
        dialog = BatchDataSummaryDialog(batch_info, self)
        dialog.exec()

    def _set_data_location(self):
        """Show dialog to set default data files location."""
        dialog = SetDataLocationDialog(self)
        if dialog.exec():
            new_location = dialog.get_location()
            self.status_bar.showMessage(
                f"Default batch location set to: {new_location}", 5000
            )
            QMessageBox.information(
                self,
                "Location Updated",
                f"Default batch location has been updated to:\n\n{new_location}\n\n"
                "This will be used for new batches created from the File → New Batch menu.",
            )

    def _show_theme_dialog(self):
        """Show theme selection dialog."""
        from gui.dialogs.theme_dialog import ThemeDialog

        dialog = ThemeDialog(self)
        dialog.exec()

    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def _show_user_guide(self):
        """Open the User Guide (local file with GitHub fallback)."""
        import os
        import subprocess
        import webbrowser
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl

        # Get path to USER_GUIDE.md
        user_guide_path = Path(__file__).parent.parent / "docs" / "USER_GUIDE.md"

        # GitHub fallback URL
        github_url = "https://github.com/juren53/HST-Metadata/blob/master/Photos/Version-2/Framework/docs/USER_GUIDE.md"

        if user_guide_path.exists():
            # Try to open with default markdown viewer or text editor
            try:
                if os.name == "nt":  # Windows
                    os.startfile(str(user_guide_path))
                elif os.name == "posix":  # macOS and Linux
                    subprocess.run(
                        [
                            "open" if sys.platform == "darwin" else "xdg-open",
                            str(user_guide_path),
                        ]
                    )

                self.status_bar.showMessage("Opening User Guide...", 2000)
            except Exception as e:
                # Local file exists but couldn't open - try GitHub fallback
                self._open_url_with_fallback(
                    github_url,
                    "User Guide",
                    f"Could not open local User Guide.\n\nOpening online version..."
                )
        else:
            # Local file not found - use GitHub fallback
            self._open_url_with_fallback(
                github_url,
                "User Guide",
                "Local User Guide not found.\n\nOpening online version..."
            )

    def _show_changelog(self):
        """Open the Change Log (local file with GitHub fallback)."""
        import os
        import subprocess
        import webbrowser
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl

        # Get path to CHANGELOG.md
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"

        # GitHub fallback URL
        github_url = "https://github.com/juren53/HST-Metadata/blob/master/Photos/Version-2/Framework/CHANGELOG.md"

        if changelog_path.exists():
            # Try to open with default markdown viewer or text editor
            try:
                if os.name == "nt":  # Windows
                    os.startfile(str(changelog_path))
                elif os.name == "posix":  # macOS and Linux
                    subprocess.run(
                        [
                            "open" if sys.platform == "darwin" else "xdg-open",
                            str(changelog_path),
                        ]
                    )

                self.status_bar.showMessage("Opening Change Log...", 2000)
            except Exception as e:
                # Local file exists but couldn't open - try GitHub fallback
                self._open_url_with_fallback(
                    github_url,
                    "Change Log",
                    f"Could not open local Change Log.\n\nOpening online version..."
                )
        else:
            # Local file not found - use GitHub fallback
            self._open_url_with_fallback(
                github_url,
                "Change Log",
                "Local Change Log not found.\n\nOpening online version..."
            )

    def _open_url_with_fallback(self, url: str, doc_name: str, info_message: str = None):
        """
        Open a URL in the default web browser with fallback options.

        Args:
            url: The URL to open
            doc_name: Name of the document (for status/error messages)
            info_message: Optional info message to show before opening
        """
        import webbrowser
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl

        # Show info message if provided
        if info_message:
            self.status_bar.showMessage(info_message.replace("\n", " "), 3000)

        try:
            # Try to open with Qt's QDesktopServices first
            if QDesktopServices.openUrl(QUrl(url)):
                self.status_bar.showMessage(f"Opening online {doc_name}...", 2000)
                return
        except Exception:
            pass

        # Fallback to webbrowser module
        try:
            webbrowser.open(url)
            self.status_bar.showMessage(f"Opening online {doc_name}...", 2000)
        except Exception as e:
            QMessageBox.warning(
                self,
                f"Cannot Open {doc_name}",
                f"Could not open online {doc_name} in browser.\n\n"
                f"Please open manually:\n{url}\n\n"
                f"Error: {str(e)}",
            )

    def _show_issue_tracker(self):
        """Open HPM Issue Tracker in web browser."""
        import webbrowser
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl

        issue_tracker_url = "https://github.com/juren53/HST-Metadata/issues"

        try:
            # Try to open with system default browser
            QDesktopServices.openUrl(QUrl(issue_tracker_url))
            self.status_bar.showMessage("Opening HPM Issue Tracker...", 2000)
        except Exception as e:
            # Fallback to webbrowser module
            try:
                webbrowser.open(issue_tracker_url)
                self.status_bar.showMessage("Opening HPM Issue Tracker...", 2000)
            except Exception as e2:
                QMessageBox.warning(
                    self,
                    "Cannot Open Issue Tracker",
                    f"Could not open HPM Issue Tracker in browser.\n\n"
                    f"Please open manually:\n{issue_tracker_url}\n\n"
                    f"Primary error: {str(e)}\n"
                    f"Fallback error: {str(e2)}",
                )

    def _show_about(self):
        """Show about dialog."""
        identity = AppIdentity(
            name="HSTL Photo Metadata Framework",
            short_name="HPM",
            version=__version__,
            commit_date=__commit_date__,
            description=(
                "An end-to-end framework for managing photo metadata processing workflows. "
                "Orchestrates 8 steps of photo metadata processing from Excel Spreadsheet "
                "preparation through final watermarked JPEG creation."
            ),
            features=[
                "Multi-batch management with progress tracking",
                "Visual step execution interface",
                "Configuration management",
                "Step revert capability",
            ],
        )

        registry = ToolRegistry()
        registry.register(ToolSpec(
            name="ExifTool", command="exiftool", version_flag="-ver",
        ))

        info = gather_info(identity, registry=registry, caller_file=__file__)
        AboutDialog(info, parent=self).exec()

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

        # Initialize and load zoom settings
        app = QApplication.instance()
        self.zoom_manager.initialize_base_font(app)
        self.zoom_manager.apply_saved_zoom(app)

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

        # Save zoom settings
        self.zoom_manager.save_zoom_preference()

        # Close pop-out log viewer if open
        if self.log_viewer_dialog:
            self.log_viewer_dialog.close()

        # Shutdown log manager
        self.log_manager.shutdown()

        event.accept()

    # Version checking methods
    class UpdateCheckThread(QThread):
        """Thread for checking updates in background"""

        result_ready = pyqtSignal(object)

        def __init__(self, checker):
            super().__init__()
            self.checker = checker

        def run(self):
            result = self.checker.get_latest_version()
            self.result_ready.emit(result)

    def _on_check_for_updates(self):
        """Handle Check for Updates menu action"""
        self.status_bar.showMessage("Checking for updates...")

        # Start background check
        self.update_check_thread = self.UpdateCheckThread(self.version_checker)
        self.update_check_thread.result_ready.connect(self._on_update_check_complete)
        self.update_check_thread.start()

    def _on_update_check_complete(self, result):
        """Handle completion of version check"""
        if result.error_message:
            self.status_bar.showMessage("Update check failed")
            error_msg = result.error_message

            # Provide more helpful message for 404 errors
            if "404" in error_msg and "Not Found" in error_msg:
                friendly_msg = (
                    "HPM repository doesn't have any releases yet.\n\n"
                    "You're using the latest available version!"
                )
                QMessageBox.information(self, "No Releases Available", friendly_msg)
            else:
                QMessageBox.warning(
                    self,
                    "Update Check Failed",
                    f"Could not check for updates:\n\n{error_msg}",
                )
            return

        # Update status
        self.status_bar.showMessage("Update check complete")

        # Check if update available
        if result.has_update:
            self._show_update_dialog(result)
        else:
            self.status_bar.showMessage("You have the latest version")
            QMessageBox.information(
                self,
                "Up to Date",
                f"HPM {result.current_version} is the latest version available.",
            )

    def _show_update_dialog(self, result):
        """Show update available dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Available")
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        # Update information
        info_text = f"""
        <h3>Update Available!</h3>
        <p><b>Current Version:</b> {result.current_version}</p>
        <p><b>Latest Version:</b> {result.latest_version}</p>
        <p><b>Published:</b> {result.published_date[:10]}</p>
        <p><b>Download URL:</b> <a href="{result.download_url}">{result.download_url}</a></p>
        """

        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        # Release notes (if available)
        if result.release_notes:
            layout.addWidget(QLabel("<h4>Release Notes:</h4>"))
            notes_edit = QTextEdit()
            notes_edit.setPlainText(result.release_notes)
            notes_edit.setReadOnly(True)
            notes_edit.setMaximumHeight(150)
            layout.addWidget(notes_edit)

        # Buttons
        button_layout = QHBoxLayout()

        download_btn = QPushButton("Download Update")
        download_btn.clicked.connect(
            lambda: self._on_download_update(result.download_url)
        )
        button_layout.addWidget(download_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def _on_download_update(self, download_url):
        """Open download URL in browser"""
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl

        QDesktopServices.openUrl(QUrl(download_url))
        self.status_bar.showMessage("Opening download page...", 2000)

    # Git update methods
    class GitUpdateThread(QThread):
        """Thread for performing git update in background"""

        result_ready = pyqtSignal(object)

        def __init__(self, updater):
            super().__init__()
            self.updater = updater

        def run(self):
            # Use force_update for clean, reliable updates
            result = self.updater.force_update()
            self.result_ready.emit(result)

    def _on_get_latest_updates(self):
        """
        Handle Get Latest Updates menu action.

        Simplified flow:
        1. Check for git repository
        2. Fetch and compare versions
        3. Show clear version info and confirm
        4. Force update (discards local changes automatically)
        """
        # Check if git updater is available
        if not self.git_updater:
            QMessageBox.warning(
                self,
                "Not a Git Repository",
                "This installation is not in a git repository.\n\n"
                "To update, please download the latest release from GitHub:\n"
                "https://github.com/juren53/HST-Metadata/releases",
            )
            return

        # Check for updates using version comparison
        self.status_bar.showMessage("Checking for updates...")
        update_info = self.git_updater.get_update_info()

        # Handle errors
        if update_info['error']:
            self.status_bar.showMessage("Update check failed")
            QMessageBox.warning(
                self,
                "Update Check Failed",
                f"Could not check for updates:\n\n{update_info['error']}\n\n"
                "Please check your internet connection and try again.",
            )
            return

        current_version = update_info['current_version']
        remote_version = update_info['remote_version']

        # No update available
        if not update_info['update_available']:
            self.status_bar.showMessage("Already up-to-date")
            QMessageBox.information(
                self,
                "Up to Date",
                f"You have the latest version.\n\n"
                f"Current version: v{current_version}",
            )
            return

        # Store remote version for use in completion handler
        self._pending_update_version = remote_version

        # Show update confirmation with clear version info
        reply = QMessageBox.question(
            self,
            "Update Available",
            f"A new version is available!\n\n"
            f"Current version:  v{current_version}\n"
            f"New version:      v{remote_version}\n\n"
            f"Download and install the update?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._perform_git_update(remote_version)

    def _perform_git_update(self, target_version: str = ""):
        """Perform git update in background thread"""
        from PyQt6.QtWidgets import QProgressDialog

        # Build progress message
        if target_version:
            progress_msg = f"Downloading v{target_version} from GitHub...\n\nPlease wait..."
        else:
            progress_msg = "Downloading latest update from GitHub...\n\nPlease wait..."

        # Show progress dialog
        self.progress_dialog = QProgressDialog(
            progress_msg,
            None,  # No cancel button
            0,
            0,
            self,
        )
        self.progress_dialog.setWindowTitle("Updating HPM")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.show()

        # Update status
        self.status_bar.showMessage("Downloading update...")

        # Start background update
        self.git_update_thread = self.GitUpdateThread(self.git_updater)
        self.git_update_thread.result_ready.connect(self._on_git_update_complete)
        self.git_update_thread.start()

    def _on_git_update_complete(self, result: GitUpdateResult):
        """Handle completion of git update operation"""
        # Close progress dialog
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        # Get the target version we were updating to
        target_version = getattr(self, '_pending_update_version', None)

        if result.error_message:
            # Update failed
            self.status_bar.showMessage("Update failed")
            QMessageBox.critical(
                self,
                "Update Failed",
                f"Failed to download update from GitHub:\n\n{result.error_message}",
            )
        elif result.already_up_to_date:
            # Already up-to-date (shouldn't happen normally)
            self.status_bar.showMessage("Already up-to-date")
            QMessageBox.information(
                self,
                "Up to Date",
                f"You already have the latest version (v{result.current_version}).",
            )
        elif result.success:
            # Update successful
            new_version = result.updated_version or target_version or "latest"
            self.status_bar.showMessage(f"Updated to v{new_version}")

            QMessageBox.information(
                self,
                "Update Complete",
                f"Successfully updated to v{new_version}!\n\n"
                f"Please restart HPM for changes to take effect.",
            )
        else:
            # Unknown result
            self.status_bar.showMessage("Update completed")
            QMessageBox.warning(
                self,
                "Update Status Unknown",
                "The update operation completed but the status is unclear.\n\n"
                "Please restart HPM and verify the version.",
            )

        # Clean up
        if hasattr(self, '_pending_update_version'):
            del self._pending_update_version
