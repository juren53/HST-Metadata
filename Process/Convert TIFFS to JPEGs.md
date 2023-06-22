# Convert TIFFs to JPEGs 

This command runs against all TiFFs in the current directory 

- scales the original TIFF image ensuring 800 pixels is the maximum dimension, horizontal or vertical
- maintains the aspect ratio of the original image
- converts and saves the image as a JPEG file

Using a Windows for loop,  this command executes against every TIFF file in the current directory. 

```
for %%i in (*.tif) do ffmpeg -i "%%i" -vf "scale='min(800\, iw)':'min(800\, ih)':force_original_aspect_ratio=decrease" "converted_%%~ni.jpg"

```

This loop iterates over all files in the current directory with the .tif extension ((*.tif)), and then runs the ffmpeg command with the corresponding input/output filenames.

The output filename is prefixed with "converted_" to prevent overwriting the original file, and the %~ni parameter expands to the filename without the extension.
