# SysMon Project Rules

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

## Version Numbering
- Format: `v0.0.X` for releases
- Format: `v0.0.Xa`, `v0.0.Xb`, `v0.0.Xc` for point releases/patches
- Update version info in the README.md file, UI label, the About dialog and header comment when making releases  Note:  Version info consists of the Version Number, the Date  AND THE TIME!!!  e.g.  v0.2.6  2025-12-22 1125  and time should always be CST/CDT

