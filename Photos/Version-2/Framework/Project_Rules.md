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

When updating version information, update **ALL** of the following files:

### Core Python Modules

| File | Location | Approx Line |
|------|----------|-------------|
| `__init__.py` | `__version__` variable | ~9 |
| `gui/__init__.py` | `__version__` and `__commit_date__` variables | ~7-8 |
| `gui/hstl_gui.py` | Module docstring (Version/Commit Date) | ~8-9 |
| `gui/hstl_gui.py` | `__version__` and `__commit_date__` variables | ~31-32 |
| `gui/main_window.py` | `setWindowTitle()` - Title bar | ~88 |
| `gui/main_window.py` | About dialog version and commit date | ~702-703 |
| `gui/widgets/step_widget.py` | Version label (Current Batch tab header) | ~64-65 |
| `gui/widgets/batch_list_widget.py` | Version label (Batches tab header) | ~69-70 |

### Documentation Files

| File | Location | Approx Line |
|------|----------|-------------|
| `CHANGELOG.md` | Add new version section at top | ~8 |
| `docs/GUI_QUICKSTART.md` | Version and Commit Date footer | ~272-273 |
| `gui/README.md` | Version and Commit Date header | ~3-4 |

### Update Order

1. **CHANGELOG.md first** - Add new version section describing changes
2. **Core Python modules** - Update all version strings
3. **Documentation files** - Update footers/headers

### Notes

- All timestamps should use format: `YYYY-MM-DD HH:MM CST`
- **IMPORTANT**: ALWAYS use CST time zone, NOT UTC!!!
- Version format: `v0.1.X` (with 'v' prefix in UI, without 'v' in code variables)
- Line numbers are approximate - search for the previous version string if needed

## Verify Version Updates

After updating, run this command from the Framework directory to confirm all locations show the new version:

```bash
grep -rn "0\.1\.7c" --include="*.py" --include="*.md" .
```

Replace `0\.1\.7c` with your new version number. You should see approximately 12-14 matches across the files listed above.

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

## Future Consideration: Centralized Version

To reduce manual updates in the future, consider creating a single source of truth for version info:

1. Have UI components read from `__init__.__version__` at runtime instead of hardcoding strings
2. Use a build script to update version strings automatically
3. This would reduce the checklist from 11+ locations to just 2-3

This is noted for potential future refactoring but is not required for current workflow.
