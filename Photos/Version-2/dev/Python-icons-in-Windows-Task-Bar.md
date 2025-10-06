This is a common issue with PyQt applications on Windows. The problem is that Windows doesn't automatically associate your custom icon with the application's taskbar button - it needs additional configuration beyond just setting the window icon.

Here are the solutions that typically work:

## Method 1: Set Application User Model ID (Recommended)
Add this code early in your application, before creating the main window:

```python
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import ctypes

# Set the App User Model ID for Windows taskbar grouping
if sys.platform == "win32":
    myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon('path/to/your/icon.ico'))

# Create your main window
window = YourMainWindow()
window.setWindowIcon(QIcon('path/to/your/icon.ico'))
window.show()
```

## Method 2: Force Icon Refresh
Sometimes you need to force Windows to recognize the icon change:

```python
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)

# Set application icon
icon = QIcon('path/to/your/icon.ico')
app.setWindowIcon(icon)

window = YourMainWindow()
window.setWindowIcon(icon)

# Force the taskbar to update (sometimes needed)
if sys.platform == "win32":
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('YourAppName')

window.show()
```

## Method 3: Ensure Proper Icon Format
Make sure your .ico file contains multiple sizes (16x16, 32x32, 48x48, 256x256). Windows picks different sizes for different contexts. You can create a proper .ico file using tools like GIMP or online converters.

## Method 4: Alternative with Direct Windows API
For more control, you can set the icon directly using Windows API:

```python
import sys
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QApplication

if sys.platform == "win32":
    # Get window handle
    hwnd = int(window.winId())
    
    # Load icon
    icon_path = "path/to/your/icon.ico"
    hicon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x00000010)
    
    # Set icon for both small and large
    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)  # WM_SETICON, ICON_SMALL
    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)  # WM_SETICON, ICON_LARGE
```

The first method with `SetCurrentProcessExplicitAppUserModelID` usually solves the taskbar icon issue. The key is that Windows needs to distinguish your application from the Python interpreter itself, which is why setting an explicit App User Model ID is crucial.