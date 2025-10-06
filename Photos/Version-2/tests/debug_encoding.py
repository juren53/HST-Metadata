#!/usr/bin/env python3
"""
Debug script to trace exactly what happens in the encoding cleaning process.
"""

try:
    from ftfy import fix_text
    FTFY_AVAILABLE = True
except ImportError:
    FTFY_AVAILABLE = False

def debug_clean_process(text):
    """Debug the cleaning process step by step."""
    print(f"🔍 Input: '{text}'")
    
    # Step 1: ftfy processing
    if FTFY_AVAILABLE:
        ftfy_result = fix_text(text)
        print(f"1️⃣ After ftfy: '{ftfy_result}'")
    else:
        ftfy_result = text
        print("1️⃣ ftfy not available, skipping")
    
    # Step 2: Manual artifact cleaning (like in your table)
    artifacts = {
        'fran├º├⌐': 'français',
        'Lalwizy├án': 'Lalwizyan',
        '├º': 'ú',
        '├⌐': 'é',
        '├án': 'án',
        # Patterns that ftfy outputs but need further correction
        'françé': 'français',
        'Lalwizyàn': 'Lalwizyan',
    }
    
    manual_result = ftfy_result
    for artifact, replacement in artifacts.items():
        if artifact in manual_result:
            manual_result = manual_result.replace(artifact, replacement)
            print(f"2️⃣ Manual fix: '{artifact}' → '{replacement}' = '{manual_result}'")
    
    if manual_result == ftfy_result:
        print("2️⃣ No manual fixes applied")
    
    return manual_result

if __name__ == "__main__":
    # Test the problematic case
    test_case = "fran├º├⌐ Lalwizy├án"
    result = debug_clean_process(test_case)
    print(f"🎯 Final result: '{result}'")
    print(f"🎯 Expected: 'français Lalwizyan'")
    print(f"✅ Match: {result == 'français Lalwizyan'}")
