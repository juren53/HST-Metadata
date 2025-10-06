#!/usr/bin/env python3
"""
Fix special characters identified in the CSV analysis report
"""

import sys
import csv
import re

def create_character_fixes():
    """Create a mapping of Unicode codes to their correct characters"""
    fixes = {
        # Unicode code point -> correct character
        '\u2013': '–',  # En dash (U+2013) - this is actually correct
        '\u00C9': 'É',  # Latin Capital Letter E with Acute
        '\u00ED': 'í',  # Latin Small Letter I with Acute  
        '\u00F3': 'ó',  # Latin Small Letter O with Acute
        '\u00F1': 'ñ',  # Latin Small Letter N with Tilde
        '\u00E9': 'é',  # Latin Small Letter E with Acute
        '\u00C1': 'Á',  # Latin Capital Letter A with Acute
        '\u00E7': 'ç',  # Latin Small Letter C with Cedilla
        '\u00FC': 'ü',  # Latin Small Letter U with Diaeresis
        '\u00E4': 'ä',  # Latin Small Letter A with Diaeresis
        '\u00DF': 'ß',  # Latin Small Letter Sharp S
        '\u00F6': 'ö',  # Latin Small Letter O with Diaeresis
    }
    return fixes

def identify_problematic_lines():
    """Identify lines and positions that need fixing based on the analysis report"""
    problems = {
        17: [(339, '\u2013', '–')],  # En dash - actually correct
        20: [(23, '\u00C9', 'É')],   # Georges-Étienne
        22: [(42, '\u00ED', 'í'),    # Caídos
             (120, '\u00F3', 'ó'),   # Revolución  
             (134, '\u00F1', 'ñ'),   # diseño
             (190, '\u00E9', 'é'),   # Méndez
             (235, '\u00C1', 'Á')],  # Ávalos
        23: [(24, '\u00E9', 'é'),    # Mémorial
             (109, '\u00E7', 'ç'),   # Français
             (149, '\u00E7', 'ç')],  # français
        24: [(32, '\u00FC', 'ü'),    # für
             (161, '\u00E4', 'ä'),   # Gänge
             (280, '\u00FC', 'ü'),   # für
             (333, '\u00DF', 'ß'),   # heißt
             (389, '\u00FC', 'ü'),   # überwiegend
             (411, '\u00E4', 'ä'),   # industriemäßige
             (412, '\u00DF', 'ß'),   # industriemäßige
             (418, '\u00F6', 'ö')],  # Tötung
        # Lines 252, 253, 261, 262, 263 have í in ID fields - these are likely errors
        252: [(49, '\u00ED', 'i')],  # Should be "i" not "í" in ID
        253: [(49, '\u00ED', 'i')],  # Should be "i" not "í" in ID  
        261: [(49, '\u00ED', 'i')],  # Should be "i" not "í" in ID
        262: [(50, '\u00ED', 'i')],  # Should be "i" not "í" in ID (position 50 due to quotes)
        263: [(49, '\u00ED', 'i')],  # Should be "i" not "í" in ID
    }
    return problems

def fix_csv_file(input_filename, output_filename):
    """Fix the special characters in the CSV file"""
    problems = identify_problematic_lines()
    
    try:
        # Read the file with UTF-8 encoding
        with open(input_filename, 'r', encoding='utf-8', errors='replace') as infile:
            lines = infile.readlines()
        
        print(f"Read {len(lines)} lines from {input_filename}")
        
        # Track changes made
        changes_made = 0
        
        # Process each line
        for line_num in range(len(lines)):
            line_number = line_num + 1  # Convert to 1-based indexing
            
            if line_number in problems:
                original_line = lines[line_num].rstrip('\n\r')
                modified_line = original_line
                
                print(f"\nProcessing Line {line_number}:")
                print(f"Original: {original_line[:100]}...")
                
                # Apply fixes for this line (in reverse order to maintain positions)
                fixes_for_line = sorted(problems[line_number], key=lambda x: x[0], reverse=True)
                
                for position, unicode_char, replacement in fixes_for_line:
                    if position < len(modified_line):
                        old_char = modified_line[position]
                        # Convert the line to a list for easier manipulation
                        line_chars = list(modified_line)
                        line_chars[position] = replacement
                        modified_line = ''.join(line_chars)
                        
                        print(f"  Position {position}: '{old_char}' → '{replacement}'")
                        changes_made += 1
                
                # Update the line in our list (add back line ending)
                lines[line_num] = modified_line + '\n'
                print(f"Modified: {modified_line[:100]}...")
        
        # Write the fixed file
        with open(output_filename, 'w', encoding='utf-8', newline='') as outfile:
            outfile.writelines(lines)
        
        print(f"\n✓ Successfully fixed {changes_made} characters")
        print(f"✓ Output written to: {output_filename}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {input_filename}")
    except Exception as e:
        print(f"❌ Error processing file: {e}")

def main():
    """Main function"""
    input_file = "../testing-data/Test-6-Files/export.csv"
    output_file = "../testing-data/Test-6-Files/export_FIXED.csv"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print("Special Character Fix Utility")
    print("=" * 40)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    fix_csv_file(input_file, output_file)

if __name__ == "__main__":
    main()
