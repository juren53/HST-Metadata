## PROCESS_for-generating-app-icons.md

Here are some a repeatable processes for generating icons with that style. The proceses use GIMP and ImageMagick approaches that can be adapted to variety of situations. 

## Process Overview

Here's a comprehensive approach using both tools:

### **Method 1: ImageMagick (Fully Automated - Recommended for Repeatability)**

This approach uses shell scripts that you can reuse for any source image.

**Step 1: Create the master script**

```bash
#!/bin/bash
# icon_generator.sh
# Usage: ./icon_generator.sh input_image.png output_icon.png [size] [corner_radius] [padding]

INPUT="$1"
OUTPUT="$2"
SIZE="${3:-512}"           # Default 512x512
CORNER_RADIUS="${4:-60}"   # Default corner radius (adjust for size)
PADDING="${5:-40}"         # Padding around the image

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 input_image output_icon.png [size] [corner_radius] [padding]"
    exit 1
fi

# Calculate inner size (size minus padding on both sides)
INNER_SIZE=$((SIZE - (PADDING * 2)))

# Step 1: Resize input to fit within inner area, maintaining aspect ratio
convert "$INPUT" \
    -resize "${INNER_SIZE}x${INNER_SIZE}" \
    -gravity center \
    -background none \
    -extent "${INNER_SIZE}x${INNER_SIZE}" \
    temp_resized.png

# Step 2: Create rounded corners mask
convert -size "${INNER_SIZE}x${INNER_SIZE}" xc:none \
    -draw "roundrectangle 0,0,${INNER_SIZE},${INNER_SIZE},${CORNER_RADIUS},${CORNER_RADIUS}" \
    temp_mask.png

# Step 3: Apply mask to create rounded corners
convert temp_resized.png temp_mask.png \
    -alpha off -compose CopyOpacity -composite \
    temp_rounded.png

# Step 4: Place on transparent square background with padding
convert -size "${SIZE}x${SIZE}" xc:none \
    temp_rounded.png \
    -gravity center \
    -composite \
    "$OUTPUT"

# Cleanup
rm temp_resized.png temp_mask.png temp_rounded.png

echo "Icon generated: $OUTPUT (${SIZE}x${SIZE}, corner radius: ${CORNER_RADIUS}, padding: ${PADDING})"
```

**Step 2: Generate multiple sizes**

```bash
#!/bin/bash
# generate_icon_set.sh
# Generates a full set of icon sizes from one source image

INPUT="$1"
OUTPUT_PREFIX="${2:-icon}"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 input_image [output_prefix]"
    exit 1
fi

# Standard icon sizes with appropriate corner radii and padding
declare -A SIZES=(
    ["16"]="2:2"      # size:corner_radius:padding
    ["32"]="4:4"
    ["48"]="6:6"
    ["64"]="8:8"
    ["128"]="16:12"
    ["256"]="32:24"
    ["512"]="60:40"
)

mkdir -p icons

for size in "${!SIZES[@]}"; do
    IFS=':' read -r corner padding <<< "${SIZES[$size]}"
    ./icon_generator.sh "$INPUT" "icons/${OUTPUT_PREFIX}_${size}.png" "$size" "$corner" "$padding"
done

echo "Generated icon set in icons/ directory"
```

### **Method 2: GIMP (Interactive Design)**

For when you want more control or are creating icons from scratch:

**Step-by-step process:**

1. **Create new image:**
   - `File → New`
   - Set to square (512x512 for master)
   - Fill with: Transparency

2. **Import/create your graphic:**
   - `File → Open as Layers` (for existing images)
   - Or use GIMP tools to create graphics
   - Scale to fit with padding: `Layer → Scale Layer`

3. **Create rounded corners:**
   - `Filters → Light and Shadow → Drop Shadow` (set offsets to 0, but use this for soft edges)
   - Or better: `Select → Rounded Rectangle`
   - Invert selection: `Select → Invert`
   - Delete: Press `Delete` key
   - Feather edges: `Select → Feather` (2-5 pixels)

4. **Alternative rounded corners method (more control):**
   ```
   - Layer → Layer to Image Size
   - Select → All
   - Select → Rounded Rectangle (adjust corner radius)
   - Select → Invert
   - Edit → Clear
   - Select → Feather (for soft edges)
   ```

5. **Export:**
   - `File → Export As`
   - Save as PNG
   - Enable "Save background color" unchecked
   - Enable "Save transparency"

6. **Create GIMP Script-Fu (for automation):**

Save this as `~/.config/GIMP/2.10/scripts/rounded-icon.scm`:

```scheme
(define (script-fu-rounded-icon input-file output-file size corner-radius)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE input-file input-file)))
         (drawable (car (gimp-image-get-active-layer image))))
    
    ; Scale image
    (gimp-image-scale image size size)
    
    ; Select rounded rectangle
    (gimp-image-select-round-rectangle image CHANNEL-OP-REPLACE 0 0 size size corner-radius corner-radius)
    
    ; Invert and clear
    (gimp-selection-invert image)
    (gimp-edit-clear drawable)
    (gimp-selection-none image)
    
    ; Export
    (file-png-save RUN-NONINTERACTIVE image drawable output-file output-file 0 9 0 0 0 0 0)
    
    (gimp-image-delete image)))

(script-fu-register
  "script-fu-rounded-icon"
  "Rounded Icon"
  "Create rounded corner icon"
  "Script"
  "Public Domain"
  "2025"
  ""
  SF-FILENAME "Input File" ""
  SF-FILENAME "Output File" ""
  SF-ADJUSTMENT "Size" '(512 16 2048 1 10 0 0)
  SF-ADJUSTMENT "Corner Radius" '(60 0 500 1 10 0 0))
```

### **Method 3: Hybrid Approach (Recommended)**

1. **Design in GIMP** - Create your master graphic at 512x512
2. **Export clean PNG** with transparency
3. **Use ImageMagick** to generate all sizes automatically

### **Quick Reference Commands**

**Single icon with soft rounded corners:**
```bash
./icon_generator.sh my_image.png app_icon.png 256 30 20
```

**Full icon set:**
```bash
./generate_icon_set.sh my_logo.png myapp
```

**Quick one-liner for testing:**
```bash
convert input.png -resize 432x432 -gravity center -background none -extent 432x432 \
    \( -size 432x432 xc:none -draw "roundrectangle 0,0,432,432,50,50" \) \
    -alpha off -compose CopyOpacity -composite \
    -gravity center -background none -extent 512x512 output.png
```

### **Tips for Best Results**

1. **Source images**: Start with high-resolution, square images (at least 512x512)
2. **Corner radius**: Should scale with size (roughly 10-15% of image size)
3. **Padding**: Gives breathing room (5-10% of size)
4. **Soft edges**: Add `-blur 0x1` before compositing for softer rounded corners
5. **Testing**: Generate at 512px first, then scale down to check quality

Would you like me to create a complete package with both scripts and a sample workflow, or would you prefer to focus on one method (ImageMagick vs GIMP)?