# Insert Watermarks over JPEGs

Using a for loop in the Windows CMD window, this command executes against every file with the .jpg extension 
in the current directory adding a watermark over each JPEG file in the current directory.  Below is the command that you can cut and paste into the CMD window.

```
for %i in (*.jpg) do ffmpeg -i "%i" -i watermark.png -filter_complex "overlay=10:10" "watermarked_%i"
```

This loop iterates over all files in the current directory with the .jpg extension ((*.jpg)), and then 
runs the ffmpeg command with the appropriate input/output filenames.
 
The output filename is prefixed with "watermarked_" to prevent overwriting the original file.

============================================================================
Another method of watermarking JPEGS is:

1. Sort the CSV file on the CopyRightNotice column.

2. Copy the list of Restricted accession numbers and paste them into a new spreadsheet.

3.  With the pasted list in column A, enter the following formula: into B1

         =A1 & ".jpg"

4. Copy the formula in B1 for each entry in column A.

5. You now have a list of JPEG filenames that you can COPY & PASTE into the IrfanView batch window and you can apply watermarks to.
