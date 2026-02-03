# HPM GitHub Download Problem - SOLVED

**Date:** 2026-01-23  0050
**Issue:** HPM "Get Latest Update" feature incorrectly reporting "already up to date"

## Problem Description

When running HPM's built-in "Get Latest Update" feature, the system reported:

```
You are already up to date with v0.1.7h.
No updates are available at this time.
```

However, the latest release on GitHub was actually `v0.1.7k`, not `v0.1.7h`.

### Initial Error

The first attempt to update produced this Git error:

```
Failed to download update from GitHub:

Git pull failed:
From https://github.com/juren53/HST-Metadata
 * branch            master     -> FETCH_HEAD
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
fatal: Need to specify how to reconcile divergent branches.
```

## Root Cause Analysis

The investigation revealed a **misalignment between Git tags and commits**:

1. **Local repository state:**
   - HEAD was at commit `1af0cc4` ("added four critiques of g2c.py to notes")
   - Local branch had diverged with 1 local commit and 6 remote commits

2. **After initial fix (git reset --hard origin/master):**
   - HEAD moved to `1af0cc4` which matched `origin/master`
   - However, the `v0.1.7k` tag pointed to an earlier commit `4a12a26`
   - HEAD was 1 commit AHEAD of the release tag

3. **Version detection issue:**
   - `__init__.py` correctly showed `__version__ = "0.1.7k"`
   - Git tag `v0.1.7k` existed at commit `4a12a26`
   - Current HEAD was at commit `1af0cc4` (one commit ahead)
   - HPM's git updater checks for commits behind origin, not version tags
   - Since local was ahead of or equal to origin, it reported "no updates available"

## The Core Problem

**HPM compares commit positions, not version strings or release tags.** When the local repository's HEAD is at or ahead of origin/master, HPM reports "already up to date" even if the code is actually ahead of the most recent tagged release.

In this case:
- GitHub Release: `v0.1.7k` at commit `4a12a26`
- Origin/master: commit `1af0cc4` (1 commit ahead of the tag)
- Local HEAD: commit `1af0cc4` (synchronized with origin/master)
- Result: No commits behind origin → HPM says "already up to date"

## Solution

### Immediate Fix

Reset the local repository to match the exact release tag:

```bash
git reset --hard v0.1.7k
```

This moves HEAD to commit `4a12a26` where the `v0.1.7k` tag is located.

### Alternative Fix for Divergent Branches

If you encounter the initial "divergent branches" error:

```bash
# Option 1: Discard local changes and match GitHub (recommended for client systems)
git reset --hard origin/master

# Option 2: Merge local and remote changes
git config pull.rebase false
git pull

# Option 3: Rebase local changes on top of remote
git config pull.rebase true
git pull
```

For client systems using HPM to receive updates, **Option 1 is recommended** as it ensures the local installation exactly matches what's published on GitHub.

## Lessons Learned

1. **Tag hygiene matters:** When creating a release, the tag should point to the latest commit that will be included in that release.

2. **Commit after tagging:** Any commits made after creating a release tag will cause version mismatches between the code version string and the Git state.

3. **Client vs. Development repos:** Client systems should track release tags, not the bleeding-edge master branch.

4. **Version checking logic:** HPM's current update checker uses commit-counting (`git rev-list --count HEAD..origin/branch`) which works for development but may not align with semantic versioning in releases.

## Recommendations

### For Future Releases

1. Create the version tag on the final commit
2. Don't push additional commits to master after tagging without bumping the version
3. Consider using release branches separate from master

### For HPM Improvement

Consider enhancing the git updater to:

1. Check for newer tags, not just commits ahead/behind
2. Compare semantic versions from `__init__.py` between local and remote
3. Provide clear messaging when local is ahead of the latest release tag

## Related Files

- `/home/juren/Projects/HST-Metadata/Photos/Version-2/Framework/__init__.py` - Version definition
- `/home/juren/Projects/HST-Metadata/Photos/Version-2/Framework/utils/git_updater.py` - Git update logic
- `/home/juren/Projects/HST-Metadata/Photos/Version-2/Framework/utils/github_version_checker.py` - Version comparison logic
