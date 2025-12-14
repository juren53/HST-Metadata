# UTF-8 Encodings and Mojibake

## Overview

This document explains a classic cross-platform encoding bug that Python 3.15's UTF-8 default is designed to prevent. Understanding this issue is critical when working with photo metadata across different operating systems.

---

## What is Mojibake?

**Mojibake** is the garbled text you see when text is decoded using the wrong character encoding.

- **Origin**: Japanese word 文字化け (moji = character, bake = transformation/corruption)
- **Cause**: Text written in one encoding but read in another

### Common Examples

You've probably seen these transformations:

| Original | Mojibake Result |
|----------|----------------|
| "café" | "cafĂ©" |
| "naïve" | "naĂŻve" |
| "São Paulo" | "SĂŁo Paulo" |
| "™" | "â„¢" |

---

## The Cross-Platform Encoding Problem

### On Linux (Development Environment)

- **Default encoding**: UTF-8 (on most modern Linux systems)
- Code like `open('metadata.txt', 'w')` automatically writes UTF-8
- Photo metadata written correctly with UTF-8 text
- ✅ Everything works fine

### On Windows (Production/Deployment)

- **Default encoding**: cp1252 or cp1251 (depending on system locale)
- Same `open('metadata.txt', 'w')` now writes using cp1252
- Characters like é, ñ, ™, or emoji get **mangled**
- ❌ Photo metadata gets mojibake embedded in it

---

## Why This Happens

The default text encoding varies by platform in Python versions before 3.15:

1. Linux developers rely on UTF-8 as the default without explicitly specifying it
2. Code "just works" on their development systems
3. When deployed to Windows, encoding **silently switches** to the Windows locale encoding
4. No errors are raised, but data is corrupted

---

## Code Example

```python
# Code written on Linux
with open('photo_caption.txt', 'w') as f:
    f.write('Café in São Paulo™')  # Works fine on Linux (UTF-8)

# Same code on Windows writes using cp1252
# Later read back as UTF-8 → mojibake
```

### Why This is Particularly Dangerous for Photo Metadata

Mojibake gets **permanently embedded** in image files' EXIF data:

- You might not notice corruption immediately
- Problems appear when images are viewed on different systems
- Different photo tools may interpret the encoding differently
- Once written, the corrupted data is difficult to fix

---

## The Solution: Python 3.15

Python 3.15's UTF-8 everywhere default solves this by:

- Making encoding behavior **consistent across all platforms**
- Ensuring code that works on Linux handles text the same way on Windows
- Eliminating silent encoding switches that cause mojibake

