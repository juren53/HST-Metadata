# WinPython Portable USB Setup

This directory contains everything you need to make WinPython work portably on a USB drive, regardless of which drive letter gets assigned.

## Files in This Directory

### Documentation
| File | Purpose |
|------|---------|
| `QUICK_START.md` | **Start here!** Simple 3-step guide to get portable WinPython working |
| `USB_PORTABLE_SETUP.md` | Comprehensive guide with detailed explanations and alternatives |
| `CROSS_PLATFORM_STRATEGY.md` | **Important!** How to develop Windows scripts on Linux |
| `LINUX_WORKFLOW_CHEATSHEET.md` | Quick reference commands for Linux development |
| `WinPythons_activate-bat_explained.md` | Background info on how WinPython activation works |

### Scripts - Windows Deployment
| File | Purpose |
|------|---------|
| `LAUNCH_HPM_PORTABLE.bat` | Ready-to-use portable launcher for Windows USB |

### Scripts - Linux Development & Testing
| File | Purpose |
|------|---------|
| `launch_hpm_portable.sh` | Linux equivalent for testing application logic |
| `validate_windows_scripts.sh` | Check Windows scripts for common issues |
| `fix_line_endings.sh` | Convert line endings to Windows format (CRLF) |

## Get Started in 2 Minutes

### For Windows USB Deployment
1. **Read:** Open `QUICK_START.md` for the essentials
2. **Copy:** Put `LAUNCH_HPM_PORTABLE.bat` at the root of your USB drive
3. **Edit:** Adjust the paths in the batch file (lines 15-17) to match your USB structure
4. **Test:** Double-click the batch file to launch on Windows

### For Linux Development Workflow
1. **Read:** Open `LINUX_WORKFLOW_CHEATSHEET.md` for quick commands
2. **Develop:** Edit Windows .bat files on your Linux system
3. **Validate:** Run `./validate_windows_scripts.sh` to check for issues
4. **Fix:** Run `./fix_line_endings.sh` to convert to Windows format
5. **Test Logic:** Run `./launch_hpm_portable.sh` to test on Linux
6. **Deploy:** Copy .bat files to USB and test on Windows

## The Problem This Solves

If you install WinPython to `D:\` and then plug the USB into another computer where `D:\` is the DVD drive, WinPython won't work because it's now on `E:\` or `F:\`.

**This solution** automatically detects whatever drive letter Windows assigns and adjusts all paths accordingly.

## How It Works (Simple Version)

The batch file uses `%~d0` which is a special variable that means "the drive letter where this batch file is located."

So instead of:
```batch
D:\WinPython\activate.bat  ← Breaks when drive letter changes
```

We use:
```batch
%~d0\WinPython\activate.bat  ← Always works!
```

## Questions?

- **Quick USB setup?** → See `QUICK_START.md`
- **Developing on Linux?** → See `LINUX_WORKFLOW_CHEATSHEET.md` ⭐
- **Cross-platform strategy?** → See `CROSS_PLATFORM_STRATEGY.md`
- **Detailed USB explanation?** → See `USB_PORTABLE_SETUP.md`
- **How does WinPython work?** → See `WinPythons_activate-bat_explained.md`

## Summary

Making WinPython portable boils down to one rule:

**Never use absolute paths (like `D:\...`).
Always use relative paths (like `%~d0\...`).**

Happy portable Python development!
