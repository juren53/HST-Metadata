# Insert Watermarks over JPEGs

Using a for loop in the Windows CMD window, this command executes against every file with the .jpg extension 
in the current directory adding a watermark over each JPEG file in the current directory.  Below is the command that you can cut and paste into the CMD window.

```
for %i in (*.jpg) do ffmpeg -i "%i" -i watermark.png -filter_complex "overlay=10:10" "watermarked_%i"
```

This loop iterates over all files in the current directory with the .jpg extension ((*.jpg)), and then 
runs the ffmpeg command with the appropriate input/output filenames.
 
The output filename is prefixed with "watermarked_" to prevent overwriting the original file.
