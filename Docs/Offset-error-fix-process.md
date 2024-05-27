### Description of Process to Fix Offset Errors and Warnings in JPEG images

The following steps fixthe offset errors and warning messages reported by
ExifTool and exiv2 metadata utilities and outlines how a Python program should work

Remove all meta-tags and fix offset errors in post-processed JPEG using FFmpeg
```
    ffmpeg -i {accession-no}.jpg output.jpg
```
copy post-processed.jpg to temporary input file using copy command
```
    cp {accession-no}.jpg input.jpg
```
extract IPTC tags from post-processed.jpg and embedd tags into output.jpg using ExifTool
```
    exiftool -tagsfromfile input.jpg -IPTC:all output.jpg
```
copy output.jpg to original filename {accession-no}.jpg using copy command
```
    cp output.jp {accession-no}.jpg
```
confirm 0 errors/warnings in new JPEG file using ExifTool
```
    exiftool -validate -warning -error -a {accession-no}.jpg
```
list IPTC metadata in new JPEG file using ExifTool
```
    exiftool -a -G0:1 -s {accession-no}.jpg
```
