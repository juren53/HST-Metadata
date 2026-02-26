## HPM (HSTL Photo Metadata) System - Installation Checklist

This checklist guides you through installing the HPM system (HSTL Photo Metadata System aka HSTL Photo Framework) from scratch. Follow each section in order and check off items as they are completed.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Install WinPython](#1-install-winpython)
  - [Install WinPython using winget (Recommended)](#install-winpython-using-winget-recommended)
  - [Alternative: Manual Download and Installation](#alternative-manual-download-and-installation)
  - [Verify Installation Structure](#verify-installation-structure)
  - [Verify WinPython Installation](#verify-winpython-installation)
- [2. Download HPM from GitHub](#2-download-hpm-from-github)
  - [Clone the Repository](#clone-the-repository)
  - [Verify Repository Structure](#verify-repository-structure)
- [3. Install Dependencies](#3-install-dependencies)
  - [Activate WinPython Environment](#activate-winpython-environment)
  - [Install Python Packages](#install-python-packages)
  - [Verify Python Package Installation](#verify-python-package-installation)
- [4. Install Helper Tools/Apps](#4-install-helper-toolsapps)
  - [Install ExifTool (Required)](#install-exiftool-required)
- [5. Install Credentials](#5-install-credentials)
  - [Create Google Cloud Project](#create-google-cloud-project)
  - [Enable Required APIs](#enable-required-apis)
  - [Create OAuth 2.0 Credentials](#create-oauth-20-credentials)
  - [Download and Install Client Secret](#download-and-install-client-secret)
  - [First-Time Authentication](#first-time-authentication)
- [6. Configure HPM Launcher (Optional)](#6-configure-hpm-launcher-optional)
  - [Verify Launcher Configuration](#verify-launcher-configuration)
  - [Test the Launcher](#test-the-launcher)
  - [Create Desktop Shortcut (Optional)](#create-desktop-shortcut-optional)
- [7. Verify Complete Installation](#7-verify-complete-installation)
  - [Test CLI Framework](#test-cli-framework)
  - [Test GUI Application](#test-gui-application)
  - [Alternate manual start of HPM System](#alternate-manual-start-of-hpm-system-from-users-home-directory)
  - [Clean Up Test Batches (Optional)](#clean-up-test-batches-optional)
- [8. Additional Helper Tools (Optional)](#8-additional-helper-tools-optional)
  - [CSV Record Viewer](#csv-record-viewer)
- [Installation Complete!](#installation-complete)
  - [Next Steps](#next-steps)
  - [Quick Reference Card](#quick-reference-card)
  - [Troubleshooting](#troubleshooting)
- [Installation Summary](#installation-summary)

---

## Prerequisites

- [ ] Windows 10 or later (64-bit recommended)
- [ ] Internet connection for downloads
- [ ] Minimum 2 GB free disk space

---

## 1. Install WinPython

WinPython is a portable Python distribution that includes all necessary packages to make a 'locally installed' version of Python.

### Install WinPython using winget (Recommended)

The easiest way to install WinPython is using Windows Package Manager (winget).

- [ ] Open **Command Prompt** or **PowerShell**
- [ ] Navigate to your user root directory:
  ```powershell
  cd %USERPROFILE%
  ```
- [ ] Run the winget installation command:
  ```powershell
  winget install winpython
  ```
- [ ] Follow any on-screen prompts to complete the installation
- [ ] Note the installation location (typically: `%USERPROFILE%\winpython\WPy64-31201b5\` or similar)

**Note:** If winget is not available, you can install it from the Microsoft Store (search for "App Installer") or use the manual installation method below.

### Alternative: Manual Download and Installation

If you prefer manual installation or winget is not available:

- [ ] Visit [WinPython Downloads](https://winpython.github.io/)
- [ ] Download **WinPython 3.12.x.x** (or later) - 64-bit version recommended
  - Example: `Winpython64-3.12.0.1b5.exe`
- [ ] Run the WinPython installer executable
- [ ] Extract to your chosen location: `%USERPROFILE%\winpython\WPy64-31201b5\`
  - Note: The exact folder name depends on your WinPython version

### Verify Installation Structure

- [ ] Verify the WinPython structure exists:
  ```
  %USERPROFILE%\winpython\
  └── WPy64-31201b5\
      ├── python-3.12.x.amd64\
      ├── scripts\
      │   └── activate.bat  ← Important!
      └── WinPython Command Prompt.exe
  ```

### Verify WinPython Installation

- [ ] Open **WinPython Command Prompt** from the installation folder
- [ ] Run: `python --version`
  - Expected output: `Python 3.12.x` (or your installed version)
- [ ] Run: `pip --version`
  - Expected output: pip version info

**Note the activation script path:** `%USERPROFILE%\winpython\WPy64-31201b5\scripts\activate.bat`
You'll need this path later.

---

## 2. Download HPM from GitHub

### Clone the Repository

- [ ] Create a directory `C:\Users\<Username>\Projects\` 
- [ ] Open **WinPython Command Prompt** or regular Command Prompt
- [ ] Navigate to your projects directory:
  ```powershell
  cd %USERPROFILE%\Projects
  ```
- [ ] Clone the HPM repository:
  ```powershell
  git clone https://github.com/juren53/HST-Metadata.git
  ```
- [ ] Navigate to the Framework directory:
  ```powershell
  cd HST-Metadata\Photos\Version-2\Framework
  ```

### Verify Repository Structure

- [ ] Confirm the following key files and directories exist:
  ```
  HST-Metadata\Photos\Version-2\Framework\
  ├── hstl_framework.py          # Main CLI entry point
  ├── requirements.txt           # Python dependencies
  ├── gui\                       # GUI application files
  │   └── hstl_gui.py           # Main GUI entry point
  ├── launcher\                  # HPM Launcher
  │   ├── launcher.py
  │   └── launcher_config.json
  ├── Google_form\               # Google Sheets integration
  ├── docs\                      # Documentation
  └── INSTALLATION.md            # Detailed installation guide
  ```

**Framework Path:** `%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework`

---

## 3. Install Dependencies

### Activate WinPython Environment

- [ ] Open **WinPython Command Prompt**, or run:
  ```powershell
  call "%USERPROFILE%\winpython\WPy64-31201b5\scripts\activate.bat"
  ```
- [ ] Verify activation - prompt should show: `(base) C:\...>`

### Install Python Packages

- [ ] Navigate to the Framework directory:
  ```powershell
  cd /d "%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework"
  ```
- [ ] Install all dependencies from requirements.txt:
  ```powershell
  pip install -r requirements.txt
  ```
  - This installs: PyYAML, pandas, pydantic, Pillow, PyQt6, Google API libraries, and more
  - Installation may take 5-10 minutes

### Verify Python Package Installation

- [ ] Test core imports:
  ```powershell
  python -c "import yaml, pandas, PIL; from PyQt6.QtWidgets import QApplication; print('Core packages OK')"
  ```
  - Expected output: `Core packages OK`

- [ ] Test Google libraries:
  ```powershell
  python -c "import google.auth, gspread; print('Google packages OK')"
  ```
  - Expected output: `Google packages OK`

---

## 4. Install Helper Tools/Apps

### Install ExifTool (Required)

ExifTool is essential for reading and writing metadata in image files.

#### Option 1: Automated Installation (Recommended)

The framework includes an automated setup script:

- [ ] Navigate to the Framework directory in PowerShell or Command Prompt
- [ ] Run **ONE** of the following:
  
  **PowerShell (Recommended):**
  ```powershell
  .\setup_exiftool.ps1
  ```
  
  **Batch File:**
  ```cmd
  setup_exiftool.bat
  ```

- [ ] Follow the on-screen prompts
- [ ] **Restart** your PowerShell/Command Prompt window after installation

**Verify ExifTool Installation:**

- [ ] Open a **new** Command Prompt or PowerShell (to reload PATH)
- [ ] Run: `exiftool -ver`
  - Expected output: Version number (e.g., `13.27`)

#### Option 2: Manual Installation

If the automated script doesn't work, you can install manually:

**Download and Install:**

- [ ] Visit [ExifTool Official Site](https://exiftool.org/)
- [ ] Download **Windows Executable** (e.g., `exiftool-12.70.zip`)
- [ ] Extract `exiftool(-k).exe` to a permanent location:
  - Recommended: `C:\Program Files\ExifTool\`
- [ ] Rename `exiftool(-k).exe` to `exiftool.exe`

**Add ExifTool to System PATH:**

- [ ] Open Windows System Properties:
  - Press `Win + Pause/Break` or right-click **This PC** → **Properties**
- [ ] Click **Advanced system settings**
- [ ] Click **Environment Variables**
- [ ] Under **System variables**, select **Path**, click **Edit**
- [ ] Click **New**, add: `C:\Program Files\ExifTool\`
- [ ] Click **OK** on all dialogs

**Verify ExifTool Installation:**

- [ ] Open a **new** Command Prompt (to reload PATH)
- [ ] Run: `exiftool -ver`
  - Expected output: Version number (e.g., `12.70`)

---

## 5. Install Credentials

The HPM system uses Google Sheets API for collaborative metadata management.

### Create Google Cloud Project

- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Sign in with your Google account
- [ ] Click **Create Project**
  - Project name: `HSTL Photo Metadata` (or your preferred name)
- [ ] Click **Create**

### Enable Required APIs

- [ ] Navigate to **APIs & Services** → **Library**
- [ ] Search for and enable:
  - [ ] **Google Sheets API**
  - [ ] **Google Drive API**

### Create OAuth 2.0 Credentials

- [ ] Go to **APIs & Services** → **Credentials**
- [ ] Click **+ CREATE CREDENTIALS** → **OAuth client ID**
- [ ] If prompted, configure the OAuth consent screen:
  - User Type: **External**
  - App name: `HSTL Photo Metadata`
  - User support email: Your email
  - Developer contact: Your email
  - Click **Save and Continue** through all steps
- [ ] Return to **Credentials** → **+ CREATE CREDENTIALS** → **OAuth client ID**
- [ ] Application type: **Desktop app**
- [ ] Name: `HPM Desktop Client`
- [ ] Click **Create**

### Download and Install Client Secret

- [ ] Click **Download JSON** (download icon next to your OAuth 2.0 Client ID)
- [ ] Save the file as `client_secret.json` in the Framework directory:
  ```
  %USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework\client_secret.json
  ```

**Important:** Keep this file secure - it contains sensitive OAuth credentials.

### First-Time Authentication

- [ ] The first time you run a Google Sheets operation, a browser window will open
- [ ] Sign in with your Google account
- [ ] Click **Allow** to grant permissions to the HPM application
- [ ] Authentication token will be saved automatically (`token.pickle`)

---

## 6. Configure HPM Launcher (Optional)

The HPM Launcher provides one-click startup for the HPM GUI application.

### Verify Launcher Configuration

- [ ] Open `launcher\launcher_config.json` in a text editor
- [ ] Verify the paths match your installation:
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
- [ ] Update paths if your installation locations differ

### Test the Launcher

- [ ] Activate WinPython environment (if not already active)
- [ ] Navigate to Framework directory
- [ ] Run the launcher:
  ```powershell
  python launcher\launcher.py
  ```
- [ ] Verify the HPM GUI application opens successfully
- [ ] Close the application

### Create Desktop Shortcut (Optional)

- [ ] Right-click on your Desktop → **New** → **Shortcut**
- [ ] Target location:
  ```
  "%USERPROFILE%\winpython\WPy64-31201b5\python-3.12.x.amd64\python.exe" "%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework\launcher\launcher.py"
  ```
  - Replace `python-3.12.x.amd64` with your actual Python directory name
- [ ] Name: `HPM Launcher`
- [ ] Click **Finish**
- [ ] (Optional) Right-click shortcut → **Properties** → **Change Icon** to customize

---

## 7. Verify Complete Installation

### Test CLI Framework

- [ ] Activate WinPython environment
- [ ] Navigate to Framework directory
- [ ] Run framework help:
  ```powershell
  python hstl_framework.py --help
  ```
  - Expected: Help text showing available commands

- [ ] Initialize a test batch:
  ```powershell
  python hstl_framework.py init "Installation Test Batch"
  ```
  - Expected: Success message with created directory path

- [ ] Verify test batch creation:
  ```powershell
  python hstl_framework.py batches
  ```
  - Expected: List showing "Installation Test Batch"

### Test GUI Application

- [ ] Start the HPM GUI:
  ```powershell
  python gui\hstl_gui.py
  ```
  - Expected: HPM application window opens

- [ ] Verify GUI components:
  - [ ] Menu bar displays: File, Edit, Help
  - [ ] Main window shows batch management interface
  - [ ] Status bar shows "Ready"

- [ ] Test creating a batch via GUI:
  - [ ] Click **File** → **New Batch**
  - [ ] Enter batch name: `GUI Test Batch`
  - [ ] Click **Create**
  - [ ] Verify batch appears in batch list

- [ ] Close the GUI application

### Alternate manual start of HPM System from users home directory 

-  C:\Users\laustin\winpython\WPy64-31201b5\scripts\activate.bat
-  cd .\Projects\HST-Metadata\Photos\Version-2\Framework\
-  python .\gui\hstl_gui.py



### Clean Up Test Batches (Optional)

- [ ] Remove test batches:
  ```powershell
  python hstl_framework.py batch remove installationtestbatch --confirm
  python hstl_framework.py batch remove guitestbatch --confirm
  ```

---

## 8. Additional Helper Tools (Optional)

These tools enhance the HPM workflow but are not required for core functionality.

### CSV Record Viewer

The CSV Record Viewer provides a visual interface for reviewing metadata CSV files.

**Note:** This requires wxPython, which should already be installed via `requirements.txt`.

- [ ] CSV Record Viewer - CSV_reader.exe

- [ ] TagWriter - Image Viewer Tool  - tag-writer.exe
---

## Installation Complete!

Congratulations! Your HPM system is now fully installed and ready to use.

### Next Steps

- [ ] Read the [Quick Start Guide](docs/QUICKSTART.md)
- [ ] Review the [User Guide](docs/USER_GUIDE.md)
- [ ] Explore the [Glossary](docs/GLOSSARY.md) for HPM terminology

### Quick Reference Card

**Start HPM GUI:**
```powershell
# Method 1: Using Launcher
python launcher\launcher.py

# Method 2: Direct startup
call "%USERPROFILE%\winpython\WPy64-31201b5\scripts\activate.bat"
cd /d "%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework"
python gui\hstl_gui.py
```

**Start HPM CLI:**
```powershell
call "%USERPROFILE%\winpython\WPy64-31201b5\scripts\activate.bat"
cd /d "%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework"
python hstl_framework.py --help
```

### Troubleshooting

If you encounter issues, refer to:
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide with troubleshooting
- [QUICKSTART.md](docs/QUICKSTART.md) - Quick start guide
- Check logs in: `launcher\launcher.log` (for launcher issues)

---

## Installation Summary

| Component | Status | Location |
|-----------|--------|----------|
| WinPython | ✓ | `%USERPROFILE%\winpython\WPy64-31201b5\` |
| HPM Framework | ✓ | `%USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework\` |
| Python Packages | ✓ | Installed via pip in WinPython environment |
| ExifTool | ✓ | `C:\Program Files\ExifTool\` (in system PATH) |
| Google Credentials | ✓ | `client_secret.json` in Framework directory |
| HPM Launcher | ✓ | Configured in `launcher\launcher_config.json` |

**Installation Date:** _______________
**Installed By:** _______________
**WinPython Version:** _______________
**HPM Version:** 0.1.3e

---

*For detailed documentation, see the [main README](README.md) and [docs/](docs/) directory.*
