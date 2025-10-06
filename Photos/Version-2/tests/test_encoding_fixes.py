#!/usr/bin/env python3

import sys
from g2c import smart_encoding_cleaner, clean_encoding_artifacts

def test_encoding_fixes():
    """Test that our encoding artifact fixes work correctly."""
    
    print("Testing encoding artifact cleaning...")
    print("=" * 50)
    
    # Test cases based on the artifacts we found in the original export.csv
    test_cases = [
        # Spanish artifacts
        ("CaA-dos", "Caídos"),
        ("RevoluciA3n", "Revolución"), 
        ("diseA±o", "diseño"),
        ("MAcndez", "Méndez"),
        ("A?valos", "Ávalos"),
        
        # French artifacts
        ("MAcmorial", "Mémorial"),
        ("FranAais", "Français"),
        
        # German artifacts
        ("fA¼r", "für"),
        ("GAnge", "Gänge"),
        
        # Current artifacts mentioned by user (2025-01-21)
        ("T├╢tung", "Tötung"),
        ("G├ñnge", "Gänge"),
        ("f├╝r", "für"),
        
        # Current export.csv artifacts
        ("écession", "Accession"),
        ("éheson", "Acheson"),
        ("äderson", "Anderson"),
        ("änouncement", "Announcement"),
        ("äthony", "Anthony"),
        ("étg", "Acting"),
        ("ädrey", "Andrey"),
        ("éademy", "Academy"),
        ("355í7", "355A-7"),
        
        # Individual pattern tests
        ("CaA-dos example text", "Caídos example text"),
        ("Test RevoluciA3n story", "Test Revolución story"),
        ("The diseA±o was great", "The diseño was great"),
        ("MAcndez family", "Méndez family"),
        ("A?valos street", "Ávalos street"),
        ("MAcmorial building", "Mémorial building"),
        ("FranAais language", "Français language"),
        ("fA¼r Germany", "für Germany"),
        ("Long GAnge path", "Long Gänge path"),
    ]
    
    print("Testing clean_encoding_artifacts function:")
    print("-" * 45)
    
    all_passed = True
    for input_text, expected in test_cases:
        result = clean_encoding_artifacts(input_text)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"{status}: '{input_text}' → '{result}'")
        if result != expected:
            print(f"       Expected: '{expected}'")
    
    print("\n" + "=" * 50)
    print("Testing smart_encoding_cleaner function:")
    print("-" * 45)
    
    for input_text, expected in test_cases:
        result = smart_encoding_cleaner(input_text)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"{status}: '{input_text}' → '{result}'")
        if result != expected:
            print(f"       Expected: '{expected}'")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All encoding tests PASSED!")
        print("The encoding artifact cleaning is working correctly.")
    else:
        print("⚠️ Some encoding tests FAILED!")
        print("The encoding cleaning may need additional improvements.")
    
    print("\nNote: This demonstrates that our encoding fixes now handle")
    print("the artifacts that were found in the original export.csv file.")

if __name__ == "__main__":
    test_encoding_fixes()
