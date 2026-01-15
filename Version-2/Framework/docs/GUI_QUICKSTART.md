# HSTL Photo Framework GUI - Quick Start Guide

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This will install PyQt6 and all other required packages.

2. **Verify Installation**
   ```bash
   python -c "import PyQt6; print('PyQt6 installed successfully')"
   ```

## Launching the GUI

From the Framework directory:
```bash
python gui/hstl_gui.py
```

Or navigate to the gui directory:
```bash
cd gui
python hstl_gui.py
```

## First-Time Setup

### Creating Your First Batch

1. **Launch the Application**
   - The GUI will open showing the "Batches" tab

2. **Create a New Batch**
   - Click **File → New Batch** (or press **Ctrl+N**)
   - Enter a project name (e.g., "January 2025 Batch")
   - Choose a location option:
     - **Default**: Uses `C:\Data\HSTL_Batches\[ProjectName]`
     - **Custom Base**: Pick a base directory, project folder created inside
     - **Full Custom**: Specify exact path
   - Click **OK**

3. **Batch Created!**
   - The new batch appears in the list
   - Directory structure is automatically created
   - Configuration file is generated

## Working with Batches

### Viewing All Batches

The **Batches** tab shows:
- Batch name and status (Active/Completed/Archived)
- Progress bar (0-100% based on completed steps)
- Completed steps count (X/8)
- Last accessed timestamp
- Batch ID

**Tip**: Check "Show All (including archived)" to see completed/archived batches

### Opening a Batch

**Method 1**: Double-click the batch in the list

**Method 2**: Right-click → "Open Batch"

**Method 3**: File → Open Config → Select the batch's config file

### Batch Context Menu

Right-click any batch for quick actions:
- **Open Batch** - Load and switch to this batch
- **Show Info** - View detailed batch information
- **Mark as Complete** - Mark all processing done
- **Archive** - Move to archived state
- **Reactivate** - Return to active state
- **Remove from Registry** - Unregister (files preserved)

## Processing Steps

### Current Batch Tab

After opening a batch, the "Current Batch" tab shows:
- Batch name and progress summary
- 8 processing steps in a grid layout
- Action buttons (Run All, Run Next, Validate)
- Output/log viewer

### Step Status Indicators

- ⭕ **Pending** - Not yet completed
- 🔄 **Running** - Currently processing
- ✅ **Completed** - Successfully finished
- ❌ **Failed** - Error occurred

### Running Steps

**Individual Step**:
1. Click the "Run" button on any step
2. Watch progress in the Output panel
3. Status updates automatically

**Run All Steps**:
1. Click "Run All Steps" button
2. Confirm the operation
3. All 8 steps execute in sequence

**Run Next Step**:
- Automatically runs the next pending step
- Perfect for sequential workflow

**Validate All**:
- Runs validation checks on completed steps
- Reports any issues found

**Revert Step**:
- Click the "Revert" button next to any completed step
- Confirms before reverting
- Marks step as Pending (output files are NOT deleted)
- Useful for re-running steps or corrections

## Configuration

### Viewing Configuration

1. Switch to the **Configuration** tab
2. Browse settings in tree view
3. See all project settings organized hierarchically

Key sections:
- **project**: Name, data directory, metadata
- **steps_completed**: Status of each step (true/false)
- **step_configurations**: Step-specific settings
- **validation**: Validation rules

## Menu Bar

### File Menu
- **New Batch** (Ctrl+N) - Create new batch
- **Open Config** (Ctrl+O) - Open config file
- **Exit** (Ctrl+Q) - Close application

### Batch Menu
- **Refresh Batches** (F5) - Reload batch list
- **Mark as Complete** - Complete current batch
- **Archive** - Archive current batch
- **Reactivate** - Reactivate current batch

### Tools Menu
- **Validate Project** (Ctrl+V) - Run validation
- **Settings** - Application preferences

### Help Menu
- **About** - Version and info

## Tips & Best Practices

### Workflow Tips

1. **Create Batches First**: Set up all batches before processing
2. **Use Descriptive Names**: Include date or collection info
3. **Check Progress Often**: Use F5 to refresh status
4. **Validate Before Completion**: Run validation before marking complete

### Managing Multiple Batches

1. **Active vs Archived**: 
   - Keep current work as "active"
   - Archive completed projects
   
2. **Quick Switching**:
   - Double-click to switch between batches
   - Last opened batch loads on startup

3. **Cleanup**:
   - Archive when done
   - Remove from registry when no longer needed
   - Manually delete files if required

### Data Organization

**Standard Directory Structure**:
```
C:\Data\HSTL_Batches\
├── January_2025\
│   ├── input\
│   │   ├── tiff\          # Place source TIFFs here
│   │   └── spreadsheet\   # Place spreadsheet exports here
│   ├── output\
│   │   ├── csv\
│   │   ├── tiff_processed\
│   │   ├── jpeg\
│   │   ├── jpeg_resized\
│   │   └── jpeg_watermarked\
│   ├── logs\
│   ├── reports\
│   └── config\
│       └── project_config.yaml
```

## Troubleshooting

### GUI Won't Start

**Error**: `ModuleNotFoundError: No module named 'PyQt6'`
- **Solution**: `pip install PyQt6`

**Error**: Import errors for other modules
- **Solution**: `pip install -r requirements.txt`

### Batch Not Showing

- Click "Refresh" button or press F5
- Check "Show All" to see archived batches
- Verify registry file: `Framework/config/batch_registry.yaml`

### Step Won't Run

- Ensure batch is opened (switch to Current Batch tab)
- Check Output panel for error messages
- Verify input files are in correct directories

### Configuration Not Loading

- Verify config file exists: `[batch_dir]/config/project_config.yaml`
- Try File → Open Config and select manually
- Check file permissions

## Advanced Features

### Window State Persistence

The GUI remembers:
- Window size and position
- Last opened batch
- Tab selection

Settings stored in system-specific location:
- **Windows**: Registry or AppData
- **macOS**: ~/Library/Preferences
- **Linux**: ~/.config

### Keyboard Navigation

- **Tab** - Move between controls
- **Arrow Keys** - Navigate tables and lists
- **Enter** - Activate selected item
- **Escape** - Cancel dialogs

## Need Help?

- Check `gui/README.md` for detailed documentation
- Review main `README.md` for framework overview
- See `docs/DEVELOPMENT_PLAN.md` for architecture details

## What's Next?

After creating and processing batches:

1. **Review Outputs**: Check `output/` directories
2. **Validate Results**: Use validation tools
3. **Generate Reports**: Review `reports/` directory
4. **Complete Batch**: Mark as complete when done
5. **Archive**: Archive finished work
6. **Deliver**: Export processed files for delivery

---

**Version:** 0.1.5e
**Commit Date:** 2026-01-15 13:53 CST
**Last Updated:** January 2026
