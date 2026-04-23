#!/usr/bin/env python3
"""
Git Clone without Git - A pure Python implementation
Clones a Git repository using HTTP/HTTPS without requiring Git installation.
"""

import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import json
import zlib
import hashlib
from pathlib import Path


def parse_git_url(url):
    """Parse Git URL and return the API-compatible URL."""
    url = url.strip()
    
    # Remove .git suffix if present
    if url.endswith('.git'):
        url = url[:-4]
    
    # Handle GitHub URLs
    if 'github.com' in url:
        # Convert SSH to HTTPS
        if url.startswith('git@github.com:'):
            url = url.replace('git@github.com:', 'https://github.com/')
        
        # Extract owner and repo
        parts = url.split('github.com/')[-1].split('/')
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            return f"https://api.github.com/repos/{owner}/{repo}", owner, repo
    
    return None, None, None


def get_default_branch(api_url):
    """Get the default branch of the repository."""
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            return data.get('default_branch', 'main')
    except Exception as e:
        print(f"Error getting default branch: {e}")
        return 'main'


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


def get_tree_recursive(api_url, owner, repo, branch):
    """Get the complete file tree recursively."""
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        with urllib.request.urlopen(tree_url) as response:
            data = json.loads(response.read().decode())
            return data.get('tree', [])
    except Exception as e:
        print(f"Error getting repository tree: {e}")
        return []


def get_branch_commit_sha(owner, repo, branch):
    """Get the commit SHA for a branch."""
    ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}"
    try:
        with urllib.request.urlopen(ref_url) as response:
            data = json.loads(response.read().decode())
            return data.get('object', {}).get('sha')
    except Exception as e:
        print(f"Error getting branch commit SHA: {e}")
        return None


def init_git_directory(destination, url, owner, repo, branch, commit_sha):
    """Initialize a proper .git directory structure."""
    git_dir = os.path.join(destination, '.git')

    # Create .git directory structure
    os.makedirs(git_dir, exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'objects', 'info'), exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'objects', 'pack'), exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'refs', 'heads'), exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'refs', 'remotes', 'origin'), exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'refs', 'tags'), exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'info'), exist_ok=True)
    os.makedirs(os.path.join(git_dir, 'hooks'), exist_ok=True)

    # Create HEAD file
    with open(os.path.join(git_dir, 'HEAD'), 'w') as f:
        f.write(f'ref: refs/heads/{branch}\n')

    # Create config file
    # Reconstruct the original clone URL
    clone_url = f"https://github.com/{owner}/{repo}.git"
    config_content = f"""[core]
\trepositoryformatversion = 0
\tfilemode = false
\tbare = false
\tlogallrefupdates = true
\tsymlinks = false
\tignorecase = true
[remote "origin"]
\turl = {clone_url}
\tfetch = +refs/heads/*:refs/remotes/origin/*
[branch "{branch}"]
\tremote = origin
\tmerge = refs/heads/{branch}
"""
    with open(os.path.join(git_dir, 'config'), 'w') as f:
        f.write(config_content)

    # Create description file
    with open(os.path.join(git_dir, 'description'), 'w') as f:
        f.write('Unnamed repository; edit this file to name the repository.\n')

    # Create info/exclude file
    with open(os.path.join(git_dir, 'info', 'exclude'), 'w') as f:
        f.write('# git ls-files --others --exclude-from=.git/info/exclude\n')

    # Write commit SHA to refs
    if commit_sha:
        # Local branch ref
        with open(os.path.join(git_dir, 'refs', 'heads', branch), 'w') as f:
            f.write(f'{commit_sha}\n')

        # Remote tracking ref
        with open(os.path.join(git_dir, 'refs', 'remotes', 'origin', branch), 'w') as f:
            f.write(f'{commit_sha}\n')

        # Create ORIG_HEAD
        with open(os.path.join(git_dir, 'ORIG_HEAD'), 'w') as f:
            f.write(f'{commit_sha}\n')

    print(f"Initialized .git directory")


def clone_repository(url, destination=None):
    """Clone a Git repository without Git installed."""
    
    # Parse the URL
    api_url, owner, repo = parse_git_url(url)
    
    if not api_url:
        print("Error: Currently only GitHub repositories are supported")
        print("Example: https://github.com/owner/repo")
        return False
    
    # Set destination directory
    if destination is None:
        destination = repo
    
    destination = os.path.abspath(destination)
    
    # Check if destination exists
    if os.path.exists(destination):
        print(f"Error: Destination '{destination}' already exists")
        return False
    
    print(f"Cloning {owner}/{repo} into {destination}...")
    
    # Get default branch
    branch = get_default_branch(api_url)
    print(f"Using branch: {branch}")

    # Get the commit SHA for the branch
    commit_sha = get_branch_commit_sha(owner, repo, branch)
    if commit_sha:
        print(f"Commit: {commit_sha[:8]}...")

    # Get the complete file tree
    tree = get_tree_recursive(api_url, owner, repo, branch)

    if not tree:
        print("Error: Could not retrieve repository contents")
        return False

    # Create base directory
    os.makedirs(destination, exist_ok=True)

    # Initialize .git directory for proper Git integration
    init_git_directory(destination, url, owner, repo, branch, commit_sha)
    
    # Download all files
    total_files = len([item for item in tree if item['type'] == 'blob'])
    downloaded = 0
    
    for item in tree:
        path = item['path']
        item_type = item['type']
        
        if item_type == 'tree':
            # Create directory
            dir_path = os.path.join(destination, path)
            os.makedirs(dir_path, exist_ok=True)
        
        elif item_type == 'blob':
            # Download file
            file_path = os.path.join(destination, path)
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{urllib.parse.quote(path)}"
            
            if download_file(raw_url, file_path):
                downloaded += 1
                if downloaded % 10 == 0 or downloaded == total_files:
                    print(f"Progress: {downloaded}/{total_files} files downloaded")
    
    print(f"\nSuccessfully cloned {owner}/{repo} to {destination}")
    print(f"Total files: {downloaded}")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python git_clone.py <repository-url> [destination]")
        print("\nExample:")
        print("  python git_clone.py https://github.com/owner/repo")
        print("  python git_clone.py https://github.com/owner/repo my-folder")
        sys.exit(1)
    
    url = sys.argv[1]
    destination = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = clone_repository(url, destination)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
