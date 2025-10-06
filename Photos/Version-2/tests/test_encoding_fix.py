#!/usr/bin/env python3
"""
Test script to check how well ftfy handles the encoding artifacts found in your CSV.
"""

try:
    from ftfy import fix_text
    FTFY_AVAILABLE = True
except ImportError:
    FTFY_AVAILABLE = False
    print("❌ ftfy not available. Please run: pip install ftfy")
    exit(1)

def test_artifacts():
    """Test various encoding artifacts."""
    
    test_cases = [
        # Original artifacts from your CSV
        ("Ca├¡dos", "Caídos"),
        ("Revoluci├│n", "Revolución"),
        ("dise├▒o", "diseño"),
        ("M├⌐ndez", "Méndez"),
        ("├<81>valos", "Ávalos"),
        ("M├⌐morial", "Mémorial"),
        ("Fran├ºais", "Français"),
        ("fran├º├⌐", "français"),
        ("Lalwizy├án", "Lalwizyan"),
        ("f├╝r", "für"),
        ("G├ñnge", "Gänge"),
        
        # Individual characters
        ("├¡", "í"),
        ("├│", "ó"),
        ("├▒", "ñ"),
        ("├⌐", "é"),
        ("├º", "ú"),
        ("├╝", "ü"),
        ("├ñ", "ä"),
    ]
    
    print("🧪 Testing ftfy on encoding artifacts")
    print("=" * 50)
    
    ftfy_success = 0
    total_tests = len(test_cases)
    
    for broken_text, expected_text in test_cases:
        fixed_text = fix_text(broken_text)
        success = fixed_text == expected_text
        
        if success:
            ftfy_success += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} '{broken_text}' → '{fixed_text}' (expected: '{expected_text}')")
    
    print(f"\n📊 Results:")
    print(f"✅ ftfy fixed: {ftfy_success}/{total_tests} ({ftfy_success/total_tests*100:.1f}%)")
    print(f"❌ Still broken: {total_tests - ftfy_success}/{total_tests}")
    
    if ftfy_success == total_tests:
        print("\n🎉 ftfy handles all your artifacts perfectly!")
        print("You may not need the manual artifact table anymore.")
    elif ftfy_success > total_tests * 0.8:
        print(f"\n👍 ftfy handles most artifacts well ({ftfy_success/total_tests*100:.1f}%).")
        print("The manual table provides good backup for the rest.")
    else:
        print(f"\n⚠️  ftfy only handles {ftfy_success/total_tests*100:.1f}% of artifacts.")
        print("The manual artifact table is still important.")

if __name__ == "__main__":
    test_artifacts()
