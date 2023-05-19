You can use the following FFmpeg command to convert a TIF image to JPG format while preserving the metadata information:

ffmpeg -i input.tif -c:v mjpeg -q:v 1 -metadata:s:v:0 comment="exiftool -S -Comment input.tif" output.jpg

This command uses the -c:v mjpeg option to encode the output as MJPEG, and the -q:v 1 option to set the highest quality for the output. 
The -metadata:s:v:0 comment="exiftool -S -Comment input.tif" option carries over the comment metadata from the input file to the 
output file. You will need to have exiftool installed on your system for this to work.

Replace input.tif with the path and filename of your input TIF image, and output.jpg with the desired output filename.
