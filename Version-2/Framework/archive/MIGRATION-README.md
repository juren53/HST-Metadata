# HST-Metadata Repository Migration Guide

## Overview

The HST-Metadata repository has been cleaned to remove large binary files (TIFF images and executables) from its git history. This reduced the repository size from **2.6 GB to 7.2 MB** (99.7% reduction).

If you have an existing clone of the old repository, you need to migrate to the cleaned version.

## Quick Start

### For Windows (PowerShell)

1. Download the migration script from the repository
2. Run it:
   ```powershell
   .\migrate-to-cleaned-repo.ps1
   ```

### For Other Systems

See the "Manual Migration" section below.

---

## Migration Script Usage

### Basic Usage

The script will auto-detect the repository at the default location:
```powershell
.\migrate-to-cleaned-repo.ps1
```

### Custom Repository Path

If your repository is in a different location:
```powershell
.\migrate-to-cleaned-repo.ps1 -RepoPath "D:\MyProjects\HST-Metadata"
```

### Migration Options

The script offers two migration methods:

#### Option 1: Fresh Clone (Recommended)
- **Safest option**
- Creates a new directory with the cleaned repository
- Keeps your old repository intact until you verify the new one
- Use this if you want to be extra cautious

#### Option 2: Force Reset
- **Faster option**
- Updates the existing directory in place
- **WARNING:** Deletes all uncommitted changes
- Use this only if you have no uncommitted work

---

## What the Script Does

1. **Checks** your repository location and current size
2. **Detects** any uncommitted changes
3. **Offers** to create a backup if you have uncommitted work
4. **Migrates** using your chosen method:
   - Fresh Clone: Downloads clean repo to new directory
   - Force Reset: Resets existing repo to match clean version
5. **Reports** the size savings

---

## Manual Migration

### For Windows (PowerShell)

#### Fresh Clone Method
```powershell
# Navigate to parent directory
cd C:\Users\YourName\Projects

# Rename old repository
Rename-Item HST-Metadata HST-Metadata-old

# Clone cleaned repository
git clone https://github.com/juren53/HST-Metadata.git

# After verifying the new clone works, delete old one
Remove-Item -Recurse -Force HST-Metadata-old
```

#### Force Reset Method
```powershell
cd C:\Users\YourName\Projects\HST-Metadata

# Backup any uncommitted changes first!
git stash

# Fetch and reset to cleaned repository
git fetch origin
git reset --hard origin/master
git clean -fdx

# Clean up git history
git reflog expire --expire=now --all
git gc --aggressive --prune=now
```

### For Linux/Mac (Bash)

#### Fresh Clone Method
```bash
# Navigate to parent directory
cd ~/Projects

# Rename old repository
mv HST-Metadata HST-Metadata-old

# Clone cleaned repository
git clone https://github.com/juren53/HST-Metadata.git

# After verifying the new clone works, delete old one
rm -rf HST-Metadata-old
```

#### Force Reset Method
```bash
cd ~/Projects/HST-Metadata

# Backup any uncommitted changes first!
git stash

# Fetch and reset to cleaned repository
git fetch origin
git reset --hard origin/master
git clean -fdx

# Clean up git history
git reflog expire --expire=now --all
git gc --aggressive --prune=now
```

---

## FAQ

### Q: What if I have uncommitted changes?

**A:** The script will detect them and offer to create a backup. You can also manually backup:
```powershell
# Create a backup
Copy-Item -Path HST-Metadata -Destination HST-Metadata-backup -Recurse
```

### Q: Will this affect GitHub?

**A:** No, the GitHub repository has already been cleaned. This only updates your local clone.

### Q: Can I still access the old large files?

**A:** No, they have been permanently removed from the repository history. If you need them:
1. Check your local working directory before migration
2. Look in any backups you created
3. The files should still exist in your local file system if they were untracked

### Q: What happens if I try to push/pull without migrating?

**A:** Git will reject the operation with a "non-fast-forward" error because the histories are incompatible. You must migrate to continue working with the repository.

### Q: Do I need to migrate?

**A:** If you want to continue working with this repository and syncing with GitHub, yes. The old and new histories are incompatible.

### Q: How do I know the migration worked?

**A:** Check your `.git` directory size:
```powershell
Get-ChildItem .git -Recurse -File | Measure-Object -Property Length -Sum | Select-Object @{Name="SizeMB";Expression={[math]::Round($_.Sum/1MB, 2)}}
```

It should be around **7-8 MB**. If it's over 100 MB, the migration didn't complete properly.

---

## What Files Were Removed

The following file types were removed from git history:
- `*.tif` / `*.tiff` (TIFF images)
- `*.exe` (Windows executables)
- `*.pkg` (Package files)

These files are now listed in `.gitignore` to prevent them from being added again.

---

## Support

If you encounter issues with the migration script or have questions, contact the repository maintainer or file an issue on GitHub.
