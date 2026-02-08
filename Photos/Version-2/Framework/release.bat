@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  HPM Release Script
echo ============================================
echo.

REM --- Step 1: Read version from __init__.py ---
for /f "tokens=2 delims==" %%a in ('findstr /R "__version__ =" __init__.py') do (
    set "RAW=%%a"
)
REM Trim quotes and spaces
set "VERSION=%RAW: =%"
set "VERSION=%VERSION:"=%"
echo [1/7] Version detected: v%VERSION%
echo.

REM --- Step 2: Check for uncommitted changes ---
echo [2/7] Checking for uncommitted changes...
git diff --quiet 2>nul
if errorlevel 1 (
    echo WARNING: You have uncommitted changes!
    echo Commit or stash them before releasing.
    echo.
    git status --short
    echo.
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "!CONTINUE!"=="y" (
        echo Aborted.
        exit /b 1
    )
)
echo       Working tree is clean.
echo.

REM --- Step 3: Push latest commits ---
echo [3/7] Pushing latest commits to GitHub...
git push origin master
echo.

REM --- Step 4: Build the executable ---
echo [4/7] Building executable with PyInstaller...
if exist build rmdir /s /q build
if exist dist\HPM.exe del /f dist\HPM.exe
pyinstaller --clean HPM.spec
if not exist dist\HPM.exe (
    echo ERROR: Build failed! dist\HPM.exe not found.
    exit /b 1
)
echo       Build successful.
echo.

REM --- Step 5: Create git tag ---
echo [5/7] Creating git tag v%VERSION%...
git tag -a v%VERSION% -m "Release v%VERSION%"
if errorlevel 1 (
    echo WARNING: Tag v%VERSION% may already exist.
    set /p OVERWRITE="Delete and recreate tag? (y/N): "
    if /i "!OVERWRITE!"=="y" (
        git tag -d v%VERSION%
        git push origin :refs/tags/v%VERSION%
        git tag -a v%VERSION% -m "Release v%VERSION%"
    ) else (
        echo Continuing with existing tag...
    )
)
git push origin v%VERSION%
echo.

REM --- Step 6: Extract changelog and create GitHub Release ---
echo [6/7] Creating GitHub Release with binary...

REM Extract changelog section for this version into a temp file
set "FOUND=0"
(for /f "usebackq delims=" %%L in ("CHANGELOG.md") do (
    set "LINE=%%L"
    if !FOUND!==1 (
        echo !LINE! | findstr /R "^## " >nul && goto :done_changelog
        echo %%L
    )
    echo !LINE! | findstr /C:"[%VERSION%]" >nul && set "FOUND=1"
)) > release_notes_temp.md
:done_changelog

REM Create the release
gh release create v%VERSION% ^
    --title "HPM v%VERSION%" ^
    --notes-file release_notes_temp.md ^
    dist\HPM.exe

del release_notes_temp.md 2>nul
echo.

REM --- Step 7: Deploy to local bin ---
echo [7/7] Deploying to ~\bin\HPM.exe...
copy /y dist\HPM.exe "%USERPROFILE%\bin\HPM.exe"
echo.

echo ============================================
echo  Release v%VERSION% complete!
echo ============================================
echo.
echo  Tag:     v%VERSION%
echo  Release: https://github.com/juren53/HST-Metadata/releases/tag/v%VERSION%
echo  Binary:  %USERPROFILE%\bin\HPM.exe
echo.
pause
