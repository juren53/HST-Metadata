# Convert TIFFs to JPEGs 

This command takes all TiFFs in the current directory 

- scales the image to 800x800
- maintains the aspect ratio
- converts and saves the file as a JPEG image

Using a Windows for loop,  this command executes against every TIFF file in the current directory. 

```
for %i in (*.tif) do ffmpeg -i "%i" -vf "scale=w=800:h=800:force_original_aspect_ratio=decrease,pad=800:600:(ow-iw)/2:(oh-ih)/2" "converted_%~ni.jpg"
```

This loop iterates over all files in the current directory with the .tif extension ((*.tif)), and then runs the ffmpeg command with the corresponding input/output filenames.

The output filename is prefixed with "converted_" to prevent overwriting the original file, and the %~ni parameter expands to the filename without the extension.