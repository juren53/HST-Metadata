## PyGit - a Python Git cloning program

The following creates a Python script that clones a Git repository without requiring Git to be installed. This will use HTTP/HTTPS to fetch the repository data directly.I've created a Python script that clones Git repositories without requiring Git to be installed. Here's what it does:

**Features:**
- Clones GitHub repositories using only Python's standard library
- Downloads all files and recreates the directory structure
- Shows progress during download
- Handles both HTTPS and SSH-style GitHub URLs
- Automatically detects the default branch

**Usage:**
```bash
python git_clone.py https://github.com/owner/repo
python git_clone.py https://github.com/owner/repo my-custom-folder
```

**How it works:**
1. Parses the GitHub URL to extract owner/repo
2. Uses GitHub's API to get the repository tree
3. Downloads each file individually using raw.githubusercontent.com
4. Recreates the complete directory structure locally

**Limitations:**
- Currently only supports GitHub (most common use case)
- Downloads files from the default branch only
- Doesn't include Git history or .git folder (just the current files)
- May be slower for very large repositories compared to Git

This is perfect for situations where you need repository files but can't or don't want to install Git, such as in portable Python environments or restricted systems.