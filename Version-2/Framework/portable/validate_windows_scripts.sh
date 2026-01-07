#!/bin/bash
# ==============================================================
# Windows Script Validator
# Checks .bat and .ps1 files for common issues before deployment
# ==============================================================

echo "========================================"
echo "Windows Script Validator"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check line endings
check_line_endings() {
    local file=$1
    local file_info=$(file "$file")

    if echo "$file_info" | grep -q "CRLF"; then
        echo -e "${GREEN}✓${NC} Correct line endings (CRLF)"
        return 0
    elif echo "$file_info" | grep -q "LF"; then
        echo -e "${RED}✗${NC} WRONG line endings (LF - Unix style)"
        echo "  Fix with: unix2dos \"$file\""
        ((ERRORS++))
        return 1
    else
        echo -e "${YELLOW}?${NC} Could not determine line endings"
        ((WARNINGS++))
        return 2
    fi
}

# Function to check batch file best practices
check_batch_file() {
    local file=$1
    echo
    echo "Checking: $file"
    echo "----------------------------------------"

    # Check line endings (CRITICAL)
    check_line_endings "$file"

    # Check for @echo off (best practice)
    if grep -q "^@echo off" "$file"; then
        echo -e "${GREEN}✓${NC} Uses '@echo off'"
    else
        echo -e "${YELLOW}!${NC} Missing '@echo off' at start"
        ((WARNINGS++))
    fi

    # Check for proper drive change syntax
    if grep -q "cd /d" "$file"; then
        echo -e "${GREEN}✓${NC} Uses 'cd /d' for drive changes"
    fi

    # Check for %~d0 usage (portable USB)
    if grep -q "%~d0" "$file"; then
        echo -e "${GREEN}✓${NC} Uses %~d0 for drive detection (portable)"
    fi

    # Check for hardcoded drive letters (BAD for USB)
    if grep -E "^[A-Z]:\\\\" "$file" | grep -v "REM" | grep -v "echo"; then
        echo -e "${RED}✗${NC} Contains hardcoded drive letters (not portable)"
        grep -n -E "^[A-Z]:\\\\" "$file" | grep -v "REM" | grep -v "echo"
        ((ERRORS++))
    fi

    # Check for error handling
    if grep -q "errorlevel" "$file" || grep -q "if errorlevel" "$file"; then
        echo -e "${GREEN}✓${NC} Has error handling (errorlevel checks)"
    else
        echo -e "${YELLOW}!${NC} No error handling detected"
        ((WARNINGS++))
    fi

    # Check for pause commands (good for debugging)
    if grep -q "pause" "$file"; then
        echo -e "${GREEN}✓${NC} Has pause for error viewing"
    fi
}

# Function to check PowerShell files
check_powershell_file() {
    local file=$1
    echo
    echo "Checking: $file"
    echo "----------------------------------------"

    # Check line endings
    check_line_endings "$file"

    # Check if PowerShell Core is installed for syntax checking
    if command -v pwsh &> /dev/null; then
        echo "Testing PowerShell syntax..."
        if pwsh -Command "Get-Command Test-Path" &> /dev/null; then
            echo -e "${GREEN}✓${NC} PowerShell Core available for testing"

            # Try to parse the script
            if pwsh -Command "& { \$ErrorActionPreference='Stop'; try { \$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content '$file' -Raw), [ref]\$null) } catch { exit 1 } }" &> /dev/null; then
                echo -e "${GREEN}✓${NC} PowerShell syntax appears valid"
            else
                echo -e "${RED}✗${NC} PowerShell syntax errors detected"
                ((ERRORS++))
            fi
        fi
    else
        echo -e "${YELLOW}!${NC} PowerShell Core not installed (can't verify syntax)"
        echo "  Install with: sudo apt install powershell"
        ((WARNINGS++))
    fi

    # Check for execution policy comments
    if grep -q "ExecutionPolicy" "$file"; then
        echo -e "${GREEN}✓${NC} Mentions ExecutionPolicy"
    else
        echo -e "${YELLOW}!${NC} No ExecutionPolicy guidance"
        ((WARNINGS++))
    fi
}

# Find and check all batch files
echo "Scanning for Windows scripts..."
echo

BAT_FILES=($(find . -name "*.bat" -type f 2>/dev/null))
PS1_FILES=($(find . -name "*.ps1" -type f 2>/dev/null))

if [ ${#BAT_FILES[@]} -eq 0 ] && [ ${#PS1_FILES[@]} -eq 0 ]; then
    echo "No Windows script files found in current directory"
    exit 0
fi

echo "Found ${#BAT_FILES[@]} .bat file(s) and ${#PS1_FILES[@]} .ps1 file(s)"

# Check batch files
for bat in "${BAT_FILES[@]}"; do
    check_batch_file "$bat"
done

# Check PowerShell files
for ps1 in "${PS1_FILES[@]}"; do
    check_powershell_file "$ps1"
done

# Summary
echo
echo "========================================"
echo "Summary"
echo "========================================"
echo -e "${RED}Errors: $ERRORS${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}No errors, but some warnings to review${NC}"
    exit 0
else
    echo -e "${RED}Please fix errors before deploying to Windows${NC}"
    exit 1
fi
