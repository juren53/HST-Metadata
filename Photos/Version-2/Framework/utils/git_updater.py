#!/usr/bin/env python3
"""
Git Updater Module

Handles git operations for updating the HPM Framework from GitHub.
Provides safe git pull functionality with status checking and error handling.

Author: HPM Development Team
Created: 2026-01-13
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple, Optional


class GitUpdateResult:
    """Data class for git update operation results"""
    def __init__(self):
        self.success = False
        self.already_up_to_date = False
        self.current_version = ""
        self.updated_version = ""
        self.error_message = ""
        self.output = ""
        self.files_changed = 0
        self.insertions = 0
        self.deletions = 0


class GitUpdater:
    """
    Handles git operations for updating HPM from GitHub
    
    Features:
    - Check if repository is up-to-date
    - Perform git pull with safety checks
    - Detect uncommitted changes
    - Parse git output for user-friendly messages
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize git updater
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
        """
        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            # Find the git root from current file location
            self.repo_path = self._find_git_root()
        
        if not self.repo_path:
            raise ValueError("Not in a git repository")
    
    def _find_git_root(self) -> Optional[Path]:
        """Find the git repository root directory"""
        current = Path(__file__).parent.parent.absolute()
        
        # Walk up the directory tree looking for .git
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        
        return None
    
    def _run_git_command(self, args: list, capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Run a git command and return results
        
        Args:
            args: List of command arguments (e.g., ['status', '--short'])
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=str(self.repo_path),
                capture_output=capture_output,
                text=True,
                timeout=30  # 30 second timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Git command timed out"
        except FileNotFoundError:
            return 1, "", "Git executable not found"
        except Exception as e:
            return 1, "", str(e)
    
    def is_git_repository(self) -> bool:
        """Check if the path is a valid git repository"""
        exit_code, _, _ = self._run_git_command(['rev-parse', '--git-dir'])
        return exit_code == 0
    
    def has_uncommitted_changes(self) -> Tuple[bool, str]:
        """
        Check if there are uncommitted changes
        
        Returns:
            Tuple of (has_changes, description)
        """
        exit_code, stdout, _ = self._run_git_command(['status', '--short'])
        
        if exit_code != 0:
            return False, ""
        
        if stdout.strip():
            # Parse the status output
            lines = stdout.strip().split('\n')
            modified = sum(1 for line in lines if line.startswith(' M') or line.startswith('M '))
            untracked = sum(1 for line in lines if line.startswith('??'))
            added = sum(1 for line in lines if line.startswith('A '))
            
            parts = []
            if modified > 0:
                parts.append(f"{modified} modified")
            if added > 0:
                parts.append(f"{added} added")
            if untracked > 0:
                parts.append(f"{untracked} untracked")
            
            description = f"{', '.join(parts)} file(s)"
            return True, description
        
        return False, ""
    
    def get_current_branch(self) -> str:
        """Get the current branch name"""
        exit_code, stdout, _ = self._run_git_command(['branch', '--show-current'])
        if exit_code == 0:
            return stdout.strip()
        return "unknown"
    
    def fetch_updates(self) -> bool:
        """
        Fetch updates from remote without merging
        
        Returns:
            True if fetch successful, False otherwise
        """
        exit_code, _, _ = self._run_git_command(['fetch', 'origin'])
        return exit_code == 0
    
    def get_remote_version(self) -> Optional[str]:
        """
        Get the version from the remote repository's __init__.py

        Returns:
            Version string or None if unable to determine
        """
        branch = self.get_current_branch()

        # The __init__.py is in Photos/Version-2/Framework/ relative to git root
        init_path = "Photos/Version-2/Framework/__init__.py"

        # Get __init__.py content from remote
        exit_code, stdout, _ = self._run_git_command(
            ['show', f'origin/{branch}:{init_path}']
        )

        if exit_code == 0:
            # Parse the __version__ line
            for line in stdout.split('\n'):
                if line.strip().startswith('__version__'):
                    # Extract version from: __version__ = "0.1.7f"
                    try:
                        version = line.split('=')[1].strip().strip('"').strip("'")
                        return version
                    except (IndexError, AttributeError):
                        pass

        return None
    
    def check_for_updates(self) -> Tuple[bool, str]:
        """
        Check if updates are available from remote
        
        Returns:
            Tuple of (updates_available, message)
        """
        # First, fetch the latest
        if not self.fetch_updates():
            return False, "Failed to fetch updates from remote"
        
        # Get current branch
        branch = self.get_current_branch()
        
        # Check if local is behind remote
        exit_code, stdout, _ = self._run_git_command(
            ['rev-list', '--count', f'HEAD..origin/{branch}']
        )
        
        if exit_code == 0:
            commits_behind = int(stdout.strip()) if stdout.strip() else 0
            if commits_behind > 0:
                return True, f"{commits_behind} commit(s) available"
            else:
                return False, "Already up-to-date"
        
        return False, "Unable to determine update status"
    
    def pull_updates(self) -> GitUpdateResult:
        """
        Perform git pull to update the repository
        
        Returns:
            GitUpdateResult with operation details
        """
        result = GitUpdateResult()
        
        # Check if we're in a git repository
        if not self.is_git_repository():
            result.error_message = "Not a git repository"
            return result
        
        # Check for uncommitted changes
        has_changes, changes_desc = self.has_uncommitted_changes()
        if has_changes:
            result.error_message = f"You have uncommitted changes: {changes_desc}\n\nPlease commit or stash your changes before updating."
            return result
        
        # Get current branch
        branch = self.get_current_branch()
        
        # Perform git pull
        exit_code, stdout, stderr = self._run_git_command(['pull', '--rebase', 'origin', branch])
        
        result.output = stdout + stderr
        
        if exit_code == 0:
            result.success = True
            
            # Check if already up-to-date
            if "Already up to date" in stdout or "Already up-to-date" in stdout:
                result.already_up_to_date = True
            else:
                # Parse the output for statistics
                result = self._parse_pull_output(stdout, result)
        else:
            result.error_message = f"Git pull failed:\n{stderr}"
        
        return result
    
    def _parse_pull_output(self, output: str, result: GitUpdateResult) -> GitUpdateResult:
        """
        Parse git pull output to extract statistics
        
        Args:
            output: Git pull stdout
            result: GitUpdateResult to populate
            
        Returns:
            Updated GitUpdateResult
        """
        lines = output.split('\n')
        
        for line in lines:
            # Look for: "X files changed, Y insertions(+), Z deletions(-)"
            if 'file' in line and 'changed' in line:
                parts = line.split(',')
                for part in parts:
                    if 'file' in part and 'changed' in part:
                        try:
                            result.files_changed = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif 'insertion' in part:
                        try:
                            result.insertions = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif 'deletion' in part:
                        try:
                            result.deletions = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
        
        return result
    
    def get_remote_url(self) -> str:
        """Get the remote origin URL"""
        exit_code, stdout, _ = self._run_git_command(['remote', 'get-url', 'origin'])
        if exit_code == 0:
            return stdout.strip()
        return ""

    def _get_local_version(self) -> Optional[str]:
        """
        Get the version from the local __init__.py file

        Returns:
            Version string or None if unable to determine
        """
        try:
            # The __init__.py is in the Framework directory (parent of utils/)
            framework_dir = Path(__file__).parent.parent
            init_path = framework_dir / "__init__.py"
            if init_path.exists():
                content = init_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if line.strip().startswith('__version__'):
                        try:
                            version = line.split('=')[1].strip().strip('"').strip("'")
                            return version
                        except (IndexError, AttributeError):
                            pass
        except Exception:
            pass
        return None

    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings semantically.
        Handles HPM version format like "0.1.7n" where the letter suffix
        indicates point releases (a < b < c < ... < z).

        Args:
            v1: First version string
            v2: Second version string

        Returns:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        import re

        def parse_version(v: str) -> tuple:
            # Remove 'v' prefix if present
            v = v.lstrip('v').strip()

            # Match pattern like "0.1.7n" or "0.1.7"
            match = re.match(r'^(\d+)\.(\d+)\.(\d+)([a-z])?$', v)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                patch = int(match.group(3))
                suffix = match.group(4) or ''  # Empty string if no suffix
                return (major, minor, patch, suffix)

            # Fallback: try to extract numbers
            parts = re.findall(r'\d+', v)
            if len(parts) >= 3:
                return (int(parts[0]), int(parts[1]), int(parts[2]), '')

            return (0, 0, 0, '')

        v1_parsed = parse_version(v1)
        v2_parsed = parse_version(v2)

        # Compare major.minor.patch first
        for i in range(3):
            if v1_parsed[i] < v2_parsed[i]:
                return -1
            elif v1_parsed[i] > v2_parsed[i]:
                return 1

        # If major.minor.patch are equal, compare suffix
        # Empty suffix (release) comes after lettered suffix (point release)
        # So "0.1.8" > "0.1.7z" but "0.1.7a" < "0.1.7b"
        suffix1, suffix2 = v1_parsed[3], v2_parsed[3]

        if suffix1 == suffix2:
            return 0
        elif suffix1 == '':
            return 1  # No suffix means release version (higher)
        elif suffix2 == '':
            return -1  # No suffix means release version (higher)
        elif suffix1 < suffix2:
            return -1
        else:
            return 1

    def get_update_info(self) -> dict:
        """
        Get comprehensive update information.

        Returns:
            dict with keys:
                - current_version: Local version string
                - remote_version: Remote version string
                - update_available: Boolean
                - error: Error message if any
        """
        info = {
            'current_version': None,
            'remote_version': None,
            'update_available': False,
            'error': None
        }

        # Get local version
        info['current_version'] = self._get_local_version()

        # Fetch from remote
        if not self.fetch_updates():
            info['error'] = "Failed to connect to GitHub"
            return info

        # Get remote version
        info['remote_version'] = self.get_remote_version()

        if not info['current_version']:
            info['error'] = "Could not determine current version"
            return info

        if not info['remote_version']:
            info['error'] = "Could not determine remote version"
            return info

        # Compare versions
        comparison = self._compare_versions(info['current_version'], info['remote_version'])
        info['update_available'] = comparison < 0  # current < remote

        return info

    def force_update(self) -> GitUpdateResult:
        """
        Force update to match remote, discarding all local changes.

        This is the recommended update method for client systems that just
        want the latest code from GitHub. Local modifications (logs, cache,
        temp files) are safely discarded.

        Uses: git fetch origin && git reset --hard origin/[branch]

        Returns:
            GitUpdateResult with operation details
        """
        result = GitUpdateResult()

        # Check if we're in a git repository
        if not self.is_git_repository():
            result.error_message = "Not a git repository"
            return result

        # Get current version before update
        result.current_version = self._get_local_version() or ""

        # Get current branch
        branch = self.get_current_branch()

        # Fetch latest from remote
        exit_code, _, stderr = self._run_git_command(['fetch', 'origin'])
        if exit_code != 0:
            result.error_message = f"Failed to fetch updates from GitHub:\n{stderr}"
            return result

        # Force reset to match remote exactly
        exit_code, stdout, stderr = self._run_git_command(
            ['reset', '--hard', f'origin/{branch}']
        )

        result.output = stdout + stderr

        if exit_code == 0:
            result.success = True

            # Get new version after update
            result.updated_version = self._get_local_version() or ""

            # Check if versions are the same (already up-to-date)
            if result.current_version == result.updated_version:
                result.already_up_to_date = True
        else:
            result.error_message = f"Failed to update:\n{stderr}"

        return result


def test_git_updater():
    """Test the git updater functionality"""
    print("=== Git Updater Test ===")
    print()
    
    try:
        updater = GitUpdater()
        print(f"✅ Repository found: {updater.repo_path}")
        print(f"   Branch: {updater.get_current_branch()}")
        print(f"   Remote: {updater.get_remote_url()}")
        print()
        
        # Check for uncommitted changes
        has_changes, desc = updater.has_uncommitted_changes()
        if has_changes:
            print(f"⚠️  Uncommitted changes: {desc}")
        else:
            print("✅ Working directory is clean")
        print()
        
        # Check for updates
        print("Checking for updates...")
        updates_available, message = updater.check_for_updates()
        if updates_available:
            print(f"📦 Updates available: {message}")
        else:
            print(f"✅ {message}")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    test_git_updater()
