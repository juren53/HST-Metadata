# Quick Fix: "ExifTool not in PATH" Error

## Symptoms

HPM displays an error message:
- "HPM can't run properly because exiftool is not in your path"
- "ExifTool not found"
- HPM fails to read or write image metadata

## Quick Fix (2 minutes)

### Step 1: Run the Setup Script

Open PowerShell or Command Prompt in the HPM Framework directory and run:

**PowerShell:**
```powershell
.\setup_exiftool.ps1
```

**Command Prompt:**
```cmd
setup_exiftool.bat
```

### Step 2: Restart Your Terminal

Close all PowerShell/Command Prompt windows and open a new one.

### Step 3: Verify

Run this command:
```cmd
exiftool -ver
```

You should see: `13.27` (or similar version number)

### Step 4: Run HPM Again

ExifTool is now installed and HPM should work without errors!

---

## Alternative: One-Line Fix (PowerShell)

If you're comfortable with PowerShell, you can run this single command from the Framework directory:

```powershell
.\setup_exiftool.ps1; Write-Host "`nDone! Please restart your terminal." -ForegroundColor Green
```

---

## Still Having Issues?

### Problem: "Cannot be loaded because running scripts is disabled"

**Solution:** Run PowerShell with bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_exiftool.ps1
```

### Problem: Script doesn't find the zip file

**Solution:** Make sure you're in the Framework directory:
```powershell
cd %USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework
```

### Problem: ExifTool still not found after restart

**Solution:** Check if it's installed:
```powershell
Test-Path $env:LOCALAPPDATA\exiftool\exiftool.exe
```

If it returns `True`, manually verify PATH:
```powershell
$env:Path -split ';' | Select-String exiftool
```

---

## For More Information

See the complete setup guide: `EXIFTOOL_SETUP_README.md`
