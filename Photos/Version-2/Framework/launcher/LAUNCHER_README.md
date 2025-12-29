# Thumbdrive Launcher

A robust Python-based launcher for running PowerShell scripts from a thumbdrive with comprehensive error handling, logging, and user-friendly notifications.

## Features

- **Smart Drive Detection**: Automatically waits for thumbdrive to be inserted
- **File Validation**: Verifies all required files exist before execution
- **Error Handling**: Comprehensive error checking and user-friendly messages
- **Logging**: Detailed logs for troubleshooting
- **Configurable**: Easy JSON configuration file
- **Timeout Protection**: Prevents hanging on long-running scripts
- **User Notifications**: Clear GUI messages for all scenarios

## Quick Start

### Option 1: Run as Python Script (For Testing)

1. Make sure Python is installed (Python 3.7 or later)
2. Run the script:
   ```
   python thumbdrive_launcher.py
   ```

### Option 2: Create Desktop Executable (Recommended)

1. **Build the executable:**
   - Double-click `build_launcher.bat`
   - Wait for the build to complete
   - The executable will be created in the `dist` folder

2. **Deploy the launcher:**
   - Copy `dist\ThumbdriveLauncher.exe` to your desired location (e.g., `C:\Tools\`)
   - Copy `launcher_config.json` to the same directory as the .exe
   - Edit `launcher_config.json` if needed (see Configuration section)

3. **Create desktop shortcut:**
   - Right-click `ThumbdriveLauncher.exe`
   - Select "Create shortcut"
   - Drag the shortcut to your Desktop
   - (Optional) Right-click shortcut → Properties → Change Icon

## Configuration

Edit `launcher_config.json` to customize the launcher:

```json
{
    "drive_letter": "D:\\",           // Thumbdrive drive letter
    "startup_script": "startup.ps1",   // PowerShell script to run
    "required_files": [                 // Files that must exist on thumbdrive
        "startup.ps1"
    ],
    "wait_for_drive_timeout": 30,      // Seconds to wait for drive
    "script_timeout": 300,              // Seconds before script times out
    "enable_logging": true,             // Enable/disable logging
    "show_success_message": false,      // Show message on success
    "auto_retry": true                  // Auto-wait for drive if not present
}
```

### Configuration Options Explained

- **drive_letter**: The drive letter where your thumbdrive is mounted (include backslashes: `"D:\\"`)
- **startup_script**: Name of the PowerShell script to execute
- **required_files**: List of files that must exist on the thumbdrive (add additional files as needed)
- **wait_for_drive_timeout**: How long to wait for the thumbdrive (in seconds)
- **script_timeout**: Maximum time the PowerShell script can run (in seconds)
- **enable_logging**: Set to `false` to disable logging
- **show_success_message**: Set to `true` to show a success popup when script completes
- **auto_retry**: Set to `false` to fail immediately if drive isn't present

## Error Scenarios Handled

### 1. Thumbdrive Not Inserted
- **What happens**: Shows dialog asking you to insert the thumbdrive
- **Options**: Retry (waits up to configured timeout) or Cancel
- **Logged**: Yes

### 2. Missing Required Files
- **What happens**: Shows list of missing files
- **User action**: Check thumbdrive and ensure all files are present
- **Logged**: Yes, with specific missing file names

### 3. PowerShell Script Fails
- **What happens**: Shows error message with PowerShell error details
- **User action**: Check the log file for full details
- **Logged**: Yes, including stderr output

### 4. Script Timeout
- **What happens**: Shows timeout error
- **User action**: Increase `script_timeout` in config or investigate script
- **Logged**: Yes

### 5. PowerShell Not Found
- **What happens**: Shows error that PowerShell isn't installed
- **User action**: Install PowerShell (should be pre-installed on Windows)
- **Logged**: Yes

## Logging

Logs are automatically created at:
```
C:\Users\<YourUsername>\thumbdrive_launcher.log
```

The log includes:
- Timestamp for each operation
- Drive detection status
- File validation results
- PowerShell execution details
- Any errors encountered

**Example log output:**
```
2025-12-29 10:30:15 - INFO - Thumbdrive Launcher started
2025-12-29 10:30:15 - INFO - Configuration loaded from launcher_config.json
2025-12-29 10:30:15 - INFO - Drive D:\ exists: True
2025-12-29 10:30:15 - INFO - Found required file: startup.ps1
2025-12-29 10:30:15 - INFO - Executing PowerShell script: D:\startup.ps1
2025-12-29 10:30:18 - INFO - PowerShell script completed successfully
```

## Troubleshooting

### Problem: "Drive D:\ not found"
- **Solution**: Check if thumbdrive is inserted and has correct drive letter
- **Solution**: Update `drive_letter` in `launcher_config.json` if using different drive

### Problem: "Missing required files"
- **Solution**: Ensure all files listed in `required_files` exist on thumbdrive
- **Solution**: Check for typos in file names (case-sensitive)

### Problem: "Script execution failed"
- **Solution**: Check the log file for detailed error messages
- **Solution**: Try running the PowerShell script manually to debug
- **Solution**: Check PowerShell execution policy

### Problem: "Script times out"
- **Solution**: Increase `script_timeout` value in config
- **Solution**: Investigate why script takes so long

### Problem: Build fails with PyInstaller
- **Solution**: Ensure Python is installed and in PATH
- **Solution**: Run `pip install pyinstaller` manually
- **Solution**: Check for antivirus interference

## Advanced Usage

### Adding Multiple Required Files

Edit `launcher_config.json`:
```json
{
    "required_files": [
        "startup.ps1",
        "config.json",
        "data/settings.ini",
        "scripts/helper.ps1"
    ]
}
```

### Custom Icon for Executable

1. Get a `.ico` file for your icon
2. Edit `build_launcher.bat` and modify the PyInstaller line:
   ```batch
   pyinstaller --onefile --windowed --icon=myicon.ico --name "ThumbdriveLauncher" thumbdrive_launcher.py
   ```

### Running Without GUI (Silent Mode)

For advanced users, you can modify the script to run without showing any dialogs. Contact your developer for this customization.

## File Structure

```
thumbdrive_launcher/
├── thumbdrive_launcher.py      # Main Python script
├── launcher_config.json         # Configuration file
├── build_launcher.bat          # Build script for creating .exe
├── LAUNCHER_README.md          # This file
└── dist/                       # Created after build
    └── ThumbdriveLauncher.exe # Executable launcher
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
