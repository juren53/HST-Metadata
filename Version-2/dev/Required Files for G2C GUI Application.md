# Required Files for G2C GUI Application

This guide provides a complete list of files and installation steps needed to run the G2C GUI application on a new Windows 11 machine.

## 📋 **Required Files for G2C GUI Application**

### **🔧 Core Application Files:**
```
g2c_gui.py                    # Main GUI application
g2c.py                        # Core Google Sheets processing logic
map.py                        # Data mapping functionality
sheets_type_detector.py       # Excel/Sheet detection module
```

### **🔐 Authentication & Configuration Files:**
```
client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json   # Google API credentials
token_drive_sheets.pickle     # Enhanced authentication token (if available)
token_sheets.pickle          # Basic authentication token (if available)
```

### **📦 Python Dependencies:**
```
requirements.txt             # Package dependencies list
```

### **📚 Optional Support Files:**
```
sheets_converter.py          # Excel to Google Sheets conversion (if needed)
__init__.py                  # Python package marker
```

## 🚀 **Installation Steps for New Machine:**

### **1. Install Python Dependencies:**
```powershell
pip install -r requirements.txt
```

**Or manually install these packages:**
```powershell
pip install PyQt5 google-api-python-client google-auth-httplib2 google-auth-oauthlib google-auth pandas pyperclip typing-extensions
```

### **2. Required Python Packages:**
- **PyQt5** - GUI framework
- **google-api-python-client** - Google Sheets/Drive API
- **google-auth-httplib2** - Google authentication
- **google-auth-oauthlib** - OAuth flow
- **google-auth** - Core authentication
- **pandas** - Data processing
- **pyperclip** - Clipboard functionality (optional)
- **typing-extensions** - Type hints

### **3. Authentication Setup:**
- Copy the `client_secret_*.json` file (Google API credentials)
- Copy the `token_*.pickle` files (if you want to transfer existing authentication)
- **OR** let the user authenticate fresh on the new machine

### **4. Run the Application:**
```powershell
python g2c_gui.py
```

## ⚠️ **Important Notes:**

### **Authentication Tokens:**
The `.pickle` files contain user-specific authentication. You can either:
- Copy them to transfer authentication
- Let the app create new ones (user will need to authenticate)

### **Google API Credentials:**
The `client_secret_*.json` file is essential and must be copied

### **Optional Dependencies:**
If `pyperclip` is not available, clipboard auto-detection will be disabled but the app will still work

### **File Structure:**
Keep all files in the same directory to maintain import relationships

## 🎯 **Application Features:**

- **Full Screen Mode**: Opens maximized for optimal workspace
- **Clipboard Auto-Detection**: Automatically detects Google Sheets URLs from clipboard
- **Excel File Detection**: Identifies and warns about Excel files that need conversion
- **Version Display**: Shows "Ver 0.1" and live timestamp in status bar
- **Progress Tracking**: Real-time status updates during data processing
- **Data Preview**: Built-in table view of processed data
- **CSV Export**: One-click export to CSV with IPTC field mapping
- **Error Handling**: User-friendly error messages and guidance

## 📁 **Directory Structure:**
```
project-folder/
├── g2c_gui.py
├── g2c.py
├── map.py
├── sheets_type_detector.py
├── sheets_converter.py (optional)
├── __init__.py
├── requirements.txt
├── client_secret_*.json
├── token_drive_sheets.pickle (generated/copied)
└── token_sheets.pickle (generated/copied)
```

## 🔧 **Troubleshooting:**

### **Common Issues:**

1. **"Module not found" errors**: Install missing packages with pip
2. **Authentication failures**: Delete `.pickle` files and re-authenticate
3. **Google API errors**: Verify `client_secret_*.json` file is present and valid
4. **GUI not opening**: Ensure PyQt5 is properly installed

### **First-Time Setup:**
1. Copy all required files to the target machine
2. Install Python dependencies
3. Run the application - it will prompt for Google authentication
4. Grant necessary permissions for Google Sheets and Drive access

This setup will provide a fully functional G2C GUI application on the new Windows 11 machine!
