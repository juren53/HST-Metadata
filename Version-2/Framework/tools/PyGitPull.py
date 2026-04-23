#!/usr/bin/env python3
"""
Git Pull without Git - A pure Python implementation
Pulls updates from a Git repository using HTTP/HTTPS without requiring Git installation.
Remote repository is authoritative - local changes are overwritten.
"""

import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import json
import re
from pathlib import Path


def read_git_config(repo_path):
    """Read .git/config and extract remote URL, owner, repo, and branch info."""
    git_dir = os.path.join(repo_path, '.git')
    config_path = os.path.join(git_dir, 'config')

    if not os.path.exists(config_path):
        return None, None, None, None

    with open(config_path, 'r') as f:
        config_content = f.read()

    # Extract remote origin URL
    url_match = re.search(r'\[remote "origin"\][^\[]*url\s*=\s*(.+)', config_content)
    if not url_match:
        return None, None, None, None

    url = url_match.group(1).strip()

    # Parse GitHub URL to get owner and repo
    # Handle https://github.com/owner/repo.git format
    github_match = re.search(r'github\.com[/:]([^/]+)/([^/.\s]+)', url)
    if not github_match:
        return None, None, None, None

    owner = github_match.group(1)
    repo = github_match.group(2)
    if repo.endswith('.git'):
        repo = repo[:-4]

    # Get current branch from HEAD
    head_path = os.path.join(git_dir, 'HEAD')
    branch = 'main'
    if os.path.exists(head_path):
        with open(head_path, 'r') as f:
            head_content = f.read().strip()
        if head_content.startswith('ref: refs/heads/'):
            branch = head_content.replace('ref: refs/heads/', '')

    return url, owner, repo, branch


def get_local_commit_sha(repo_path, branch):
    """Get the current local commit SHA."""
    ref_path = os.path.join(repo_path, '.git', 'refs', 'heads', branch)
    if os.path.exists(ref_path):
        with open(ref_path, 'r') as f:
            return f.read().strip()
    return None


def get_remote_commit_sha(owner, repo, branch):
    """Get the latest commit SHA from remote."""
    ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}"
    try:
        with urllib.request.urlopen(ref_url) as response:
            data = json.loads(response.read().decode())
            return data.get('object', {}).get('sha')
    except urllib.error.HTTPError as e:
        print(f"Error getting remote commit SHA: {e}")
        return None
    except Exception as e:
        print(f"Error getting remote commit SHA: {e}")
        return None


def get_tree_recursive(owner, repo, branch):
    """Get the complete file tree recursively from remote."""
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        with urllib.request.urlopen(tree_url) as response:
            data = json.loads(response.read().decode())
            return data.get('tree', [])
    except Exception as e:
        print(f"Error getting repository tree: {e}")
        return []


def download_file(url, destination):
    """Download a file from URL to destination."""
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    try:
        with urllib.request.urlopen(url) as response:
            with open(destination, 'wb') as f:
                f.write(response.read())
        return True
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"Error downloading {url}: {e}")
        return False


def get_local_files(repo_path):
    """Get set of all tracked files in the repository (excluding .git)."""
    local_files = set()
    for root, dirs, files in os.walk(repo_path):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            # Normalize path separators
            rel_path = rel_path.replace(os.sep, '/')
            local_files.add(rel_path)

    return local_files


def update_refs(repo_path, branch, commit_sha):
    """Update local refs to point to new commit."""
    git_dir = os.path.join(repo_path, '.git')

    # Update local branch ref
    ref_path = os.path.join(git_dir, 'refs', 'heads', branch)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(f'{commit_sha}\n')

    # Update remote tracking ref
    remote_ref_path = os.path.join(git_dir, 'refs', 'remotes', 'origin', branch)
    os.makedirs(os.path.dirname(remote_ref_path), exist_ok=True)
    with open(remote_ref_path, 'w') as f:
        f.write(f'{commit_sha}\n')

    # Update ORIG_HEAD
    with open(os.path.join(git_dir, 'ORIG_HEAD'), 'w') as f:
        f.write(f'{commit_sha}\n')


def pull_repository(repo_path=None):
    """Pull updates from remote repository, overwriting local changes."""

    # Default to current directory
    if repo_path is None:
        repo_path = os.getcwd()

    repo_path = os.path.abspath(repo_path)

    # Check if this is a git repository
    if not os.path.exists(os.path.join(repo_path, '.git')):
        print(f"Error: '{repo_path}' is not a Git repository")
        return False

    # Read repository configuration
    url, owner, repo, branch = read_git_config(repo_path)

    if not owner or not repo:
        print("Error: Could not read remote origin from .git/config")
        print("Currently only GitHub repositories are supported")
        return False

    print(f"Pulling {owner}/{repo} (branch: {branch})...")

    # Get local and remote commit SHAs
    local_sha = get_local_commit_sha(repo_path, branch)
    remote_sha = get_remote_commit_sha(owner, repo, branch)

    if not remote_sha:
        print("Error: Could not get remote commit SHA")
        return False

    if local_sha:
        print(f"Local:  {local_sha[:8]}...")
    print(f"Remote: {remote_sha[:8]}...")

    # Check if already up to date
    if local_sha == remote_sha:
        print("Already up to date.")
        return True

    # Get remote file tree
    print("Fetching remote file tree...")
    tree = get_tree_recursive(owner, repo, branch)

    if not tree:
        print("Error: Could not retrieve repository contents")
        return False

    # Build set of remote files
    remote_files = set()
    for item in tree:
        if item['type'] == 'blob':
            remote_files.add(item['path'])

    # Get local files
    local_files = get_local_files(repo_path)

    # Find files to delete (exist locally but not in remote)
    files_to_delete = local_files - remote_files

    # Delete files that no longer exist in remote
    deleted_count = 0
    for rel_path in files_to_delete:
        file_path = os.path.join(repo_path, rel_path.replace('/', os.sep))
        try:
            os.remove(file_path)
            deleted_count += 1
        except OSError:
            pass

    if deleted_count > 0:
        print(f"Deleted {deleted_count} files no longer in remote")

    # Clean up empty directories
    for root, dirs, files in os.walk(repo_path, topdown=False):
        if '.git' in root:
            continue
        for dir_name in dirs:
            if dir_name == '.git':
                continue
            dir_path = os.path.join(root, dir_name)
            try:
                os.rmdir(dir_path)
            except OSError:
                pass  # Directory not empty

    # Download all files from remote (overwriting local)
    total_files = len([item for item in tree if item['type'] == 'blob'])
    downloaded = 0
    updated = 0

    print(f"Downloading {total_files} files...")

    for item in tree:
        path = item['path']
        item_type = item['type']

        if item_type == 'tree':
            # Create directory
            dir_path = os.path.join(repo_path, path.replace('/', os.sep))
            os.makedirs(dir_path, exist_ok=True)

        elif item_type == 'blob':
            # Download file
            file_path = os.path.join(repo_path, path.replace('/', os.sep))
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{urllib.parse.quote(path)}"

            if download_file(raw_url, file_path):
                downloaded += 1
                updated += 1
                if downloaded % 10 == 0 or downloaded == total_files:
                    print(f"Progress: {downloaded}/{total_files} files")

    # Update refs
    update_refs(repo_path, branch, remote_sha)

    print(f"\nSuccessfully pulled {owner}/{repo}")
    print(f"Updated: {local_sha[:8] if local_sha else 'none'}..{remote_sha[:8]}")
    print(f"Files updated: {updated}")
    if deleted_count > 0:
        print(f"Files deleted: {deleted_count}")

    return True


def main():
    """Main entry point."""
    repo_path = None

    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python PyGitPull.py [repository-path]")
            print("\nPulls updates from remote GitHub repository.")
            print("Remote is authoritative - local changes are overwritten.")
            print("\nIf no path is specified, uses current directory.")
            print("\nExamples:")
            print("  python PyGitPull.py")
            print("  python PyGitPull.py ./my-repo")
            sys.exit(0)
        repo_path = sys.argv[1]

    success = pull_repository(repo_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
