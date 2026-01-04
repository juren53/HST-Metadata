## Anthropic's Claude AI response:
The issue you're seeing is a classic metadata problem during TIFF conversion - the pixel data is preserved correctly, but the **DPI (dots per inch) metadata** is being changed or lost.

## What's Actually Happening

Your original 16 bit file:
- **Pixels**: 4509 × 3454
- **DPI**: 1200
- **Physical size**: 3.758" × 2.878" (which is 4509÷1200 and 3454÷1200)
- **File size**: 

Your converted 8 bit file:
- **Pixels**: 4509 × 3454 (unchanged - good!)
- **DPI**: 72 (changed - this is the problem)
- **Physical size**: 62.625" × 47.972" (which is 4509÷72 and 3454÷72)
- **File size**: 

The physical dimensions aren't actually changing - what's changing is the **resolution metadata** that tells software "how many pixels per inch this represents." When the DPI drops from 1200 to 72, the same pixels appear to represent a much larger physical object.

## Why This Happens

72 DPI is a common default value that many image processing tools fall back to when:
- The DPI metadata isn't explicitly preserved during conversion
- The conversion tool doesn't properly copy TIFF tags
- The tool assumes screen resolution (72 or 96 DPI) as default

## The Fix

Whatever tool you're using to convert from 16-bit to 8-bit needs to **preserve the resolution metadata**. If you're using:

- **ImageMagick**: Add `-units PixelsPerInch -density 1200` to your command
- **Python/PIL**: Explicitly set the DPI in your save operation
- **Other tools**: Look for resolution/DPI preservation settings

========================================================================

## References for TIFF DPI Metadata Issue

Here are authoritative references that support the technical explanation provided:

### **TIFF Format and Resolution Tags**

1. **Library of Congress - TIFF Tags Documentation**
   - The TIFF 6.0 specification defines baseline and extended tags, including resolution-related metadata stored in the TIFF header
   - URL: https://www.loc.gov/preservation/digital/formats/content/tiff_tags.shtml

2. **Wikipedia - TIFF Format**
   - TIFF files use tags identified by 16-bit numbers to specify metadata including horizontal and vertical resolution
   - URL: https://en.wikipedia.org/wiki/TIFF

3. **Exiv2 - TIFF Metadata Structure**
   - TIFF files contain XResolution (tag 0x011a), YResolution (tag 0x011b), and ResolutionUnit (tag 0x0128) tags that define image resolution metadata
   - URL: https://dev.exiv2.org/projects/exiv2/wiki/The_Metadata_in_TIFF_files

### **72 DPI as Default Value**

4. **Wikipedia - Dots Per Inch**
   - Since the 1980s, Macs have set the default display DPI to 72 PPI, while Microsoft Windows has used a default of 96 PPI
   - URL: https://en.wikipedia.org/wiki/Dots_per_inch

5. **Adobe Photoshop Forums (archived)**
   - Untagged images open at 72 ppi by default in most programs, and cameras commonly save JPEG files with the dummy value of 72 placed into the DPI slot
   - URL: https://groups.google.com/g/adobe.photoshop.windows/c/HKYDazLur94

6. **Digital Photography Review Forums**
   - 72 dpi is the proper setting for monitor viewing, and it's common for cameras to save jpg files with the dummy value of 72 placed into the dpi slot in the jpg file
   - URL: https://www.dpreview.com/forums/thread/309864

### **ImageMagick DPI Preservation**

7. **ImageMagick Forums - Change DPI while keeping resolution**
   - To preserve DPI when converting images with ImageMagick, use `-units PixelsPerInch` followed by `-density` value to set output density without changing pixel dimensions
   - URL: https://www.imagemagick.org/discourse-server/viewtopic.php?t=20347

8. **ImageMagick Forums - Determining DPI**
   - The command `convert image.jpg -units "PixelsPerInch" -density 300` can adjust DPI without resampling, preserving the pixel dimensions while changing resolution metadata
   - URL: https://legacy.imagemagick.org/discourse-server/viewtopic.php?t=16110

### **Python/PIL DPI Preservation**

9. **Pillow Documentation - Image File Formats**
   - When saving TIFF files with Pillow, resolution can be set using the dpi parameter as a tuple of two numbers corresponding to the desired dpi in each direction
   - URL: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

10. **Pillow Source Code - TiffImagePlugin.py**
    - Pillow's TIFF encoder sets RESOLUTION_UNIT to 2 (inches) and writes X_RESOLUTION and Y_RESOLUTION tags when the dpi parameter is provided during save operations
    - URL: https://github.com/python-pillow/Pillow/blob/main/src/PIL/TiffImagePlugin.py

These references confirm the technical details about TIFF resolution metadata, the 72 DPI default behavior, and proper methods for preserving DPI during image format conversions.
