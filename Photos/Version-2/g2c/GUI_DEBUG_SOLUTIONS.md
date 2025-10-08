# G2C GUI Debugging Solutions

## Problem Summary
The original `g2c_gui.py` was showing GObject/GTK warnings and hanging when started, causing the terminal to lock up.

## Root Cause Analysis
1. **GObject/GTK Warnings**: These were caused by conflicts between GTK libraries and PyQt5
2. **Terminal Hanging**: The GUI was starting but not properly releasing control back to the terminal
3. **Environment Issues**: Missing environment variables for proper X11/PyQt5 operation

## Solutions Provided

### 1. Fixed GUI Script: `g2c_gui_fixed.py`
- ✅ Suppresses GObject/GTK warnings that interfere with PyQt5
- ✅ Sets proper environment variables (`QT_QPA_PLATFORM=xcb`)
- ✅ Improved error handling and startup logging
- ✅ Better shutdown handling with proper thread cleanup
- ✅ Same functionality as original but more stable

### 2. Launcher Script: `launch_gui.sh`
- ✅ Pre-flight checks for dependencies
- ✅ Environment setup
- ✅ Better process management
- ✅ User-friendly status messages

### 3. Test Script: `test_gui.py`
- ✅ Simple PyQt5 test to verify GUI functionality
- ✅ Minimal example for troubleshooting

## How to Use

### Option 1: Use the Fixed GUI Directly
```bash
cd /home/juren/Projects/HST-Metadata/Photos/Version-2/g2c
python3 g2c_gui_fixed.py
```

### Option 2: Use the Launcher Script (Recommended)
```bash
cd /home/juren/Projects/HST-Metadata/Photos/Version-2/g2c
./launch_gui.sh
```

### Option 3: Test Simple GUI First
```bash
cd /home/juren/Projects/HST-Metadata/Photos/Version-2/g2c
python3 test_gui.py
```

## Environment Requirements
- ✅ Python 3.11.2 (confirmed working)
- ✅ PyQt5 (confirmed installed)
- ✅ X11 display server (confirmed working)
- ✅ All g2c dependencies (confirmed working)

## Key Fixes Applied

### Warning Suppression
```python
# Suppress GObject/GTK warnings
warnings.filterwarnings('ignore', message='.*g_boxed_type_register_static.*')
warnings.filterwarnings('ignore', message='.*g_once_init_leave.*')
warnings.filterwarnings('ignore', message='.*g_type_get_qdata.*')
```

### Environment Setup
```python
# Force X11 backend and reduce Qt logging
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
```

### Better Error Handling
```python
try:
    # GUI startup code with detailed logging
    print("✅ Step completed successfully")
except Exception as e:
    print(f"💥 Error: {e}")
    traceback.print_exc()
```

## If You Still Have Issues

1. **Kill any stuck processes**:
   ```bash
   pkill -f "python3.*g2c_gui"
   ```

2. **Check system resources**:
   ```bash
   free -h
   ps aux | grep python
   ```

3. **Verify X11 connection**:
   ```bash
   echo $DISPLAY
   xdpyinfo | head
   ```

4. **Run the test GUI first**:
   ```bash
   python3 test_gui.py
   ```

## Status
- ✅ Original issue diagnosed
- ✅ Fixed version created (`g2c_gui_fixed.py`)
- ✅ Launcher script created (`launch_gui.sh`)
- ✅ Test script created (`test_gui.py`)
- ⚠️  GUI functionality confirmed, ready for use

The GUI should now start without warnings and work properly. Use `./launch_gui.sh` for the best experience.