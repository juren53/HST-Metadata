# HSTL Photo Metadata System Launcher

A robust Python-based launcher for the HSTL Photo Metadata (HPM) system. Launches the HPM GUI application from the local Framework directory using WinPython.

## Features

- **Local Directory Execution**: Launches HPM from C:\Users\jimur\Projects\HST-Metadata\Photos\Version-2\Framework
- **WinPython Integration**: Automatically activates WinPython environment
- **Path Validation**: Verifies all required paths exist before execution
- **Error Handling**: Comprehensive error checking and user-friendly messages
- **Logging**: Detailed logs for troubleshooting
- **Configurable**: Easy JSON configuration file
- **Timeout Protection**: Prevents hanging on long-running applications
- **User Notifications**: Clear GUI messages for all scenarios

## Installation & Deployment

The Thumbdrive Launcher is fully portable and can be installed to any directory on your system.

### Automated Installation (Recommended)

1. **Run the installer:**
   ```powershell
   Right-click INSTALL.ps1 → Run with PowerShell
   ```

2. **Choose installation location:**
   - Default: `C:\Tools\ThumbdriveLauncher`
   - Or specify any custom path you prefer

3. **Installer will:**
   - Copy all necessary files to the chosen location
   - Offer to create a desktop shortcut
   - Configure everything automatically

### Manual Installation

If you prefer to install manually:

1. **Copy the entire `launcher` folder** to your desired location:
   - Example: `C:\Tools\ThumbdriveLauncher`
   - Example: `C:\Program Files\ThumbdriveLauncher`
   - Example: `D:\Utilities\ThumbdriveLauncher`

2. **Create desktop shortcut:**
   - Navigate to your installation folder
   - Run `create_shortcut.ps1` (right-click → Run with PowerShell)
   - Desktop shortcut will be created automatically

3. **Customize configuration:**
   - Edit `launcher_config.json` as needed
   - See Configuration section below

**Note**: The launcher works from any directory - no hardcoded paths!

## Quick Start

### Option 1: Run as Python Script (For Testing)

1. Make sure Python is installed (Python 3.7 or later)
2. Run the script:
   ```
   python launcher.py
   ```

### Option 2: Create Desktop Executable (Recommended)

1. **Build the executable:**
   - Double-click `build_launcher.bat`
   - Wait for the build to complete
   - The executable will be created in the `dist` folder

2. **Deploy the launcher:**
   - Copy `dist\HPMLauncher.exe` to your desired location (e.g., `C:\Tools\`)
   - Copy `launcher_config.json` to the same directory as the .exe
   - Edit `launcher_config.json` if needed (see Configuration section)

3. **Create desktop shortcut:**
   - Right-click `HPMLauncher.exe`
   - Select "Create shortcut"
   - Drag the shortcut to your Desktop
   - (Optional) Right-click shortcut → Properties → Change Icon

## Configuration

Edit `launcher_config.json` to customize the launcher:

```json
{
    "base_directory": "%USERPROFILE%\\Projects\\HST-Metadata\\Photos\\Version-2\\Framework",
    "winpython_activate": "%USERPROFILE%\\winpython\\WPy64-31201b5\\scripts\\activate.bat",
    "gui_script": "gui\\hstl_gui.py",
    "script_timeout": 300,
    "enable_logging": true,
    "show_success_message": false
}
```

### Configuration Options Explained

- **base_directory**: Path to the Framework directory containing the HPM system (supports environment variables)
- **winpython_activate**: Path to the WinPython activate.bat script (supports environment variables)
- **gui_script**: Relative path to the GUI script (from base_directory)
- **script_timeout**: Maximum time the application can take to launch (in seconds)
- **enable_logging**: Set to `false` to disable logging
- **show_success_message**: Set to `true` to show a success popup when application launches

### Environment Variables

The configuration supports Windows environment variables for easy multi-user deployment:

- **%USERPROFILE%**: Expands to `C:\Users\<username>`
- **%HOMEDRIVE%**: Expands to `C:`
- **%HOMEPATH%**: Expands to `\Users\<username>`
- Any other Windows environment variable

**Example for different users:**
- User "jimur": `%USERPROFILE%\winpython` → `C:\Users\jimur\winpython`
- User "alice": `%USERPROFILE%\winpython` → `C:\Users\alice\winpython`
- User "bob": `%USERPROFILE%\winpython` → `C:\Users\bob\winpython`

This allows the same configuration file to work for multiple users without modification.

## Error Scenarios Handled

### 1. Missing Required Paths
- **What happens**: Shows dialog listing missing paths (base directory, WinPython, or GUI script)
- **User action**: Check configuration file and ensure all paths are correct
- **Logged**: Yes, with specific missing paths

### 2. Application Launch Fails
- **What happens**: Shows error message with launch failure details
- **User action**: Check the log file for full details
- **Logged**: Yes, including error output

### 3. Application Timeout
- **What happens**: Shows timeout error
- **User action**: Increase `script_timeout` in config or investigate application
- **Logged**: Yes

## Logging

Logs are automatically created at:
```
C:\Users\<YourUsername>\hpm_launcher.log
```

The log includes:
- Timestamp for each operation
- Path validation results
- Application launch details
- Any errors encountered

**Example log output:**
```
2026-01-03 10:30:15 - INFO - HPM Launcher started
2026-01-03 10:30:15 - INFO - Configuration loaded from launcher_config.json
2026-01-03 10:30:15 - INFO - Base directory found: C:\Users\jimur\Projects\HST-Metadata\Photos\Version-2\Framework
2026-01-03 10:30:15 - INFO - Launching HPM application from C:\Users\jimur\Projects\HST-Metadata\Photos\Version-2\Framework
2026-01-03 10:30:18 - INFO - HPM application launched successfully
```

## Troubleshooting

### Problem: "Missing required paths"
- **Solution**: Check configuration file and ensure all paths exist
- **Solution**: Verify WinPython is installed at the configured location
- **Solution**: Ensure HPM Framework directory exists

### Problem: "Application launch failed"
- **Solution**: Check the log file for detailed error messages
- **Solution**: Verify WinPython environment is properly configured
- **Solution**: Try running the GUI script manually to debug

### Problem: "Application times out"
- **Solution**: Increase `script_timeout` value in config
- **Solution**: Investigate why application takes so long to launch

### Problem: Build fails with PyInstaller
- **Solution**: Ensure Python is installed and in PATH
- **Solution**: Run `pip install pyinstaller` manually
- **Solution**: Check for antivirus interference

## Advanced Usage

### Custom Icon for Executable

1. Get a `.ico` file for your icon
2. Edit `build_launcher.bat` and modify the PyInstaller line:
   ```batch
   pyinstaller --onefile --windowed --icon=myicon.ico --name "HPMLauncher" launcher.py
   ```

### Running Without GUI (Silent Mode)

For advanced users, you can modify the script to run without showing any dialogs. Contact your developer for this customization.

## File Structure

```
launcher/
├── launcher.py                 # Main Python script
├── launcher_config.json         # Configuration file
├── build_launcher.bat          # Build script for creating .exe
├── create_shortcut.ps1         # PowerShell script to create desktop shortcut
├── LAUNCHER_README.md          # This file
└── dist/                       # Created after build
    └── HPMLauncher.exe         # Executable launcher
```

## Requirements

- **Python**: 3.7 or later (for building/running)
- **Operating System**: Windows (PowerShell required)
- **Dependencies**:
  - PyInstaller (for building .exe)
  - tkinter (included with Python)

## Support

For issues or questions:
1. Check the log file at `C:\Users\<YourUsername>\thumbdrive_launcher.log`
2. Review this README's Troubleshooting section
3. Verify your `launcher_config.json` is valid JSON

## License

This project is provided as-is for use in your organization.
