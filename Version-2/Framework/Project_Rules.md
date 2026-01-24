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
- Changelog: `Sat 18 Jan 2026 10:30:00 AM CST`
- Version label: `v0.1.7c | 2026-01-18 10:30 CST`
- Always include timezone indicator (CST or CDT) in full timestamps
- And make certain time is represented as CST or CDT . . . and NOT GMT!!

## Version Numbering
- Format: `v0.1.X` for releases
- Format: `v0.1.Xa`, `v0.1.Xb`, `v0.1.Xc` for point releases/patches
- Update version info in all locations listed in the checklist below
- Version info consists of the Version Number, the Date AND THE TIME!!! e.g. `v0.1.7c 2026-01-18 10:30 CST`

## Version Update Checklist

Version information is **centralized** in `__init__.py`. All UI components import from there automatically.

### Files Requiring Manual Update (5 files)

| File | Location | Approx Line |
|------|----------|-------------|
| `__init__.py` | `__version__` and `__commit_date__` | ~9-10 |
| `CHANGELOG.md` | Add new version section at top | ~8 |
| `docs/GUI_QUICKSTART.md` | Version and Commit Date footer | ~272-273 |
| `docs/USER_GUIDE.md` | Version and Commit Date footer | ~173-174 |
| `gui/README.md` | Version and Commit Date header | ~3-4 |

### Files That Auto-Update (no manual changes needed)

These files import `__version__` and `__commit_date__` from `__init__.py` at runtime:

- `gui/__init__.py` - imports from parent
- `gui/hstl_gui.py` - imports and uses variables
- `gui/main_window.py` - title bar and About dialog
- `gui/widgets/step_widget.py` - Current Batch tab header
- `gui/widgets/batch_list_widget.py` - Batches tab header

### Update Order

1. **`__init__.py` first** - Update `__version__` and `__commit_date__`
2. **`CHANGELOG.md`** - Add new version section describing changes
3. **Documentation files** - Update footers/headers in markdown files

### Notes

- All timestamps should use format: `YYYY-MM-DD HH:MM CST`
- **IMPORTANT**: ALWAYS use CST time zone, NOT UTC!!!
- Version format: `v0.1.X` (with 'v' prefix in UI, without 'v' in code variables)

## Verify Version Updates

After updating, run this command from the Framework directory to confirm the new version appears:

```bash
grep -rn "0\.1\.7c" --include="*.py" --include="*.md" .
```

Replace `0\.1\.7c` with your new version number. You should see matches in `__init__.py` and the markdown documentation files.

## Post-Update Testing

After updating version info, **launch the application and verify**:

1. **Title bar** shows correct version (e.g., "HSTL Photo Framework v0.1.7c")
2. **Help > About** dialog shows correct version and commit date
3. **Batches tab** header (top-right) shows correct version
4. **Current Batch tab** header (top-right) shows correct version

## Post-Commit Steps (REQUIRED)

After committing and pushing version changes:

1. **Create Git Tag**:
   ```bash
   git tag -a v0.1.Xa -m "Release v0.1.Xa: Brief description of changes"
   git push origin v0.1.Xa
   ```

2. **Create GitHub Release** (CRITICAL - required for "Check for Updates" feature):
   ```bash
   gh release create v0.1.Xa --title "HPM v0.1.Xa - Feature Name" --notes "## Release Notes..."
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
   gh release create v0.1.Xa --title "HPM v0.1.Xa - Feature Name" --notes "Release description..."
   ```

3. Use backtick-n (\`n) for newlines in PowerShell:
   ```powershell
   gh release create v0.1.7c --title "HPM v0.1.7c - UI Improvements" --notes "## Release Notes`n`nFeature description...`n`n### Changes`n- Change 1`n- Change 2"
   ```

4. Verify the release was created:
   ```bash
   gh release view v0.1.Xa
   ```

#### Option 2: Using GitHub Web Interface

1. Navigate to: `https://github.com/juren53/HST-Metadata/releases/new`

2. **Choose a tag**: Select your tag (e.g., `v0.1.7c`) from dropdown

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
- Use same version number as tag (v0.1.Xa)
- Include comprehensive release notes from CHANGELOG.md
- Test the "Check for Updates" feature after creating release
- Release enables automatic update detection for all users

## Centralized Version Architecture

Version information is centralized in `Framework/__init__.py`:

```python
__version__ = "0.1.7c"
__commit_date__ = "2026-01-18 10:30 CST"
```

All UI components import these values at runtime:

```python
from __init__ import __version__, __commit_date__
```

This reduces manual updates from 11+ locations to just 5 files (1 Python + 4 markdown).
