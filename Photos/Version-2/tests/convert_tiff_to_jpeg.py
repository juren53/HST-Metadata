import os
import sys
import subprocess
from PIL import Image
from glob import glob

def convert_tiff_to_jpeg_with_metadata(tiff_path):
    """Convert a TIFF file to JPEG and preserve metadata using exiftool"""
    try:
        # Get the base name without extension
        base_name = os.path.splitext(os.path.basename(tiff_path))[0]
        jpeg_path = f"{base_name}.jpg"
        
        print(f"Converting {tiff_path} to {jpeg_path}...")
        
        # Step 1: Convert TIFF to JPEG using PIL
        with Image.open(tiff_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPEG with high quality
            img.save(jpeg_path, 'JPEG', quality=95)
        
        # Step 2: Copy metadata from TIFF to JPEG using exiftool
        if os.path.exists(jpeg_path):
            print("  Copying metadata using exiftool...")
            exiftool_cmd = f'exiftool -tagsfromfile "{tiff_path}" -all:all "{jpeg_path}" -overwrite_original'
            subprocess.run(exiftool_cmd, shell=True, check=True)
            
            print(f"  Success! Created {jpeg_path} with metadata preserved.")
            return True
        else:
            print(f"  Failed to create JPEG file: {jpeg_path}")
            return False
            
    except Exception as e:
        print(f"  Error processing {tiff_path}: {str(e)}")
        return False

def main():
    """Convert all TIFF files in the current directory to JPEG with metadata preserved"""
    # Find all TIFF files in the current directory
    tiff_files = glob("*.tif")
    
    total_files = len(tiff_files)
    converted = 0
    
    print(f"Found {total_files} TIFF files to convert")
    
    for i, tiff_file in enumerate(tiff_files, 1):
        print(f"[{i}/{total_files}] Processing {tiff_file}")
        success = convert_tiff_to_jpeg_with_metadata(tiff_file)
        if success:
            converted += 1
    
    print(f"\nConversion complete: {converted} of {total_files} files successfully converted.")
    
    # Verify IPTC metadata in the first JPEG file as a sample
    if converted > 0:
        jpeg_files = glob("*.jpg")
        if jpeg_files:
            print("\nVerifying metadata in first JPEG file:")
            sample_jpeg = jpeg_files[0]
            verify_cmd = f'exiftool -IPTC "{sample_jpeg}"'
            subprocess.run(verify_cmd, shell=True)

if __name__ == "__main__":
    main()
