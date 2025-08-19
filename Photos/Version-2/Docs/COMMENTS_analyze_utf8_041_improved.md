# UTF-8 Analysis Script - Version 0.4.1 Comments

## Overview
The script has been updated to Version 0.4.1 with the following improvements:
- Prints Version 0.4.1 in the header
- Writes a timestamped report file mirroring the console output

## Report Output Location
```
C:\Users\jimur\Projects\HST-Metadata\Photo\Version-2\testing-data\Test-6-Files\REPORT_UTF8-2025-08-13_14-16-30.txt
```

## Suggestions for Refining "Special Characters" Detection

### 1. Whitelist Approach by Field
- **Title/Description fields**: Allow standard punctuation and letters with diacritics (Latin-1 supplement) but flag:
  - Control characters
  - Replacement characters
  - Private-use characters
- **Accession/ObjectName fields**: Restrict to `[A-Za-z0-9_-]` and flag everything else

### 2. Unicode Categories
Flag characters in these categories:
- **Cc** (control)
- **Cf** (format, e.g., zero-width joiner)
- **Co** (private use)
- **Cs** (surrogates)

Optionally flag **Pd/Po** characters outside a small set (only accept: `- . ; : ' " ( ) / &`)

### 3. Normalization First
- Apply Unicode normalization (NFC) and flag if normalization changes the string
- Detect decomposed vs composed sequences

### 4. Known Mojibake Patterns
- Keep current high-bit 128–255 detection
- Add checks for typical UTF-8→Windows-1252 corruption sequences
- Look for patterns like: `â€™`, `Ã©`, etc., as multi-character patterns

### 5. Zero-width and Whitespace Characters
Explicitly flag these characters:
- **ZERO WIDTH SPACE** (U+200B)
- **NO-BREAK SPACE** (U+00A0)
- **EM/EN SPACE** (U+2002–U+2003)
- Other **U+2000–U+200A** spaces (unless in allowed list)

### 6. Smart Quotes and Dashes
Decide policy: either allow `" " ' ' – —` or auto-normalize them to ASCII equivalents and report.

### 7. Confusable/Spoofing Characters
Optionally flag characters outside Latin scripts (Greek, Cyrillic) that visually resemble Latin letters in fields expected to be English.

### 8. Configurable Policy
Move the character policy into a config at the top with:
- Allowed ranges per column
- Easy tuning without changing code

## Implementation Options

The following features can be implemented:
- [ ] Column-aware validator with allowlists/regex per column
- [ ] Unicode normalization (NFC) with "changed by normalization" indicator
- [ ] Explicit detection of zero-width and non-breaking spaces
- [ ] Command-line switches like `--strict` or `--loose` to control sensitivity

---

## Unicode Normalization (NFC) - Technical Background

### What is Unicode Normalization?
Unicode normalization ensures text is represented consistently in memory, even when multiple encodings of the same characters are possible.

### Why Normalization Exists
Some Unicode characters can be represented in multiple ways:

#### Precomposed Form
A single code point for a character with an accent.
- Example: `"é"` → `U+00E9` (Latin small letter e with acute)

#### Decomposed Form
A base letter plus a separate "combining" accent mark.
- Example: `"é"` → `U+0065` (e) + `U+0301` (combining acute accent)

**Note**: Both look identical (`é`) but are different byte sequences internally.

### Unicode Normalization Forms

| Form | Name | Description |
|------|------|-------------|
| **NFC** | Normalization Form C (Canonical Composition) | Prefers the composed form when available |
| **NFD** | Normalization Form D (Canonical Decomposition) | Prefers the decomposed form |
| **NFKC** | Compatibility Composition | Like NFC, but also converts compatibility equivalents |
| **NFKD** | Compatibility Decomposition | Like NFD, but also expands compatibility forms |

### NFC Example in Python
```python
import unicodedata

s1 = "e\u0301"        # decomposed form: 'e' + combining acute
s2 = "é"              # composed form: single code point

print(s1 == s2)       # False, different binary representation

s1_nfc = unicodedata.normalize("NFC", s1)
print(s1_nfc == s2)   # True, both now NFC-composed
```

### Summary
✅ **NFC normalization** converts Unicode text into a consistent, composed form where possible, ensuring visually identical text has the same binary representation.
