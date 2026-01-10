#!/bin/bash
# ==============================================================
# Linux equivalent of LAUNCH_HPM_PORTABLE.bat
# Use this for testing application logic on Linux
# Deploy the .bat version to Windows USB drives
# ==============================================================

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine the mount point (simulate USB drive)
# This finds the mount point of the filesystem containing this script
USB_MOUNT="$(df "$SCRIPT_DIR" | tail -1 | awk '{print $6}')"

echo
echo "========================================"
echo "Portable Launcher (Linux Test Version)"
echo "========================================"
echo "Script location: $SCRIPT_DIR"
echo "Mount point: $USB_MOUNT"
echo

# Define paths relative to mount point
# Note: On Linux, adjust these paths to match where you're testing
# On Windows USB, they would be: WinPython\..., Projects\...
FRAMEWORK_DIR="$USB_MOUNT/Projects/HST-Metadata/Photos/Version-2/Framework"
GUI_SCRIPT="gui/hstl_gui.py"

# For Linux testing, you might use system Python instead of WinPython
# Detect if we have python3 or python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python not found in PATH"
    exit 1
fi

echo "Using Python: $PYTHON_CMD ($($PYTHON_CMD --version))"
echo

echo "Checking required paths..."
echo

# Validate that required paths exist
if [ ! -d "$FRAMEWORK_DIR" ]; then
    echo "[ERROR] Framework directory not found!"
    echo "Expected: $FRAMEWORK_DIR"
    echo
    echo "Note: Adjust the FRAMEWORK_DIR path in this script"
    echo "to match your Linux filesystem layout"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "[OK] Framework found: $FRAMEWORK_DIR"

if [ ! -f "$FRAMEWORK_DIR/$GUI_SCRIPT" ]; then
    echo "[ERROR] GUI script not found!"
    echo "Expected: $FRAMEWORK_DIR/$GUI_SCRIPT"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi
echo "[OK] GUI script found: $GUI_SCRIPT"

# All paths validated - proceed with launch
echo
echo "========================================"
echo "Launching Application"
echo "========================================"
echo

echo "[1/2] Changing to Framework directory..."
cd "$FRAMEWORK_DIR" || {
    echo "[ERROR] Failed to change directory"
    read -p "Press Enter to exit..."
    exit 1
}

echo "[2/2] Launching HSTL Photo Metadata System..."
echo

# Run the Python application
$PYTHON_CMD "$GUI_SCRIPT"

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo
    echo "========================================"
    echo "[ERROR] Application exited with code $EXIT_CODE"
    echo "========================================"
    read -p "Press Enter to exit..."
    exit $EXIT_CODE
fi

# Success
echo
echo "Application exited successfully"
exit 0
