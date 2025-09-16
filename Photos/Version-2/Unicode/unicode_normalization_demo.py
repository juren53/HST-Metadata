#!/usr/bin/env python3
"""
Unicode Normalization Demo
Demonstrates various aspects of Unicode normalization in Python
"""

import unicodedata
import sys

def print_separator(title):
    """Print a formatted section separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def analyze_string(text, label="Text"):
    """Analyze and display detailed information about a Unicode string"""
    print(f"\n{label}: {repr(text)}")
    print(f"Visual: {text}")
    print(f"Length: {len(text)} characters")
    print(f"Bytes (UTF-8): {len(text.encode('utf-8'))} bytes")
    print("Character breakdown:")
    for i, char in enumerate(text):
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = "NO NAME"
        print(f"  [{i}] U+{ord(char):04X} '{char}' - {name}")

def demo_basic_normalization():
    """Demonstrate basic normalization concepts"""
    print_separator("Basic Unicode Normalization")
    
    # Same visual character, different representations
    text1 = "café"  # precomposed é (U+00E9)
    text2 = "cafe\u0301"  # e + combining acute accent (U+0301)
    
    print("Two ways to represent the same text:")
    analyze_string(text1, "Method 1 (precomposed)")
    analyze_string(text2, "Method 2 (base + combining)")
    
    print(f"\nAre they equal? {text1 == text2}")
    print(f"Do they look the same? '{text1}' vs '{text2}'")
    
    # Normalize both to NFC
    norm1 = unicodedata.normalize('NFC', text1)
    norm2 = unicodedata.normalize('NFC', text2)
    
    print(f"\nAfter NFC normalization:")
    print(f"Are they equal now? {norm1 == norm2}")
    analyze_string(norm1, "Normalized text")

def demo_all_forms():
    """Demonstrate all four normalization forms"""
    print_separator("All Normalization Forms")
    
    # Text with various Unicode features
    test_text = "ﬁlé №①"  # fi ligature, é, №, circled 1
    
    analyze_string(test_text, "Original")
    
    forms = ['NFC', 'NFD', 'NFKC', 'NFKD']
    results = {}
    
    for form in forms:
        normalized = unicodedata.normalize(form, test_text)
        results[form] = normalized
        analyze_string(normalized, f"{form} normalized")
    
    print("\nComparison of results:")
    for form in forms:
        print(f"{form:4}: {repr(results[form]):20} -> '{results[form]}'")

def demo_practical_text_comparison():
    """Demonstrate practical text comparison issues"""
    print_separator("Practical Text Comparison")
    
    # Simulate user input variations
    variations = [
        "Müller",           # precomposed ü
        "Mu\u0308ller",     # u + combining diaeresis
        "MÜLLER",           # uppercase
        "müller",           # lowercase
    ]
    
    print("Different variations of the same name:")
    for i, name in enumerate(variations):
        analyze_string(name, f"Variation {i+1}")
    
    print("\nDirect equality comparison:")
    for i, name1 in enumerate(variations):
        for j, name2 in enumerate(variations):
            if i < j:  # Only compare each pair once
                print(f"'{name1}' == '{name2}': {name1 == name2}")
    
    print("\nAfter NFC normalization and lowercasing:")
    normalized_variations = [unicodedata.normalize('NFC', name.lower()) for name in variations]
    
    for i, name1 in enumerate(normalized_variations):
        for j, name2 in enumerate(normalized_variations):
            if i < j:
                print(f"normalized('{variations[i].lower()}') == normalized('{variations[j].lower()}'): {name1 == name2}")

def demo_filename_handling():
    """Demonstrate filename normalization (common on different OS)"""
    print_separator("Filename Normalization")
    
    # Simulate filenames from different systems
    filenames = [
        "résumé.pdf",           # NFC form (common on Windows)
        "re\u0301sume\u0301.pdf",  # NFD form (common on macOS)
    ]
    
    print("Filenames that might appear identical but aren't:")
    for i, filename in enumerate(filenames):
        analyze_string(filename, f"Filename {i+1}")
    
    print(f"\nAre filenames equal? {filenames[0] == filenames[1]}")
    
    # Normalize for consistent handling
    normalized_filenames = [unicodedata.normalize('NFC', f) for f in filenames]
    print(f"After NFC normalization, are they equal? {normalized_filenames[0] == normalized_filenames[1]}")

def demo_search_functionality():
    """Demonstrate search with normalization"""
    print_separator("Search Functionality")
    
    # Database of names (with mixed normalization)
    database = [
        "José",
        "Jose\u0301",  # Same as José but NFD
        "François",
        "Francois",
        "Müller",
        "Mu\u0308ller",  # Same as Müller but NFD
    ]
    
    print("Simulated database of names:")
    for i, name in enumerate(database):
        print(f"{i+1}. {repr(name)} -> '{name}'")
    
    def search_naive(query, db):
        """Naive search without normalization"""
        return [name for name in db if query in name]
    
    def search_normalized(query, db):
        """Search with normalization"""
        normalized_query = unicodedata.normalize('NFC', query.lower())
        results = []
        for name in db:
            normalized_name = unicodedata.normalize('NFC', name.lower())
            if normalized_query in normalized_name:
                results.append(name)
        return results
    
    search_term = "jose"
    print(f"\nSearching for '{search_term}':")
    
    naive_results = search_naive(search_term, database)
    normalized_results = search_normalized(search_term, database)
    
    print(f"Naive search results: {naive_results}")
    print(f"Normalized search results: {normalized_results}")

def demo_performance_comparison():
    """Compare performance of different operations"""
    print_separator("Performance Considerations")
    
    import time
    
    # Generate test data
    test_strings = [
        "café" * 1000,
        "cafe\u0301" * 1000,
        "naïve" * 1000,
        "nai\u0308ve" * 1000,
    ]
    
    print("Performance comparison for normalization:")
    
    for form in ['NFC', 'NFD', 'NFKC', 'NFKD']:
        start_time = time.time()
        for _ in range(100):
            for text in test_strings:
                unicodedata.normalize(form, text)
        end_time = time.time()
        print(f"{form}: {(end_time - start_time)*1000:.2f}ms for 400 normalizations")

def create_normalization_utility():
    """Create a utility function for practical use"""
    print_separator("Practical Utility Function")
    
    def normalize_for_comparison(text, form='NFC', case_fold=True):
        """
        Normalize text for consistent comparison
        
        Args:
            text: Input text
            form: Normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')
            case_fold: Whether to apply case folding
        
        Returns:
            Normalized text ready for comparison
        """
        normalized = unicodedata.normalize(form, text)
        if case_fold:
            normalized = normalized.casefold()  # More aggressive than lower()
        return normalized
    
    # Test the utility
    test_pairs = [
        ("Straße", "STRASSE"),  # German ß handling
        ("İstanbul", "istanbul"),  # Turkish i handling
        ("café", "CAFÉ"),
        ("ﬁle", "FILE"),  # ligature
    ]
    
    print("Testing normalization utility:")
    for text1, text2 in test_pairs:
        norm1 = normalize_for_comparison(text1)
        norm2 = normalize_for_comparison(text2)
        print(f"'{text1}' vs '{text2}': {norm1 == norm2} ('{norm1}' vs '{norm2}')")
    
    return normalize_for_comparison

def main():
    """Run all demonstrations"""
    print("Python Unicode Normalization Comprehensive Demo")
    print(f"Python version: {sys.version}")
    print(f"Unicode database version: {unicodedata.unidata_version}")
    
    # Run all demos
    demo_basic_normalization()
    demo_all_forms()
    demo_practical_text_comparison()
    demo_filename_handling()
    demo_search_functionality()
    demo_performance_comparison()
    
    # Create utility function
    normalize_func = create_normalization_utility()
    
    print_separator("Summary and Best Practices")
    print("""
Key Takeaways:

1. Use NFC for most applications (storage, comparison)
2. Normalize text as early as possible in your pipeline
3. Be consistent with your chosen normalization form
4. Consider case folding along with normalization
5. NFKC/NFKD are more aggressive - use carefully
6. Particularly important for:
   - User input processing
   - Database operations
   - File system operations
   - Search functionality
   - Text comparison

Recommended utility function is available as normalize_for_comparison()
    """)

if __name__ == "__main__":
    main()