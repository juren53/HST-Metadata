## Resizing JPEG images

To resize a JPEG image so that the maximum dimension in either the X or Y axis is 800 pixels using FFmpeg, you can use the following command:

```bash
ffmpeg -i input.jpg -vf "scale=min(800\,iw):min(800\,ih):force_original_aspect_ratio=decrease" output.jpg
```

This command:
- Takes `input.jpg` as the source
- Applies a scaling filter that:
  - Preserves the original aspect ratio
  - Ensures neither width nor height exceeds 800 pixels
  - Scales down the image only if it's larger than 800px in any dimension
- Outputs the result as `output.jpg`

If you want to process multiple images at once, you could use a simple shell loop. For example, in bash:

```bash
for img in *.jpg; do
    ffmpeg -i "$img" -vf "scale=min(800\,iw):min(800\,ih):force_original_aspect_ratio=decrease" "resized_$img"
done
```

Would you like me to explain how the scaling filter works in more detail?