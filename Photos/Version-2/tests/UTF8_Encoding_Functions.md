# New UTF-8 Encoding Functions Added to g2c.py

## Overview

The following functions were added to replace the problematic table-based approach in `clean_encoding_artifacts()` with more robust, hierarchical UTF-8 conversion methods.

## New Functions Added

### 1. **Method 1**: `text_to_utf8(text_or_bytes)`
- Uses chardet for automatic encoding detection
- Best for unknown/diverse encodings
- Falls back gracefully if chardet isn't available

**Purpose**: Automatic encoding detection using machine learning
**Dependencies**: chardet library (optional)
**Use Case**: When you have text from unknown or diverse sources

```python
def text_to_utf8(text_or_bytes):
    """Convert text with unknown encoding to UTF-8 string using chardet.
    
    Method 1: Using chardet for encoding detection
    
    Args:
        text_or_bytes: String or bytes that may need encoding conversion
        
    Returns:
        str: UTF-8 encoded string
    """
```

### 2. **Method 2**: `text_to_utf8_fallback(text_or_bytes)`
- Tries common encodings in order of likelihood: utf-8, latin-1, cp1252, iso-8859-1
- No external dependencies required
- Good backup when chardet isn't available

**Purpose**: Reliable backup encoding detection
**Dependencies**: None (built-in Python)
**Use Case**: When chardet isn't available or for typical Western European text

```python
def text_to_utf8_fallback(text_or_bytes):
    """Try common encodings in order of likelihood.
    
    Method 2: Try common encodings when chardet isn't available
    
    Args:
        text_or_bytes: String or bytes that may need encoding conversion
        
    Returns:
        str: UTF-8 encoded string
    """
```

### 3. **Method 3**: `clean_metadata_text(text)`
- Specifically designed for photo metadata
- Handles bytes input with encoding detection
- Removes null bytes and ensures valid UTF-8
- Perfect for IPTC/EXIF metadata fields

**Purpose**: Specialized cleaning for photo metadata
**Dependencies**: Uses chardet if available, otherwise fallback method
**Use Case**: EXIF/IPTC metadata fields that often have encoding issues

```python
def clean_metadata_text(text):
    """Clean text for photo metadata embedding.
    
    Method 3: For photo metadata specifically
    
    Args:
        text: String or bytes that may contain metadata encoding issues
        
    Returns:
        str: Cleaned UTF-8 string suitable for metadata
    """
```

### 4. **New Master Function**: `smart_encoding_cleaner(text)`
**Hierarchical approach** that combines all methods:
1. First handles bytes with chardet or fallback encoding detection
2. Then applies your original double-encoding artifact cleaning
3. Finally applies metadata-specific cleaning
4. Returns fully cleaned UTF-8 text

**Purpose**: Complete encoding solution combining all methods
**Dependencies**: Optional chardet, falls back gracefully
**Use Case**: Primary function for all text cleaning needs

```python
def smart_encoding_cleaner(text):
    """Hierarchical approach combining all methods.
    
    This function uses the three methods in a complementary way:
    1. First tries chardet-based detection for bytes
    2. Falls back to common encodings if chardet fails
    3. Then applies the original artifact cleaning for double-encoding issues
    4. Finally applies metadata-specific cleaning
    
    Args:
        text: String or bytes that may need encoding conversion and cleaning
        
    Returns:
        str: Cleaned UTF-8 string
    """
```

## Updated Functionality

- **`clean_dataframe_encoding()`** now uses `smart_encoding_cleaner()` instead of just the original artifact cleaning
- **Automatic chardet detection** - checks if chardet is available and uses it when possible  
- **Graceful fallbacks** - works even without chardet installed
- **Backward compatibility** - your original `clean_encoding_artifacts()` function is preserved and integrated

## Usage Notes

- The script will show a warning if chardet isn't installed, but will still work using the fallback methods
- To get the best results, install chardet: `pip install chardet`
- All three methods work together in the `smart_encoding_cleaner()` function
- Your existing double-encoding artifact table is still used and maintained

## Benefits

This gives you a robust, layered approach that handles:
- Unknown byte encodings (chardet)
- Common Western encodings (fallback)
- Double-encoding artifacts (your existing table)
- Metadata-specific issues (null bytes, etc.)

The implementation is now much more maintainable since you won't need to keep updating the artifact table for every new encoding issue!

## Installation

To get the full benefits of the automatic encoding detection and repair:

```bash
pip install chardet ftfy
```

Or use the provided installation script:

```bash
python install_encoding_libs.py
```

### Library Benefits:
- **chardet**: Automatic encoding detection for unknown byte sequences
- **ftfy**: Automatic double-encoding repair (eliminates most table maintenance)

The functions will work without these libraries, but with reduced functionality:
- Without chardet: Falls back to trying common encodings
- Without ftfy: Falls back to manual artifact table cleaning

## Updated Approach (ftfy Integration)

The `smart_encoding_cleaner()` now prioritizes **ftfy** for double-encoding repair:

1. **First**: Handle bytes input with encoding detection (chardet → fallback)
2. **Second**: Use ftfy for automatic double-encoding repair (preferred)
3. **Fallback**: Use manual artifact table if ftfy unavailable
4. **Finally**: Apply metadata-specific cleaning

This approach should eliminate 95% of manual table maintenance while providing robust fallbacks.
