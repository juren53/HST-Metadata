#!/usr/bin/env python3
"""
Interactive Unicode Normalization Tester
Quick tool to test Unicode normalization on custom input
"""

import unicodedata

def analyze_text(text):
    """Analyze and display Unicode details for a given text"""
    print(f"\nText: {repr(text)}")
    print(f"Visual: '{text}'")
    print(f"Length: {len(text)} characters")
    print(f"UTF-8 bytes: {len(text.encode('utf-8'))}")
    
    print("Characters:")
    for i, char in enumerate(text):
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = "NO NAME"
        print(f"  [{i}] U+{ord(char):04X} '{char}' - {name}")

def test_normalization(text1, text2=None):
    """Test normalization on one or two texts"""
    print("\n" + "="*50)
    analyze_text(text1)
    
    if text2:
        analyze_text(text2)
        print(f"\nAre they equal? {text1 == text2}")
    
    forms = ['NFC', 'NFD', 'NFKC', 'NFKD']
    print(f"\nNormalization results:")
    
    for form in forms:
        normalized1 = unicodedata.normalize(form, text1)
        print(f"{form:4}: {repr(normalized1)} -> '{normalized1}'")
        
        if text2:
            normalized2 = unicodedata.normalize(form, text2)
            equal_after = normalized1 == normalized2
            print(f"      Text2: {repr(normalized2)} -> Equal: {equal_after}")

if __name__ == "__main__":
    print("Unicode Normalization Tester")
    print("="*30)
    
    # Example tests
    examples = [
        ("Basic example", "café", "cafe\u0301"),
        ("Filename test", "résumé.pdf", "re\u0301sume\u0301.pdf"),
        ("Ligature test", "ﬁle", None),
        ("Mixed case", "Müller", "mu\u0308ller"),
    ]
    
    for title, text1, text2 in examples:
        print(f"\n{title.upper()}")
        test_normalization(text1, text2)
    
    # Interactive mode
    print("\n" + "="*50)
    print("INTERACTIVE MODE")
    print("Enter text to analyze (or 'quit' to exit)")
    print("Format: 'text1' or 'text1|text2' to compare")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if '|' in user_input:
                parts = user_input.split('|', 1)
                test_normalization(parts[0].strip(), parts[1].strip())
            else:
                test_normalization(user_input)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")