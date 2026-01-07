# Cross-Platform Windows Development Strategy

## The Challenge

You're developing Windows-specific scripts (.bat, .ps1, WinPython) on Linux LMDE, but need to deploy to Windows USB drives. Claude Code runs on your Linux system and cannot execute Windows scripts directly.

## Multi-Strategy Approach

### Strategy 1: Wine for Basic Testing (Fastest)

**What it does:** Runs Windows executables on Linux using Wine compatibility layer.

**Setup:**
```bash
# Install Wine
sudo apt update
sudo apt install wine wine64

# Test if Wine works
wine --version
```

**Limitations:**
- Only works for simple batch files
- Won't handle complex PowerShell
- WinPython may not work fully
- Good for syntax checking, not full testing

**When to use:** Quick validation that batch syntax is correct.

---

### Strategy 2: Shell Script Equivalents for Development (Recommended)

**Create Linux versions of your Windows scripts for testing the logic.**

**Example: Create `launch_hpm_portable.sh` alongside `.bat` version:**

```bash
#!/bin/bash
# Linux equivalent of LAUNCH_HPM_PORTABLE.bat
# Use for testing logic on Linux, deploy .bat to Windows

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_DRIVE="$(df "$SCRIPT_DIR" | tail -1 | awk '{print $6}')"

echo "========================================"
echo "Portable Python Launcher (Linux Test)"
echo "========================================"
echo "USB Mount: $USB_DRIVE"
echo

# Define paths relative to USB mount
PYTHON_DIR="$USB_DRIVE/WinPython/WPy64-31201b5"
FRAMEWORK_DIR="$USB_DRIVE/Projects/HST-Metadata/Photos/Version-2/Framework"
GUI_SCRIPT="gui/hstl_gui.py"

echo "Checking required paths..."

# Validate paths
if [ ! -d "$PYTHON_DIR" ]; then
    echo "[ERROR] Python directory not found: $PYTHON_DIR"
    exit 1
fi
echo "[OK] Python found: $PYTHON_DIR"

if [ ! -d "$FRAMEWORK_DIR" ]; then
    echo "[ERROR] Framework directory not found: $FRAMEWORK_DIR"
    exit 1
fi
echo "[OK] Framework found: $FRAMEWORK_DIR"

if [ ! -f "$FRAMEWORK_DIR/$GUI_SCRIPT" ]; then
    echo "[ERROR] GUI script not found: $FRAMEWORK_DIR/$GUI_SCRIPT"
    exit 1
fi
echo "[OK] GUI script found: $GUI_SCRIPT"

echo
echo "========================================"
echo "Launching Application"
echo "========================================"
echo

cd "$FRAMEWORK_DIR" || exit 1
python3 "$GUI_SCRIPT"
```

**Benefits:**
- Test your application logic on Linux
- Verify path resolution works
- Check error handling
- Develop faster without switching to Windows

**Deploy:**
- Keep both `.sh` (for Linux testing) and `.bat` (for Windows deployment) in version control
- Test logic on Linux with `.sh`
- Deploy `.bat` to Windows USB

---

### Strategy 3: Virtual Machine for Full Testing (Most Reliable)

**Setup a lightweight Windows VM for final testing.**

**Option A: VirtualBox (Free)**
```bash
# Install VirtualBox
sudo apt install virtualbox virtualbox-ext-pack

# Download Windows 10/11 Dev VM (free for testing)
# https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/
```

**Option B: QEMU/KVM (Faster, more Linux-native)**
```bash
# Install KVM
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager

# Use virt-manager GUI or virsh CLI to create Windows VM
```

**Testing Workflow:**
1. Develop scripts on Linux (using Strategy 2 for logic testing)
2. Share folder between Linux host and Windows VM
3. Test actual .bat/.ps1 files in Windows VM
4. Iterate quickly

**USB Testing in VM:**
- VirtualBox: Devices → USB → Select your USB drive
- Allows testing actual drive letter assignment behavior

---

### Strategy 4: Static Analysis and Linting (Prevention)

**Catch errors before testing on Windows.**

**For Batch Files:**
```bash
# No great linters, but you can check syntax with:
# 1. Manual review
# 2. Use shellcheck for similar logic patterns
# 3. Create a custom validator
```

**For PowerShell:**
```bash
# Install PowerShell Core on Linux
sudo apt install powershell

# Lint PowerShell scripts
pwsh -File validate_script.ps1
```

**Create a validation script:**

```bash
#!/bin/bash
# validate_windows_scripts.sh

echo "Validating Windows scripts..."

# Check batch files for common issues
for bat in **/*.bat; do
    echo "Checking $bat..."

    # Check for Linux line endings (will break on Windows)
    if file "$bat" | grep -q "CRLF"; then
        echo "  ✓ Correct line endings (CRLF)"
    else
        echo "  ✗ WARNING: Unix line endings detected (LF)"
        echo "    Fix with: unix2dos $bat"
    fi

    # Check for common issues
    if grep -q "cd /d" "$bat"; then
        echo "  ✓ Uses 'cd /d' for drive changes"
    fi
done

echo "Done."
```

---

### Strategy 5: Documentation-Driven Development (DDD)

**Since you can't always test, document thoroughly.**

**For each Windows script, create a companion test plan:**

```markdown
# LAUNCH_HPM_PORTABLE.bat - Test Plan

## Test Cases

### TC1: Drive Letter Detection
**Setup:** USB on D:
**Action:** Run LAUNCH_HPM_PORTABLE.bat
**Expected:** Detects D: correctly
**Status:** ⬜ Not tested | ✅ Pass | ❌ Fail

### TC2: Different Drive Letter
**Setup:** Change USB to E: in Disk Management
**Action:** Run LAUNCH_HPM_PORTABLE.bat
**Expected:** Detects E: correctly, launches application
**Status:** ⬜ Not tested | ✅ Pass | ❌ Fail

### TC3: Missing WinPython
**Setup:** Rename WinPython folder
**Action:** Run LAUNCH_HPM_PORTABLE.bat
**Expected:** Shows error message, doesn't crash
**Status:** ⬜ Not tested | ✅ Pass | ❌ Fail
```

**Test on Windows, track results, iterate.**

---

## Recommended Workflow

### Day-to-Day Development (On Linux)

1. **Use Strategy 2:** Develop with shell script equivalents
   - Test application logic
   - Verify path resolution
   - Check error handling

2. **Use Strategy 4:** Validate scripts automatically
   - Check line endings (MUST be CRLF for Windows)
   - Lint PowerShell with `pwsh`
   - Review batch syntax manually

3. **Version Control:** Commit both `.sh` and `.bat` versions
   - `.sh` for Linux testing
   - `.bat` for Windows deployment

### Weekly Testing (On Windows)

1. **Use Strategy 3:** Boot Windows VM
2. **Run through test plan** (Strategy 5)
3. **Test USB drive with different letters**
4. **Document results**

### Before Client Deployment

1. **Full Windows testing** with actual USB drive
2. **Test on multiple Windows machines** if possible
3. **Verify different drive letter scenarios**

---

## Quick Reference: File Validation Commands

```bash
# Check line endings (CRITICAL for Windows scripts)
file LAUNCH_HPM_PORTABLE.bat
# Should say: "ASCII text, with CRLF line terminators"

# Convert Unix (LF) to Windows (CRLF) line endings
unix2dos LAUNCH_HPM_PORTABLE.bat

# Convert Windows (CRLF) to Unix (LF) line endings
dos2unix script.sh

# Validate PowerShell syntax on Linux
pwsh -Command "Test-Path ./create_usb_shortcut.ps1"
```

---

## Tool Recommendations

### Essential Tools for Cross-Platform Windows Development

```bash
# Line ending converters
sudo apt install dos2unix

# PowerShell Core (run PowerShell on Linux)
sudo apt install powershell

# VirtualBox (for Windows VM testing)
sudo apt install virtualbox

# File analysis
sudo apt install file
```

---

## When to Ask Claude Code for Help

**✅ Good requests for Claude Code on Linux:**
- "Write a .bat file for Windows" (I can write it, just can't run it)
- "Create a shell script equivalent for testing"
- "Review this batch file for errors"
- "Help me set up a Windows VM"
- "Create a test plan for Windows scripts"

**❌ Requests that won't work:**
- "Run this .bat file" (unless you're in a Windows environment)
- "Test this PowerShell script" (I can test syntax if pwsh is installed, but not Windows-specific features)
- "Launch WinPython" (Windows-only application)

---

## Your Specific Situation

For your WinPython USB project:

1. **Develop on Linux:**
   - Write the .bat files (I can help!)
   - Create .sh equivalents for logic testing
   - Test your Python application directly

2. **Test on Windows:**
   - Use a Windows VM weekly
   - Or: Test directly on your client's Windows machine
   - Or: Keep a small Windows partition for testing

3. **Deploy:**
   - Copy .bat files to USB
   - Ensure CRLF line endings
   - Test on actual Windows systems

---

## Bottom Line

**You CAN develop Windows scripts on Linux.** You just need:
- A testing strategy (VM, dual boot, or client's machine)
- Line ending awareness (unix2dos is your friend)
- Shell script equivalents for rapid iteration
- Good documentation of what needs Windows testing

The inconvenience is real, but it's manageable with the right workflow. Choose the strategies that fit your development speed vs. testing thoroughness needs.

Most importantly: **Don't let Claude Code saying "I can't run that" stop you.** I can still:
- Write the scripts
- Review them for errors
- Create test equivalents
- Document test plans
- Help you set up VMs

Just can't execute Windows binaries on your Linux system. But that's what VMs are for!
