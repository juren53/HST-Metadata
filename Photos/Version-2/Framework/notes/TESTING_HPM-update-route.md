# Testing HPM Update Features

This guide documents various methods to test the "Get Latest Updates" feature without continuously releasing minor version bumps.

---

## Method 1: Test Script (Recommended) ✅

The easiest and safest way to test all update dialog scenarios without modifying any files or git state.

### Usage

```bash
python test_update_dialog.py
```

This opens a window with buttons to test each dialog:
- **Update Available** - Main update prompt with version info
- **Already Up-to-Date** - No updates available
- **Uncommitted Changes Warning** - Warning about unsaved changes
- **Update Complete** - Success message after update
- **Update Failed** - Error message when update fails

### Customization

Edit `test_update_dialog.py` line 24 to test different versions:

```python
remote_version = "0.1.7g"  # Change to any version for testing
```

### Advantages
- ✅ No git operations required
- ✅ No version file modifications
- ✅ Test all dialog scenarios independently
- ✅ Safe - can't accidentally break anything
- ✅ Fast iteration

---

## Method 2: Temporary Local Version Change

Quick way to test the actual update flow with real git operations.

### Steps

1. **Lower your local version** in `__init__.py`:
   ```python
   __version__ = "0.1.7e"  # Temporarily set to older version
   ```

2. **Run HPM** and test Help → Get Latest Updates
   - It will detect remote has `0.1.7f` and show update dialog
   - You can proceed with actual git pull to test full flow

3. **Restore version** after testing:
   ```python
   __version__ = "0.1.7f"  # Back to current
   ```

### Advantages
- ✅ Tests real git update flow
- ✅ Tests version detection from remote
- ✅ Simple and quick

### Disadvantages
- ⚠️ Requires manual file editing
- ⚠️ Easy to forget to restore version
- ⚠️ Can't test "update available" to future versions

---

## Method 3: Test Branch Workflow

For testing updates to future versions or complex scenarios.

### Setup

1. **Create test branch** with higher version:
   ```bash
   git checkout -b test-update-dialog
   ```

2. **Edit version** in `__init__.py`:
   ```python
   __version__ = "0.1.7g-test"
   ```

3. **Commit and push**:
   ```bash
   git commit -am "Test version for update dialog"
   git push origin test-update-dialog
   ```

4. **Switch back to master**:
   ```bash
   git checkout master
   ```

5. **Temporarily modify** `utils/git_updater.py` to check test branch:
   ```python
   # In get_current_branch() or check_for_updates()
   branch = "test-update-dialog"  # Instead of actual branch
   ```

### Testing

1. Run HPM with modified git_updater
2. Click Help → Get Latest Updates
3. It will show `0.1.7g-test` as available update

### Cleanup

1. Switch back to master
2. Restore git_updater.py
3. Delete test branch:
   ```bash
   git branch -d test-update-dialog
   git push origin --delete test-update-dialog
   ```

### Advantages
- ✅ Tests updates to future versions
- ✅ Tests full git workflow
- ✅ Can test multiple scenarios with different branches

### Disadvantages
- ⚠️ More complex setup
- ⚠️ Requires git operations
- ⚠️ Need to clean up afterwards

---

## Method 4: Mock Git Updater

For unit testing or automated testing.

### Concept

Create a mock version of `GitUpdater` class that returns predetermined values:

```python
class MockGitUpdater:
    def check_for_updates(self):
        return True, "1 commit(s) available"
    
    def get_remote_version(self):
        return "0.1.7g"
    
    def get_current_branch(self):
        return "master"
    
    def has_uncommitted_changes(self):
        return False, ""
    
    def pull_updates(self):
        result = GitUpdateResult()
        result.success = True
        result.files_changed = 5
        return result
```

### Usage

1. Create mock in test file
2. Replace `self.git_updater` in MainWindow with mock
3. Test all update scenarios

### Advantages
- ✅ Full control over test scenarios
- ✅ No git operations
- ✅ Fast and repeatable
- ✅ Good for automated testing

### Disadvantages
- ⚠️ Requires test framework setup
- ⚠️ Doesn't test real git operations
- ⚠️ More code to maintain

---

## Best Practices

### During Development

1. **Use Method 1 (Test Script)** for UI/UX testing
   - Quick iterations on dialog appearance
   - Test all user-facing messages
   - Verify button behavior

2. **Use Method 2 (Temporary Version Change)** for integration testing
   - Test actual git operations
   - Verify version detection works
   - Test update completion flow

### Before Release

1. Test with real version difference:
   - Have a colleague test with older version
   - Or use Method 3 with test branch

2. Verify all dialog scenarios:
   - Update available
   - Already up-to-date
   - Uncommitted changes warning
   - Success message
   - Error handling

### Testing Checklist

- [ ] Update available dialog shows correct versions
- [ ] "Download" language (not "pull")
- [ ] Remote version displays correctly
- [ ] Progress dialog shows user-friendly text
- [ ] Success message is clear
- [ ] Error messages are helpful
- [ ] Uncommitted changes warning works
- [ ] Already up-to-date message is friendly
- [ ] Status bar updates appropriately

---

## Common Issues

### Remote Version Shows None

**Problem**: `get_remote_version()` returns None

**Solutions**:
- Ensure `git fetch origin` has been run
- Check that remote has `__init__.py` with `__version__`
- Verify branch name is correct

### "Already Up-to-Date" When Testing

**Problem**: Can't trigger update dialog because version matches

**Solution**: Use Method 1 (Test Script) or Method 2 (lower local version)

### Git Errors During Testing

**Problem**: Git operations fail during testing

**Solution**:
- Check for uncommitted changes first
- Ensure network connectivity
- Verify git credentials are configured

---

## Future Improvements

Consider adding:
- Automated UI tests using pytest-qt
- Mock server for testing update checks
- Test mode flag in settings to enable test dialogs
- Dry-run mode for git operations

---

## Related Files

- `test_update_dialog.py` - Test script for dialog previews
- `utils/git_updater.py` - Git update functionality
- `gui/main_window.py` - Update dialog implementation
- `CHANGELOG.md` - Version history and changes

---

**Last Updated**: 2026-01-19  
**Applies to Version**: 0.1.7f+
