# Procedure: Download a Specific HPM Version

This document describes how to download or switch to a specific earlier version of the HSTL Photo Metadata (HPM) framework.

## Prerequisites

- Git installed and available in PATH
- Access to the HST-Metadata repository (local clone or GitHub access)
- Basic familiarity with command line operations

## Method 1: Git Checkout (Recommended for Local Development)

This method switches your local repository to a specific version.

### Step 1: Open Command Prompt or Terminal

Navigate to your HPM Framework directory:
```bash
cd %USERPROFILE%\Projects\HST-Metadata\Photos\Version-2\Framework
```

### Step 2: Check Available Versions

List all available version tags:
```bash
git tag --list
```

Example output:
```
v0.0.10
v0.1.3
v0.1.5
v0.1.5a
...
```

### Step 3: Save Any Uncommitted Changes (if applicable)

Before switching versions, ensure your work is saved:
```bash
git status
git stash    # Temporarily saves uncommitted changes
```

### Step 4: Checkout the Desired Version

**Option A: Temporary checkout (detached HEAD state)**
```bash
git checkout v0.1.5
```
This puts you in "detached HEAD" state - you can view and run the code but shouldn't make commits.

**Option B: Create a branch from the version**
```bash
git checkout -b testing-v0.1.5 v0.1.5
```
This creates a new branch named `testing-v0.1.5` starting from version 0.1.5.

### Step 5: Verify the Version

Check that you're on the correct version:
```bash
git log -1 --oneline
```

### Step 6: Return to Latest Version

When finished testing, return to the main branch:
```bash
git checkout master
git stash pop    # Restore any stashed changes (if applicable)
```

---

## Method 2: GitHub Web Download

This method downloads a ZIP file of a specific version without requiring Git.

### Step 1: Navigate to GitHub Releases

Open your web browser and go to:
```
https://github.com/juren53/HST-Metadata/releases
```

### Step 2: Find the Desired Version

Scroll through the releases list to find the version you need.

### Step 3: Download the Source Code

Click on either:
- **Source code (zip)** - for Windows users
- **Source code (tar.gz)** - for Linux/macOS users

### Step 4: Extract the Archive

Extract the downloaded file to your desired location.

### Step 5: Install Dependencies

Navigate to the extracted Framework directory and install dependencies:
```bash
pip install -r requirements.txt
```

---

## Method 3: Git Clone with Specific Tag

This method clones only a specific version to a new directory.

### Step 1: Choose a Destination Directory

```bash
cd %USERPROFILE%\Projects
```

### Step 2: Clone with Specific Tag

```bash
git clone --branch v0.1.5 --depth 1 https://github.com/juren53/HST-Metadata.git HST-Metadata-v0.1.5
```

Parameters:
- `--branch v0.1.5` - specifies the tag/version to clone
- `--depth 1` - shallow clone (only the specified version, no history)
- `HST-Metadata-v0.1.5` - destination folder name

### Step 3: Navigate to Framework

```bash
cd HST-Metadata-v0.1.5\Photos\Version-2\Framework
```

---

## Method 4: Checkout by Commit Hash

Use this method when a version doesn't have a tag.

### Step 1: Find the Commit Hash

View the commit history to find the desired commit:
```bash
git log --oneline --all
```

Or search for a specific date or message:
```bash
git log --oneline --after="2026-01-15" --before="2026-01-16"
```

### Step 2: Checkout the Commit

```bash
git checkout abc1234    # Replace with actual commit hash
```

---

## Available Tagged Versions

As of 2026-01-18, the following versions have git tags:

| Version | Tag | Date |
|---------|-----|------|
| 0.1.5e | v0.1.5e | 2026-01-15 |
| 0.1.5c | v0.1.5c | 2026-01-13 |
| 0.1.5b | v0.1.5b | 2026-01-12 |
| 0.1.5a | v0.1.5a | 2026-01-12 |
| 0.1.5 | v0.1.5 | 2026-01-12 |
| 0.1.4 | v0.1.4 | 2026-01-07 |
| 0.1.3e | v0.1.3e | 2026-01-03 |
| 0.1.3d | v0.1.3d | 2026-01-03 |
| 0.1.3b | v0.1.3b | 2026-01-02 |
| 0.1.3a | v0.1.3a | 2025-12-31 |
| 0.1.3 | v0.1.3 | 2025-12-18 |
| 0.1.2 | v0.1.2 | 2025-12-16 |
| 0.1.1 | v0.1.1 | 2025-12-14 |
| 0.0.10 | v0.0.10 | 2025-12-14 |
| 0.0.9 | v0.0.9 | 2025-12-13 |
| 0.0.8 | v0.0.8 | 2025-12-13 |
| 0.0.7 | v0.0.7 | 2025-12-12 |
| 0.0.6 | v0.0.6 | 2025-12-12 |
| 0.0.5 | v0.0.5 | 2025-12-08 |
| 0.0.4 | v0.0.4 | 2025-12-08 |
| 0.0.3 | v0.0.3 | 2025-12-08 |

To refresh this list, run: `git tag --list`

---

## Troubleshooting

### "error: Your local changes would be overwritten"

You have uncommitted changes. Either commit them, stash them, or discard them:
```bash
git stash           # Save changes temporarily
git checkout .      # Discard all changes (use with caution)
```

### "fatal: reference is not a tree"

The tag or commit hash doesn't exist. Verify the tag name:
```bash
git tag --list | findstr "0.1.5"
```

### Version doesn't have a tag

Some versions (e.g., 0.1.5d, 0.1.3f-i, 0.1.7b) may not have tags. Use Method 4 (checkout by commit hash) or check CHANGELOG.md for the commit date and search by date.

### Need to update tag list from remote

```bash
git fetch --tags
```

---

## See Also

- [CHANGELOG.md](../CHANGELOG.md) - Complete version history with changes
- [HPM_Installation.md](../HPM_Installation.md) - Full installation guide
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide

---

*Document created: 2026-01-18*
