# Insert Watermarks over JPEGs

Using a for loop in Windows command prompt,this command executes against every file with the .jpg extension 
in the current directory.

```
for %i in (*.jpg) do ffmpeg -i "%i" -i watermark.png -filter_complex "overlay=10:10" "watermarked_%i"
```

This loop iterates over all files in the current directory with the .jpg extension ((*.jpg)), and then 
runs the ffmpeg command with the appropriate input/output filenames.
 
The output filename is prefixed with "watermarked_" to prevent overwriting the original file.
