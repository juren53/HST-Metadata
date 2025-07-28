# analyze_utf8.py - Documentation

## Overview

The `analyze_utf8.py` script is a Python utility designed to analyze CSV files and identify special characters (non-ASCII) that might indicate encoding issues or international text content. It provides detailed reporting on the location and nature of these characters.

## Purpose

This script helps identify:
- **Mojibake patterns** - Corrupted text from encoding mismatches
- **International characters** - Legitimate accented letters, umlauts, etc.
- **Encoding issues** - Characters that appear in wrong contexts
- **Unicode problems** - Unusual or high-code-point characters

## How It Works

### 1. Main Entry Point (`main()` function)

```python
def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "export.csv"
    
    analyze_csv_file(filename)
```

- **Command-line argument handling**: Accepts a filename as the first argument
- **Default behavior**: If no filename provided, defaults to "export.csv"
- **Simple interface**: Just calls the main analysis function

### 2. Core Analysis (`analyze_csv_file()` function)

This is the heart of the script that:

#### Step 1: File Reading Strategy
```python
# Try to read as UTF-8 first
with open(filename, 'r', encoding='utf-8', errors='replace') as file:
    lines = file.readlines()
```

- **Primary approach**: Attempts UTF-8 encoding first (most common)
- **Error handling**: Uses `errors='replace'` to substitute problematic characters with `�`
- **Fallback encodings**: If UTF-8 fails, tries `latin1`, `cp1252`, `iso-8859-1`

#### Step 2: Line-by-Line Analysis
```python
for line_num, line in enumerate(lines, 1):
    line = line.rstrip('\n\r')  # Remove line endings
    suspicious_chars = find_non_utf8_chars(line)
```

- **Iterates through each line** with line numbers starting at 1
- **Cleans line endings** to avoid false positives
- **Calls detection function** for each line

#### Step 3: Results Reporting
For each line with special characters:
- Reports line number and count of special characters
- Shows highlighted version of the line content
- Lists detailed information about each character

### 3. Character Detection (`find_non_utf8_chars()` function)

This function implements the core logic for identifying special characters:

```python
def find_non_utf8_chars(text):
    suspicious_chars = []
    
    for i, char in enumerate(text):
        # Look for common mojibake patterns
        if char in ['À', 'Ã', 'â', '€', '™', 'š', 'œ', 'ž', 'Ÿ', ...]:
            suspicious_chars.append((i, char, ord(char)))
        # Look for high-bit characters that might be mojibake
        elif ord(char) > 127 and ord(char) < 256:
            suspicious_chars.append((i, char, ord(char)))
        # Look for unusual Unicode characters that might be encoding issues
        elif ord(char) > 8000:  # Arbitrary threshold for "unusual" Unicode
            suspicious_chars.append((i, char, ord(char)))
    
    return suspicious_chars
```

#### Detection Categories:

1. **Common Mojibake Patterns** (lines 20-21)
   - Predefined list of characters that often appear in corrupted text
   - Examples: `À`, `Ã`, `â`, `€`, `™`, etc.
   - These often result from Windows-1252 → UTF-8 encoding mistakes

2. **High-bit Characters** (lines 23-24)
   - Characters with Unicode values between 128-255
   - Includes accented letters, symbols, extended ASCII
   - Examples: `é`, `ñ`, `ü`, `ß`, etc.

3. **Unusual Unicode Characters** (lines 26-27)
   - Characters with Unicode values > 8000
   - Arbitrary threshold to catch exotic Unicode symbols
   - Examples: Various special symbols, mathematical notation, etc.

#### Return Format:
Returns a list of tuples: `(position, character, unicode_value)`

### 4. Visual Highlighting (`highlight_suspicious_chars()` function)

This function provides visual feedback by highlighting special characters:

```python
def highlight_suspicious_chars(text, suspicious_chars):
    # Check if output is being redirected to a file
    if not sys.stdout.isatty():  # Output is being redirected
        # Use ASCII-safe brackets for file output
        HIGHLIGHT_START = '['
        HIGHLIGHT_END = ']'
    else:
        # Use fancy arrows for terminal output
        HIGHLIGHT_START = '►'
        HIGHLIGHT_END = '◄'
```

#### Smart Output Formatting:
- **Terminal display**: Uses arrow symbols (`►char◄`) for visual appeal
- **File redirection**: Uses ASCII brackets (`[char]`) to avoid encoding issues
- **Detection method**: Uses `sys.stdout.isatty()` to detect redirection

#### Highlighting Process:
1. **Creates character list** from the input text
2. **Sorts positions in reverse order** to avoid index shifting when inserting markers
3. **Wraps each special character** with highlight markers
4. **Rejoins into string** and returns highlighted text

### 5. Utility Function (`is_ascii_printable()`)

```python
def is_ascii_printable(char):
    return 32 <= ord(char) <= 126
```

- **ASCII range check**: Characters from space (32) to tilde (126)
- **Currently unused**: Present but not actively used in current version
- **Future expansion**: Could be used for stricter ASCII-only detection

## Output Format

### Terminal Output Example:
```
Line 22: Found 5 special character(s)
Content: "Spanish Example Title, El Valle de los Ca►í◄dos"
Special characters:
  Position 42: 'í' (Unicode: U+00ED, Decimal: 237)
----------------------------------------
```

### File Output Example:
```
Line 22: Found 5 special character(s)
Content: "Spanish Example Title, El Valle de los Ca[í]dos"
Special characters:
  Position 42: 'í' (Unicode: U+00ED, Decimal: 237)
----------------------------------------
```

## Usage Examples

### Basic Usage (default file):
```bash
python analyze_utf8.py
```

### Analyze specific file:
```bash
python analyze_utf8.py data.csv
```

### Save results to file:
```bash
python analyze_utf8.py data.csv > results.txt
```

### Analyze file in different directory:
```bash
python analyze_utf8.py ../testing-data/Test-6-Files/export.csv
```

## Error Handling

The script includes comprehensive error handling:

1. **File not found**: Clear error message if file doesn't exist
2. **Encoding errors**: Automatic fallback to alternative encodings
3. **Unicode display issues**: Smart detection of output redirection
4. **General exceptions**: Catches and reports unexpected errors

## Technical Details

### Dependencies:
- **sys**: Command-line arguments and output detection
- **csv**: Imported but not actively used (legacy)
- **re**: Imported but not actively used (legacy)

### Character Encoding Support:
- **Primary**: UTF-8 (most common modern encoding)
- **Fallbacks**: latin1, cp1252 (Windows-1252), iso-8859-1
- **Error handling**: Replaces undecodable characters with `�`

### Performance Considerations:
- **Line-by-line processing**: Memory efficient for large files
- **Character-by-character analysis**: Thorough but may be slow on very large files
- **No external dependencies**: Uses only Python standard library

## Limitations

1. **Subjective detection**: What constitutes "special" vs "suspicious" is somewhat arbitrary
2. **False positives**: Legitimate international text gets flagged as "special"
3. **Hardcoded patterns**: Mojibake detection relies on predefined character lists
4. **No auto-correction**: Only identifies issues, doesn't fix them automatically

## Future Enhancements

Potential improvements could include:
- **Configurable sensitivity**: Allow users to adjust detection thresholds
- **Language detection**: Distinguish between legitimate international text and mojibake
- **Auto-correction suggestions**: Propose fixes for detected encoding issues
- **Statistical analysis**: Report character frequency and distribution
- **Export formats**: Support JSON, XML, or other structured output formats

## Companion Scripts

This script works well with:
- **fix_encoding.py**: Attempts to automatically correct mojibake patterns
- **CSV processing tools**: For bulk data cleaning operations
- **Text analysis pipelines**: As part of data quality assessment workflows
