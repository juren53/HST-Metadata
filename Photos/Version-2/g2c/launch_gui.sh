#!/bin/bash

# G2C GUI Launcher Script
# This script helps launch the GUI with proper environment setup

echo "🚀 G2C GUI Launcher"
echo "==================="
echo

# Check current directory
echo "📁 Current directory: $(pwd)"

# Check for required files
if [ ! -f "g2c_gui_fixed.py" ]; then
    echo "❌ g2c_gui_fixed.py not found in current directory"
    exit 1
fi

if [ ! -f "g2c.py" ]; then
    echo "❌ g2c.py not found in current directory"
    echo "   Make sure the main g2c module is in the same directory"
    exit 1
fi

echo "✅ Required files found"
echo

# Set up environment
export QT_QPA_PLATFORM=xcb
export QT_LOGGING_RULES='*.debug=false;qt.qpa.*=false'

echo "🔧 Environment configured:"
echo "   QT_QPA_PLATFORM: $QT_QPA_PLATFORM" 
echo "   Display: $DISPLAY"
echo

# Check Python and PyQt5
echo "🔍 Checking dependencies..."
python3 -c "import PyQt5.QtWidgets; print('✅ PyQt5 available')" || {
    echo "❌ PyQt5 not available - install with: sudo apt install python3-pyqt5"
    exit 1
}

python3 -c "from g2c import fetch_sheet_data; print('✅ g2c module available')" || {
    echo "❌ g2c module not available or has issues"
    exit 1
}

echo

# Launch the GUI
echo "🎯 Launching G2C GUI..."
echo "   (Close the GUI window or press Ctrl+C here to exit)"
echo

# Run with proper signal handling
python3 g2c_gui_fixed.py

echo
echo "👋 GUI has been closed"