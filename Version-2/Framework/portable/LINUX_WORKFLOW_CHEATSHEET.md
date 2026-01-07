# Linux → Windows Development Cheat Sheet

Quick reference for developing Windows scripts on Linux LMDE.

---

## Daily Workflow

### 1. Create/Edit Windows Script
```bash
# Edit the .bat file in your favorite editor
nano LAUNCH_HPM_PORTABLE.bat
# or
code LAUNCH_HPM_PORTABLE.bat
```

### 2. Validate Before Deployment
```bash
cd portable/
./validate_windows_scripts.sh
```

### 3. Fix Line Endings (CRITICAL!)
```bash
./fix_line_endings.sh
```

### 4. Test Logic with Linux Equivalent
```bash
./launch_hpm_portable.sh
```

### 5. Deploy to Windows
```bash
# Copy to USB drive
cp LAUNCH_HPM_PORTABLE.bat /media/usb/

# Or commit to git for Windows testing
git add LAUNCH_HPM_PORTABLE.bat
git commit -m "Update portable launcher"
```

---

## Quick Commands

### Check File Line Endings
```bash
file LAUNCH_HPM_PORTABLE.bat

# Good: "ASCII text, with CRLF line terminators"
# Bad:  "ASCII text" (Unix LF)
```

### Convert Line Endings Manually
```bash
# Unix → Windows (REQUIRED for .bat/.ps1)
unix2dos LAUNCH_HPM_PORTABLE.bat

# Windows → Unix (for .sh files)
dos2unix launch_hpm_portable.sh
```

### Install Required Tools
```bash
# Line ending tools
sudo apt install dos2unix

# PowerShell Core (for .ps1 validation)
sudo apt install powershell

# VirtualBox (for Windows testing)
sudo apt install virtualbox virtualbox-ext-pack
```

---

## File Types Reference

| Extension | Line Endings | Where to Run |
|-----------|--------------|--------------|
| `.bat` | CRLF (Windows) | Windows only |
| `.ps1` | CRLF (Windows) | Windows PowerShell |
| `.sh` | LF (Unix) | Linux only |
| `.py` | LF preferred | Both (Python handles it) |

---

## Common Issues & Fixes

### Issue: "Bad command or file name" in Windows
**Cause:** Wrong line endings (LF instead of CRLF)
**Fix:**
```bash
unix2dos LAUNCH_HPM_PORTABLE.bat
```

### Issue: Script works on Linux but not Windows
**Cause:** Used Linux-specific commands (like `ls`, `grep`)
**Fix:** Use Windows equivalents:
- `ls` → `dir`
- `grep` → `findstr`
- `cat` → `type`
- Path separator: `/` → `\`

### Issue: Can't test .bat on Linux
**Not a bug:** It's expected. Use strategies:
1. Test with `.sh` equivalent
2. Use Windows VM
3. Test on actual Windows machine

---

## Git Workflow

### Keep Both Versions in Git
```bash
# Track both Linux test version and Windows deployment version
git add launch_hpm_portable.sh    # Linux testing
git add LAUNCH_HPM_PORTABLE.bat   # Windows deployment
git commit -m "Add portable launcher for both platforms"
```

### Configure Git to NOT Auto-Convert Line Endings
Create `.gitattributes`:
```
# Don't auto-convert Windows scripts
*.bat text eol=crlf
*.ps1 text eol=crlf

# Don't auto-convert Linux scripts
*.sh text eol=lf

# Python can handle both, prefer LF
*.py text eol=lf
```

---

## Testing Strategies

### Quick Test (Linux)
```bash
# Test application logic only
./launch_hpm_portable.sh
```

### Thorough Test (Windows VM)
```bash
# Start VirtualBox Windows VM
VBoxManage startvm "Windows10Dev"

# Share folder with VM (one-time setup)
VBoxManage sharedfolder add "Windows10Dev" \
  --name "hst-project" \
  --hostpath "/home/juren/Projects/HST-Metadata" \
  --automount

# In Windows VM: Access \\VBOXSVR\hst-project
# Test your .bat files there
```

### Full Test (Real USB on Windows)
1. Copy files to USB
2. Test on Windows machine
3. Change USB drive letter in Disk Management
4. Test again to verify portability

---

## When to Ask Claude Code

### ✅ I CAN Help With:
- Writing .bat files (can't run them, but can write them)
- Writing .ps1 files
- Reviewing Windows scripts for errors
- Creating .sh equivalents for testing
- Documentation and test plans
- Setting up validation workflows

### ❌ I CAN'T Help With:
- Running .bat files on Linux (use Wine or VM)
- Testing Windows-specific features
- Running WinPython on Linux
- Debugging Windows-only errors

### 💡 Instead, Ask Me To:
- "Write a .bat file that..."
- "Create a shell script equivalent for testing..."
- "Review this batch file for common errors"
- "Help me set up a Windows VM on Linux"
- "Create a test plan for Windows deployment"

---

## Quick Test: Did I Forget Anything?

Before deploying to Windows USB:

- [ ] Line endings converted to CRLF? (`./fix_line_endings.sh`)
- [ ] Validation passed? (`./validate_windows_scripts.sh`)
- [ ] No hardcoded drive letters? (check for `C:\`, `D:\`)
- [ ] Uses `%~d0` for drive detection?
- [ ] Tested logic with `.sh` version on Linux?
- [ ] Committed to git with proper `.gitattributes`?
- [ ] Ready to test on Windows VM or real machine?

---

## Emergency Quick Fix

**If you're stuck and need to just make it work:**

```bash
# Fix all Windows scripts in one go:
find . -name "*.bat" -exec unix2dos {} \;
find . -name "*.ps1" -exec unix2dos {} \;

# Validate:
./validate_windows_scripts.sh

# If validation passes, copy to USB and test on Windows!
```

---

## Resources

- **Full guide:** See `CROSS_PLATFORM_STRATEGY.md`
- **Portable USB setup:** See `USB_PORTABLE_SETUP.md`
- **Quick start:** See `QUICK_START.md`

---

## Remember

**The Golden Rule of Cross-Platform Development:**

> What works on Linux may not work on Windows.
> Always test on the target platform.

But with the right workflow, you can develop on Linux and deploy to Windows efficiently!

---

**Last updated:** 2026-01-07
