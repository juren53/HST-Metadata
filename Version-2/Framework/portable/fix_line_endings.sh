#!/bin/bash
# ==============================================================
# Fix Line Endings for Windows Scripts
# Converts LF (Unix) to CRLF (Windows) for .bat and .ps1 files
# ==============================================================

echo "========================================"
echo "Windows Line Ending Fixer"
echo "========================================"
echo

# Check if unix2dos is installed
if ! command -v unix2dos &> /dev/null; then
    echo "ERROR: unix2dos is not installed"
    echo
    echo "Install with:"
    echo "  sudo apt install dos2unix"
    echo
    exit 1
fi

# Find all .bat and .ps1 files
BAT_FILES=($(find . -name "*.bat" -type f 2>/dev/null))
PS1_FILES=($(find . -name "*.ps1" -type f 2>/dev/null))

TOTAL_FILES=$((${#BAT_FILES[@]} + ${#PS1_FILES[@]}))

if [ $TOTAL_FILES -eq 0 ]; then
    echo "No Windows script files found in current directory"
    exit 0
fi

echo "Found $TOTAL_FILES Windows script file(s)"
echo

FIXED=0
ALREADY_OK=0

# Process each file
for file in "${BAT_FILES[@]}" "${PS1_FILES[@]}"; do
    FILE_INFO=$(file "$file")

    if echo "$FILE_INFO" | grep -q "CRLF"; then
        echo "✓ $file - Already has CRLF endings"
        ((ALREADY_OK++))
    else
        echo "→ $file - Converting to CRLF..."
        unix2dos "$file" 2>&1
        if [ $? -eq 0 ]; then
            echo "  ✓ Fixed"
            ((FIXED++))
        else
            echo "  ✗ Failed to convert"
        fi
    fi
done

echo
echo "========================================"
echo "Summary"
echo "========================================"
echo "Fixed: $FIXED file(s)"
echo "Already correct: $ALREADY_OK file(s)"
echo
echo "Your Windows scripts are ready for deployment!"
