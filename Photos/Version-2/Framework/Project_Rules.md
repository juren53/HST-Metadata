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
docs/USER_GUIDE.md | Version and Commit Date in document
gui/README.md | Version and Commit Date header (lines ~3-4)
CHANGELOG.md | Add new version section at top with changes (line ~8)

# Notes:
# - Update CHANGELOG.md first with new version section describing changes
# - All timestamps should use format: YYYY-MM-DD HH:MM in CST (Central Standard Time)
# - IMPORTANT: ALWAYS use CST time zone, NOT UTC!!!
# - Version format: v0.0.X (with 'v' prefix in UI, without 'v' in code)

## Post-Commit Steps (REQUIRED)

After committing and pushing version changes:

1. **Create Git Tag**:
   ```bash
   git tag -a v0.0.Xa -m "Release v0.0.Xa: Brief description of changes"
   git push origin v0.0.Xa
   ```

2. **Create GitHub Release** (CRITICAL - required for "Check for Updates" feature):
   ```bash
   gh release create v0.0.Xa --title "HPM v0.0.Xa - Feature Name" --notes "## Release Notes..."
   ```
   See "GitHub Release Procedure" section below for detailed template and instructions.

3. **Verify**:
   - Check release appears at: https://github.com/juren53/HST-Metadata/releases
   - Test "Check for Updates" in HPM GUI to confirm version detection works

## GitHub Release Procedure

**CRITICAL**: After creating and pushing a version tag, you MUST create a GitHub Release for the "Check for Updates" feature to work correctly.

### Why This Is Required

- **Git Tags** alone are NOT sufficient
- The version checker queries the GitHub Releases API: `https://api.github.com/repos/juren53/HST-Metadata/releases/latest`
- Without a release, users will see "No releases available" even though tags exist
- GitHub Releases provide structured release information, notes, and download URLs

### Release Creation Steps

#### Option 1: Using GitHub CLI (Recommended)

1. Ensure GitHub CLI is installed and authenticated:
   ```bash
   gh --version
   gh auth status
   ```

2. Create the release from your tag:
   ```bash
   gh release create v0.0.Xa --title "HPM v0.0.Xa - Feature Name" --notes "Release description..."
   ```

3. Use backtick-n (\`n) for newlines in PowerShell:
   ```powershell
   gh release create v0.1.5a --title "HPM v0.1.5a - Get Latest Updates Feature" --notes "## Release Notes\`n\`nFeature description...\`n\`n### Changes\`n- Change 1\`n- Change 2"
   ```

4. Verify the release was created:
   ```bash
   gh release view v0.0.Xa
   ```

#### Option 2: Using GitHub Web Interface

1. Navigate to: `https://github.com/juren53/HST-Metadata/releases/new`

2. **Choose a tag**: Select your tag (e.g., `v0.1.5a`) from dropdown

3. **Release title**: Format as `HPM vX.X.Xa - Feature Name`

4. **Description**: Include:
   - Brief overview
   - New features list
   - Safety features (if applicable)
   - Technical details
   - Documentation updates
   - Link to full CHANGELOG.md

5. Click **"Publish release"**

### Release Notes Template

```markdown
## HPM Release vX.X.Xa - Feature Name

**Point release: Brief description**

Release Date: YYYY-MM-DD HH:MM CST

### New Features

- Feature 1
- Feature 2
- Feature 3

### Technical Details

- New Module: path/to/module.py (XXX lines)
- GUI Integration: modifications made
- Background thread implementation
- Safety checks and error handling

### Documentation

- Added/Updated documentation files
- CHANGELOG.md updates

### Benefits

- Why this matters to users
- What problems it solves

**Full Changelog**: https://github.com/juren53/HST-Metadata/blob/master/Photos/Version-2/Framework/CHANGELOG.md
```

### Verification

After creating the release:

1. Visit: `https://github.com/juren53/HST-Metadata/releases`
2. Verify your release appears in the list
3. Test the "Check for Updates" feature in HPM GUI
4. Should now show proper version comparison instead of "No releases available"

### Important Notes

- Create release IMMEDIATELY after pushing tag
- Use same version number as tag (v0.0.Xa)
- Include comprehensive release notes from CHANGELOG.md
- Test the "Check for Updates" feature after creating release
- Release enables automatic update detection for all users

