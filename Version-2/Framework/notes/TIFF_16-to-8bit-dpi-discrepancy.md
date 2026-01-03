## Anthropic's Claude AI response:
The issue you're seeing is a classic metadata problem during TIFF conversion - the pixel data is preserved correctly, but the **DPI (dots per inch) metadata** is being changed or lost.

## What's Actually Happening

Your original file:
- **Pixels**: 4509 × 3454
- **DPI**: 1200
- **Physical size**: 3.758" × 2.878" (which is 4509÷1200 and 3454÷1200)

Your converted file:
- **Pixels**: 4509 × 3454 (unchanged - good!)
- **DPI**: 72 (changed - this is the problem)
- **Physical size**: 62.625" × 47.972" (which is 4509÷72 and 3454÷72)

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

