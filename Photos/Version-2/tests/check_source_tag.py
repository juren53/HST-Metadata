#!/usr/bin/python3
import exiftool
import os
import glob

# Find a sample image file
ext = "tif"  # Change to "jpg" if needed
files = glob.glob(f'*.{ext}')

if not files:
    print(f"No {ext} files found in the directory")
    exit(1)

sample_file = files[0]
print(f"Checking tags for sample file: {sample_file}")

# Run exiftool directly to get all tags
import subprocess

cmd = ['exiftool', '-g', '-j', sample_file]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    import json
    metadata = json.loads(result.stdout)[0]  # Parse JSON output
    
    # Look for Source tag in different tag groups
    source_tags = []
    for key, value in metadata.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if 'source' in subkey.lower():
                    source_tags.append((f"{key}:{subkey}", subvalue))
    
    if source_tags:
        print("\nFound Source tags:")
        for tag, value in source_tags:
            print(f"{tag}: {value}")
    else:
        print("\nNo Source tags found in the file.")
    
    # Print some other IPTC tags for comparison
    print("\nOther IPTC tags for comparison:")
    if 'IPTC' in metadata:
        iptc_data = metadata['IPTC']
        for tag, value in iptc_data.items():
            print(f"IPTC:{tag}: {value}")
    else:
        print("No IPTC tags found")
        
except subprocess.CalledProcessError as e:
    print(f"Error running exiftool: {e}")
    print(f"stderr: {e.stderr}")

