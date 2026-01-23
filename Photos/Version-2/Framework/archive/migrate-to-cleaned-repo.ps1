# HST-Metadata Repository Migration Script
# This script helps migrate from the old (large) repository to the cleaned version
# Run this script on any system that has the old clone with TIFF files

param(
    [Parameter(Mandatory=$false)]
    [string]$RepoPath = "C:\Users\$env:USERNAME\Projects\HST-Metadata",
    
    [Parameter(Mandatory=$false)]
    [switch]$FreshClone = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HST-Metadata Repository Migration Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if repo exists
if (-not (Test-Path $RepoPath)) {
    Write-Host "Repository not found at: $RepoPath" -ForegroundColor Red
    Write-Host "Please specify the correct path using -RepoPath parameter" -ForegroundColor Yellow
    exit 1
}

# Check if it's a git repo
if (-not (Test-Path "$RepoPath\.git")) {
    Write-Host "Not a git repository: $RepoPath" -ForegroundColor Red
    exit 1
}

Write-Host "Repository found: $RepoPath" -ForegroundColor Green
Write-Host ""

# Show current size
Write-Host "Calculating current repository size..." -ForegroundColor Yellow
$currentSize = (Get-ChildItem "$RepoPath\.git" -Recurse -File | Measure-Object -Property Length -Sum).Sum
$currentSizeMB = [math]::Round($currentSize / 1MB, 2)
Write-Host "Current .git size: $currentSizeMB MB" -ForegroundColor White
Write-Host ""

# Check for uncommitted changes
Push-Location $RepoPath
$status = git status --short
Pop-Location

if ($status) {
    Write-Host "WARNING: You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $status -ForegroundColor Gray
    Write-Host ""
    
    $backup = Read-Host "Would you like to create a backup of uncommitted changes? (Y/N)"
    if ($backup -eq 'Y' -or $backup -eq 'y') {
        $backupDir = "$RepoPath-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Host "Creating backup at: $backupDir" -ForegroundColor Yellow
        Copy-Item -Path $RepoPath -Destination $backupDir -Recurse -Force
        Write-Host "Backup created successfully!" -ForegroundColor Green
        Write-Host ""
    }
}

# Ask for migration method
Write-Host "Choose migration method:" -ForegroundColor Cyan
Write-Host "1. Fresh Clone (Recommended - cleanest, creates new directory)" -ForegroundColor White
Write-Host "2. Force Reset (Updates existing directory, faster)" -ForegroundColor White
Write-Host ""

if (-not $FreshClone) {
    $choice = Read-Host "Enter your choice (1 or 2)"
} else {
    $choice = "1"
}

if ($choice -eq "1") {
    # Fresh Clone Method
    Write-Host ""
    Write-Host "=== Fresh Clone Method ===" -ForegroundColor Cyan
    Write-Host ""
    
    $parentDir = Split-Path $RepoPath -Parent
    $repoName = Split-Path $RepoPath -Leaf
    $newRepoPath = "$parentDir\$repoName-cleaned-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    Write-Host "This will:" -ForegroundColor Yellow
    Write-Host "  1. Clone the cleaned repository to: $newRepoPath" -ForegroundColor Gray
    Write-Host "  2. Keep your old repository at: $RepoPath" -ForegroundColor Gray
    Write-Host "  3. You can delete the old one after verifying the new one works" -ForegroundColor Gray
    Write-Host ""
    
    $confirm = Read-Host "Continue? (Y/N)"
    if ($confirm -ne 'Y' -and $confirm -ne 'y') {
        Write-Host "Migration cancelled." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host ""
    Write-Host "Cloning cleaned repository..." -ForegroundColor Yellow
    Push-Location $parentDir
    git clone https://github.com/juren53/HST-Metadata.git $newRepoPath
    $cloneSuccess = $LASTEXITCODE -eq 0
    Pop-Location
    
    if ($cloneSuccess) {
        Write-Host ""
        Write-Host "SUCCESS! Migration complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "New repository location: $newRepoPath" -ForegroundColor Cyan
        
        $newSize = (Get-ChildItem "$newRepoPath\.git" -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $newSizeMB = [math]::Round($newSize / 1MB, 2)
        $savedMB = [math]::Round($currentSizeMB - $newSizeMB, 2)
        
        Write-Host "New .git size: $newSizeMB MB (saved $savedMB MB)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Verify the new repository works correctly" -ForegroundColor Gray
        Write-Host "  2. Move any uncommitted work from old to new repo if needed" -ForegroundColor Gray
        Write-Host "  3. Delete the old repository: Remove-Item -Recurse -Force '$RepoPath'" -ForegroundColor Gray
        Write-Host "  4. Optionally rename new repo: Rename-Item '$newRepoPath' '$repoName'" -ForegroundColor Gray
    } else {
        Write-Host "ERROR: Clone failed!" -ForegroundColor Red
        exit 1
    }
    
} elseif ($choice -eq "2") {
    # Force Reset Method
    Write-Host ""
    Write-Host "=== Force Reset Method ===" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "WARNING: This will:" -ForegroundColor Red
    Write-Host "  1. Delete ALL uncommitted changes" -ForegroundColor Gray
    Write-Host "  2. Reset to match the cleaned GitHub repository" -ForegroundColor Gray
    Write-Host "  3. Remove all untracked files" -ForegroundColor Gray
    Write-Host ""
    
    $confirm = Read-Host "Are you SURE you want to continue? Type 'YES' to confirm"
    if ($confirm -ne 'YES') {
        Write-Host "Migration cancelled." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host ""
    Write-Host "Fetching cleaned repository from GitHub..." -ForegroundColor Yellow
    Push-Location $RepoPath
    
    git fetch origin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to fetch from origin!" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "Resetting to origin/master..." -ForegroundColor Yellow
    git reset --hard origin/master
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to reset!" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "Cleaning untracked files..." -ForegroundColor Yellow
    git clean -fdx
    
    Write-Host "Running garbage collection..." -ForegroundColor Yellow
    git reflog expire --expire=now --all
    git gc --aggressive --prune=now
    
    Pop-Location
    
    Write-Host ""
    Write-Host "SUCCESS! Migration complete!" -ForegroundColor Green
    Write-Host ""
    
    $newSize = (Get-ChildItem "$RepoPath\.git" -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $newSizeMB = [math]::Round($newSize / 1MB, 2)
    $savedMB = [math]::Round($currentSizeMB - $newSizeMB, 2)
    
    Write-Host "New .git size: $newSizeMB MB (saved $savedMB MB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository has been updated to the cleaned version!" -ForegroundColor Cyan
    
} else {
    Write-Host "Invalid choice. Migration cancelled." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
