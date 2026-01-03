# HSTL Photo Framework - Installation Guide

## Overview

The HSTL Photo Metadata Framework requires several dependencies to function properly. This guide covers both Python package installation and external tool requirements.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Internet connection for package downloads

## Quick Installation

```bash
# Clone or download the framework
cd HSTL-Photo-Framework

# Install all Python dependencies
pip install -r requirements.txt
```

## Detailed Installation Steps

### 1. Python Dependencies

All Python dependencies are specified in `requirements.txt`. The file is organized into categories:

#### Core Framework Dependencies
- **PyYAML** >= 6.0 - YAML configuration file parsing
- **pandas** >= 1.5.0 - Data manipulation and CSV processing
- **pydantic** >= 1.10.0 - Configuration validation and data models
- **ftfy** >= 6.0.0 - Text encoding fixes and Unicode normalization
- **tqdm** >= 4.64.0 - Progress bars for CLI operations
- **colorama** >= 0.4.4 - Cross-platform colored terminal output (optional)
- **structlog** >= 22.0.0 - Enhanced structured logging

#### Image Processing Dependencies
- **Pillow** >= 9.0.0 - Image processing and format conversions
- **PyExifTool** >= 0.5.0 - Python wrapper for ExifTool command-line utility

#### GUI Framework Dependencies
- **PyQt6** >= 6.0.0 - Main GUI framework for the application
- **wxPython** >= 4.1.0 - Optional GUI utility (for csv_record_viewer.py)

#### Google Services Integration
- **google-auth** >= 2.0.0 - Google authentication library
- **google-auth-oauthlib** >= 0.5.0 - OAuth 2.0 flow for Google services
- **google-auth-httplib2** >= 0.1.0 - HTTP transport for Google authentication
- **google-api-python-client** >= 2.0.0 - Google API client library
- **gspread** >= 5.0.0 - Google Sheets API wrapper

#### Development and Testing Dependencies
- **pytest** >= 7.0.0 - Unit testing framework
- **pytest-cov** >= 4.0.0 - Test coverage reporting

### 2. External Tool Requirements

#### ExifTool (Required - Both Components Needed)

**ExifTool is essential for metadata operations** and requires TWO components:

1. **ExifTool Command-Line Tool** - Must be installed separately
2. **PyExifTool Python Wrapper** - Installed via requirements.txt

**Windows:**
1. Download from: https://exiftool.org/
2. Extract to a permanent location (e.g., `C:\ExifTool`)
3. Add the directory to your system PATH
4. Verify installation by running: `exiftool -ver`

**macOS:**
```bash
# Using Homebrew
brew install exiftool

# Or download directly from https://exiftool.org/
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install exiftool

# Or download directly from https://exiftool.org/
```

### 3. Platform-Specific Dependencies

#### Windows-Specific
- **pywin32** - Auto-installed when needed for desktop shortcuts
  - The framework will automatically install this if you try to create desktop shortcuts
  - Manual installation: `pip install pywin32`

### 4. Google Services Setup

To use Google Sheets integration:

1. **Create Google Cloud Project:**
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google Sheets API and Google Drive API

2. **Create Credentials:**
   - Go to "Credentials" -> "Create Credentials" -> "OAuth client ID"
   - Select "Desktop application"
   - Download the JSON file and rename it to `client_secret.json`
   - Place it in your project directory or specify the path in configuration

3. **First-Time Authentication:**
   - Run the framework once with Google features
   - A browser window will open for Google authentication
   - Grant permissions to access Sheets and Drive
   - Authentication tokens will be saved automatically

## Installation Verification

After installation, verify everything works:

```bash
# Test all dependencies
python -c "
import yaml, pandas, pydantic, ftfy, tqdm, colorama, structlog
from PIL import Image
from PyQt6.QtWidgets import QApplication
import wx, google.auth, google_auth_oauthlib, googleapiclient, gspread
import exiftool  # PyExifTool wrapper
import pytest, pytest_cov
print('✅ All dependencies imported successfully!')
"

# Test external command-line tool
exiftool -ver
```

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### 2. ExifTool not found
```bash
# Solution: Ensure ExifTool is in PATH
where exiftool  # Windows
which exiftool  # macOS/Linux
```

#### 3. Google Authentication Issues
```bash
# Solution: Clear cached credentials
# Delete token files in your project directory
# Re-run authentication process
```

#### 4. PyQt6 Installation Issues
```bash
# On some systems, PyQt6 may need additional system libraries
# Windows: Usually works out-of-the-box
# macOS: `brew install qt` may be needed
# Linux: `sudo apt-get install python3-pyqt6` (Ubuntu/Debian)
```

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Create a virtual environment (recommended)
python -m venv hstl_env
source hstl_env/bin/activate  # macOS/Linux
# or
hstl_env\Scripts\activate     # Windows

# Then install requirements
pip install -r requirements.txt
```

## Optional Components

### GUI Applications

The framework includes optional GUI components:
- Main GUI application (`python gui/hstl_gui.py`)
- CSV Record Viewer (`python csv_record_viewer.py`) - requires wxPython

### Development Tools

For development and testing:
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## Upgrade Instructions

To upgrade dependencies:

```bash
# Update all packages to latest compatible versions
pip install --upgrade -r requirements.txt

# Check for any conflicts
pip check
```

## Support

If you encounter issues not covered in this guide:

1. Check the main documentation files:
   - `README.md` - General information
   - `QUICKSTART.md` - Quick start guide
   - `USER_GUIDE.md` - Detailed usage guide

2. Verify your Python version: `python --version`
3. Check for system-specific requirements
4. Ensure all external tools are properly installed

## File Structure

```
HSTL-Photo-Framework/
├── requirements.txt              # Python dependencies
├── client_secret.json           # Google OAuth credentials (create this)
├── hstl_framework.py            # Main CLI entry point
├── gui/                         # GUI application files
├── Google_form/                 # Google Sheets integration
├── csv_record_viewer.py         # Optional CSV viewer utility
└── docs/                        # Documentation files
```

This completes the installation setup for the HSTL Photo Metadata Framework.