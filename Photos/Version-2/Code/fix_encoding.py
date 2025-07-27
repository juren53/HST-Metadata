#!/usr/bin/env python3
"""
Fix mojibake encoding issues from Google Sheets downloads
"""

def fix_mojibake(text):
    """
    Try different encoding combinations to fix mojibake text
    """
    fixes = [
        ('cp1252', 'utf-8'),
        ('latin1', 'utf-8'),
        ('iso-8859-1', 'utf-8'),
        ('windows-1252', 'utf-8')
    ]
    
    for source_encoding, target_encoding in fixes:
        try:
            fixed = text.encode(source_encoding).decode(target_encoding)
            return fixed, f"{source_encoding} -> {target_encoding}"
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    
    return text, "No fix found"

if __name__ == "__main__":
    # Test with the problematic text
    corrupted_text = "NiÃos HÃroes"
    print(f"Original corrupted text: {corrupted_text}")
    
    fixed_text, method = fix_mojibake(corrupted_text)
    print(f"Fixed text: {fixed_text}")
    print(f"Method used: {method}")
    
    # Test if it worked
    if fixed_text != corrupted_text:
        print("✓ Successfully fixed the encoding!")
    else:
        print("✗ Could not fix the encoding automatically")
