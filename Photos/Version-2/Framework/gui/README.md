# HSTL Photo Framework - GUI Application

**Version:** 0.1.7k
**Commit Date:** 2026-01-23 02:07 CST

PyQt6-based graphical user interface for the HSTL Photo Framework.

## Features

### Batch Management
- View all registered batches with status, progress, and completion percentage
- Create new batches with flexible directory options
- Batch lifecycle management (complete, archive, reactivate, remove)
- Context menu for quick actions
- Color-coded status indicators (active/completed/archived)

### Step Execution
- Visual interface for all 8 processing steps
- Individual step execution with status tracking
- **Revert completed steps back to pending status**
- Batch operations (Run All, Run Next)
- Real-time progress feedback
- Output/log viewer for each step

### Configuration Management
- Tree view of project configuration
- View all settings in hierarchical format
- Configuration refresh capability

### User Interface
- Tab-based interface for easy navigation
- Menu bar with keyboard shortcuts
- Status bar with current batch indicator
- Window state persistence (size, position, last batch)
- Responsive design with progress indicators

## Installation

1. Install PyQt6 if not already installed:
```bash
pip install PyQt6>=6.0.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the GUI

```bash
python hstl_gui.py
```

Or from the main framework directory:
```bash
python gui/hstl_gui.py
```

### Quick Start

1. **Create a New Batch**
   - File → New Batch (Ctrl+N)
   - Enter project name
   - Choose location option
   - Click OK

2. **Select a Batch**
   - Double-click a batch in the Batches tab
   - Or right-click → Open Batch

3. **Run Processing Steps**
   - Switch to "Current Batch" tab
   - Click individual step "Run" buttons
   - Or use "Run All Steps" for complete workflow

4. **View Configuration**
   - Switch to "Configuration" tab
   - Browse settings in tree view

## Keyboard Shortcuts

- **Ctrl+N** - New Batch
- **Ctrl+O** - Open Config File
- **Ctrl+Q** - Exit
- **F5** - Refresh Batch List
- **Ctrl+V** - Validate Project

## Architecture

### Main Components

- **MainWindow** - Primary application window with tab interface
- **BatchListWidget** - Displays and manages batch list
- **StepWidget** - Step execution interface
- **ConfigWidget** - Configuration viewer/editor
- **LogWidget** - Log viewer

### Dialogs

- **NewBatchDialog** - Create new batch projects
- **BatchInfoDialog** - Display detailed batch information
- **SettingsDialog** - Application settings (extensible)

## Integration with CLI

The GUI uses the same backend as the CLI (`hstl_framework.py`):
- **HSLTFramework** class for core operations
- **BatchRegistry** for multi-batch tracking
- **ConfigManager** for configuration management
- **PathManager** for path operations

All functionality available in the CLI is accessible through the GUI.

## Development

### Adding New Features

1. **New Widget**: Create in `gui/widgets/`
2. **New Dialog**: Create in `gui/dialogs/`
3. **Update Main Window**: Import and integrate in `main_window.py`

### Extending Step Execution

Step execution currently calls `framework.run_steps()`. To enhance:
- Add threading for long-running operations
- Implement progress callbacks
- Add step-specific dialogs for configuration

## Notes

- Configuration files are managed through the existing YAML system
- All batch operations update the central registry
- Window state and preferences are saved automatically
- The GUI respects all existing framework validation rules

## Future Enhancements

- Real-time log streaming
- Advanced configuration editing (inline)
- Visual file browser integration
- Step-specific progress bars
- Batch comparison tools
- Export/import batch configurations
