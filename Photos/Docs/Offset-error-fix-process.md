### Description of Process to Fix Offset Errors and Warnings in JPEG images

The following steps fix the offset errors and warning messages associated with JPEG image files reported by
ExifTool and exiv2 metadata utilities. These steps outline how a program would automate the process and 
make the JPEG images viewable in the NARA Catalog. This process assumes that HSTL compressed JPEG images are 
intended for efficient Web access and the larger TIFF master files are off-line, available on request from HSTL A/V Archives.

1. Remove all metadata tags in 'post-processed.jpg' file using FFmpeg. Note: all EXIF and XMP meta will be available in the TIFF master file.
```
    ffmpeg -i {accession-no}.jpg output.jpg
```
2. Copy 'post-processed.jpg' to temporary input file using a copy command.
```
    cp {accession-no}.jpg input.jpg
```
3. Extract IPTC metadata from 'post-processed.jpg' and then embed it into 'output.jpg' using ExifTool.
```
    exiftool -tagsfromfile input.jpg -IPTC:all output.jpg
```
4. Copy output.jpg to original filename {accession-no}.jpg using copy command
```
    cp output.jp {accession-no}.jpg
```
5. Confirm 0 errors/warnings in new JPEG file using ExifTool
```
    exiftool -validate -warning -error -a {accession-no}.jpg
```
6. List IPTC metadata in new JPEG file using ExifTool
```
    exiftool -a -G0:1 -s {accession-no}.jpg
```
   <sub> Mon 27 May 2024 05:46:42 PM CDT </sub>
