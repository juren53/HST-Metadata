## How to convert non-ASCII characters to UTF-8 in Python 

## Method 1: Using chardet for encoding detection

```python
import chardet

def text_to_utf8(text_or_bytes):
    """Convert text with unknown encoding to UTF-8 string"""
    if isinstance(text_or_bytes, str):
        # Already a Unicode string, just return it
        return text_or_bytes
    
    # Detect encoding for bytes
    detected = chardet.detect(text_or_bytes)
    encoding = detected['encoding']
    
    if encoding:
        return text_or_bytes.decode(encoding)
    else:
        # Fallback to UTF-8 with error handling
        return text_or_bytes.decode('utf-8', errors='replace')
```

## Method 2: Try common encodings

```python
def text_to_utf8_fallback(text_or_bytes):
    """Try common encodings in order of likelihood"""
    if isinstance(text_or_bytes, str):
        return text_or_bytes
    
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            return text_or_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Last resort - decode with replacement characters
    return text_or_bytes.decode('utf-8', errors='replace')
```

## Method 3: For photo metadata specifically

When working with photo metadata libraries like `exifread` or `Pillow`, you might encounter this pattern:

```python
from PIL import Image
from PIL.ExifTags import TAGS
import chardet

def clean_metadata_text(text):
    """Clean text for photo metadata embedding"""
    if isinstance(text, bytes):
        # Detect and decode
        detected = chardet.detect(text)
        encoding = detected.get('encoding', 'utf-8')
        text = text.decode(encoding, errors='replace')
    
    # Ensure it's valid UTF-8 and remove problematic characters
    text = text.encode('utf-8', errors='replace').decode('utf-8')
    
    # Optional: remove or replace characters that might cause issues
    text = text.replace('\x00', '')  # Remove null bytes
    
    return text

# Usage example
metadata_text = clean_metadata_text(suspicious_text)
```

The `chardet` library (`pip install chardet`) is particularly useful because it can detect encodings with good accuracy. For photo metadata, Method 3 is often most practical since it handles the common edge cases you'll encounter with text from various sources.
