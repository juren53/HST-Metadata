# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable with icon and manifest
pyinstaller --onefile --windowed --icon=ICON_g2c.ico --manifest=g2c_gui.exe.manifest g2c_gui.py

Write-Host "Executable created in the dist folder!"
