# Project Rules

## Timezone Convention
**CRITICAL**: ALL timestamps, dates, and times in this project MUST use Central Time USA (CST/CDT), NEVER UTC or any other timezone.

This applies to:
- Changelog entries in source code headers
- Version labels and dates in the UI
- Git commit messages (if applicable)
- Documentation timestamps
- Any other date/time references in the project

Example formats:
- Changelog: `Tue 03 Dec 2025 09:20:00 PM CST`
- Version label: `v0.0.9b 2025-12-03`
- Always include timezone indicator (CST or CDT) in full timestamps
- an make certain time is represented as CST or CDT . . . and NOT GMT!!

## Version Numbering
- Format: `v0.0.X` for releases
- Format: `v0.0.Xa`, `v0.0.Xb`, `v0.0.Xc` for point releases/patches
- Update version info in the README.md file, UI label, the About dialog and header comment when making releases  Note:  Version info consists of the Version Number, the Date  AND THE TIME!!!  e.g.  v0.2.6  2025-12-22 1125  and time should always be CST/CDT

## Version Update Checklist

# When updating version information, update ALL of the following files:
# Format: file_path | location_description

# Core Python Modules
__init__.py | __version__ variable (line ~9)
gui/__init__.py | __version__ and __commit_date__ variables (lines ~7-8)
gui/hstl_gui.py | Module docstring Version/Commit Date (lines ~8-9) and __version__/__commit_date__ variables (lines ~27-28)
gui/main_window.py | Window title in setWindowTitle() (line ~52) and About dialog version and commit date (lines ~500-501)
gui/widgets/step_widget.py | Version label displayed in UI (line ~55)

# Documentation Files
docs/GUI_QUICKSTART.md | Version and Commit Date footer (lines ~272-273)
gui/README.md | Version and Commit Date header (lines ~3-4)
CHANGELOG.md | Add new version section at top with changes (line ~8)

# Notes:
# - Update CHANGELOG.md first with new version section describing changes
# - All timestamps should use format: YYYY-MM-DD HH:MM in CST (Central Standard Time)
# - IMPORTANT: ALWAYS use CST time zone, NOT UTC!!!
# - Version format: v0.0.X (with 'v' prefix in UI, without 'v' in code)

