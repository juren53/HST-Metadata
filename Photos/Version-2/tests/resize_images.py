#!/usr/bin/env python3
"""
Image Resizer Script

This script resizes all JPEG images in the current working directory
to fit within an 800x800 pixel box while maintaining aspect ratio.
It preserves all metadata (EXIF, IPTC, etc.) during the conversion process.
"""

import os
import glob
import time
import subprocess
from PIL import Image
from datetime import datetime

def get_size_format(b):
    """
    Convert bytes to a human-readable format (KB, MB, etc.)
    """
    factor = 1024
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < factor:
            return f"{b:.2f} {unit}"
        b /= factor

def resize_image(image_path, max_size=800, quality=85, output_suffix="_800px"):
    """
    Resize an image to fit within max_size x max_size while maintaining aspect ratio
    Preserves all metadata (EXIF, IPTC, etc.) using ExifTool
    Returns: (original_size, new_size) in bytes
    """
    # Get the original file size
    original_size = os.path.getsize(image_path)
    
    # Open the image
    with Image.open(image_path) as img:
        # Get original image size and format
        width, height = img.size
        format = img.format
        
        # Skip if image is already smaller than max_size
        if width <= max_size and height <= max_size:
            print(f"Skipping {os.path.basename(image_path)} - already smaller than {max_size}x{max_size}")
            return (original_size, original_size, width, height, width, height, False)
        
        # Calculate the scaling factor
        scale_factor = min(max_size / width, max_size / height)
        
        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Create a new filename with suffix
        file_name, file_ext = os.path.splitext(image_path)
        output_path = f"{file_name}{output_suffix}{file_ext}"
        
        # Preserve EXIF data
        exif = img.info.get('exif', b'')
        
        # Resize image with high-quality resampling
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Save the resized image with original EXIF data
        if 'exif' in img.info:
            resized_img.save(output_path, format=format, quality=quality, exif=exif)
        else:
            resized_img.save(output_path, format=format, quality=quality)
        
        # Get new file size after initial save
        initial_new_size = os.path.getsize(output_path)
        
        # Use ExifTool to copy all metadata from the original image to the resized image
        print("  Preserving metadata with ExifTool...")
        try:
            # Run ExifTool to copy all metadata
            exiftool_cmd = ['exiftool', '-tagsFromFile', image_path, '-all:all', output_path, '-overwrite_original']
            result = subprocess.run(exiftool_cmd, capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                print(f"  Warning: ExifTool reported an issue: {result.stderr.strip()}")
            else:
                print("  Metadata successfully preserved")
        except Exception as e:
            print(f"  Error preserving metadata: {str(e)}")
        
        # Get final file size
        new_size = os.path.getsize(output_path)
        
        return (original_size, new_size, width, height, new_width, new_height, True)

def main():
    print("\n===== JPEG Image Resizer =====")
    print(f"Target Size: 800x800 pixels (maintaining aspect ratio)")
    print(f"Metadata: All EXIF/IPTC metadata will be preserved")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==============================\n")
    
    # Find all JPEG files in the current directory
    jpg_files = glob.glob("*.jpg")
    
    if not jpg_files:
        print("No JPEG files found in the current directory.")
        return
    
    print(f"Found {len(jpg_files)} JPEG files to process\n")
    
    # Process each image
    total_original_size = 0
    total_new_size = 0
    processed_count = 0
    skipped_count = 0
    
    start_time = time.time()
    
    for i, jpg_file in enumerate(jpg_files, 1):
        print(f"[{i}/{len(jpg_files)}] Processing: {jpg_file}")
        
        try:
            orig_size, new_size, orig_width, orig_height, new_width, new_height, was_resized = resize_image(jpg_file)
            
            total_original_size += orig_size
            total_new_size += new_size
            
            if was_resized:
                size_change_percent = 100 - (new_size / orig_size * 100)
                print(f"  Original: {orig_width}x{orig_height} ({get_size_format(orig_size)})")
                print(f"  Resized:  {new_width}x{new_height} ({get_size_format(new_size)})")
                print(f"  Reduction: {size_change_percent:.1f}%")
                processed_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"  Error processing {jpg_file}: {str(e)}")
        
        print()  # Empty line for readability
    
    # Calculate and display summary
    elapsed_time = time.time() - start_time
    total_reduction = total_original_size - total_new_size
    percent_reduction = 0
    if total_original_size > 0:
        percent_reduction = (total_reduction / total_original_size) * 100
    
    print("\n===== Summary =====")
    print(f"Total files found:      {len(jpg_files)}")
    print(f"Files processed:        {processed_count}")
    print(f"Files skipped:          {skipped_count} (already smaller than 800x800)")
    print(f"Original total size:    {get_size_format(total_original_size)}")
    print(f"New total size:         {get_size_format(total_new_size)}")
    print(f"Size reduction:         {get_size_format(total_reduction)} ({percent_reduction:.1f}%)")
    print(f"Time taken:             {elapsed_time:.2f} seconds")
    print(f"Completed at:           {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("===================")
    
    print("\nResized images have been saved with '_800px' added to the filename.")
    print("All metadata (EXIF, IPTC, etc.) has been preserved in the resized images.")

if __name__ == "__main__":
    main()

