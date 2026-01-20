# ExifTool Setup for HPM

## Overview

HPM (HSTL Photo Metadata) requires ExifTool to read and write image metadata. This directory contains automated setup scripts to install ExifTool and configure it for your system.

## Quick Setup

### For Most Users (Recommended)

1. Open PowerShell or Command Prompt
2. Navigate to the HPM Framework directory:
   ```powershell
   cd %USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework
   ```

3. Run the setup script:
   
   **PowerShell:**
   ```powershell
   .\setup_exiftool.ps1
   ```
   
   **Command Prompt:**
   ```cmd
   setup_exiftool.bat
   ```

4. **Restart your terminal** after installation completes

5. Verify installation:
   ```cmd
   exiftool -ver
   ```
   You should see the version number (e.g., `13.27`)

## What the Setup Scripts Do

1. **Check for existing installation** - If ExifTool is already installed and in your PATH, the script exits without making changes

2. **Extract ExifTool** - Extracts the bundled `exiftool-13.27_64.zip` to:
   ```
   %LOCALAPPDATA%\exiftool\
   (typically: C:\Users\<YourName>\AppData\Local\exiftool\)
   ```

3. **Update PATH** - Adds the ExifTool directory to your user PATH environment variable

4. **Verify installation** - Confirms ExifTool is working correctly

## Installation Location

ExifTool will be installed to:
```
%LOCALAPPDATA%\exiftool\exiftool.exe
```

This is a **user-specific** location that doesn't require administrator privileges.

## Troubleshooting

### "ExifTool not found" Error After Installation

**Solution:** Restart your PowerShell/Command Prompt window
- The PATH environment variable is only updated for new terminal sessions
- Close all terminal windows and open a new one

### "Execution Policy" Error (PowerShell)

If you see an error about execution policies when running the PowerShell script:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_exiftool.ps1
```

### "exiftool-13.27_64.zip not found" Error

**Solution:** Ensure you're running the script from the Framework directory
- The script looks for `exiftool-13.27_64.zip` in the same directory
- This file should already be included in the repository

### Manual Verification

To check if ExifTool is in your PATH:

**Windows Command Prompt:**
```cmd
where exiftool
```

**PowerShell:**
```powershell
Get-Command exiftool
```

Both should show the path to `exiftool.exe`

### Manual PATH Configuration

If the automated scripts fail to add ExifTool to your PATH:

1. Open **Environment Variables**:
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Go to **Advanced** tab → **Environment Variables**

2. Under **User variables**, select **Path** → **Edit**

3. Click **New** and add:
   ```
   %LOCALAPPDATA%\exiftool
   ```

4. Click **OK** on all dialogs

5. Restart your terminal

## For System Administrators

If you're deploying HPM to multiple users, you can:

1. **Include in deployment package**: The setup scripts are designed to run without user input

2. **Silent installation**: Run the batch file from a deployment script:
   ```cmd
   setup_exiftool.bat
   ```

3. **Pre-configure PATH**: Alternatively, extract ExifTool to a network location and add it to the system-wide PATH

## Alternative: Manual Installation

If you prefer not to use the automated scripts:

1. Download ExifTool from: https://exiftool.org/
2. Extract to a permanent location (e.g., `C:\Program Files\ExifTool\`)
3. Add that directory to your system PATH
4. Verify with: `exiftool -ver`

## Support

If you encounter issues:

1. Check this README's troubleshooting section
2. Verify `exiftool-13.27_64.zip` exists in the Framework directory
3. Try the manual installation method
4. Contact your HPM administrator

## Technical Details

- **ExifTool Version**: 13.27 (64-bit)
- **Installation Type**: User-specific (no admin rights required)
- **PATH Scope**: User PATH (not system-wide)
- **Installation Size**: ~12 MB

## Files Included

- `setup_exiftool.ps1` - PowerShell automated setup script
- `setup_exiftool.bat` - Batch file setup script
- `exiftool-13.27_64.zip` - ExifTool distribution package
- `EXIFTOOL_SETUP_README.md` - This file

---

**Last Updated**: January 2026
**HPM Version**: 0.1.3e
