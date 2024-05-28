### Description of Process to Fix Offset Errors and Warnings in JPEG images

The following steps fix the offset errors and warning messages associated with JPEG image files reported by
ExifTool and exiv2 metadata utilities. These steps outline how a program would automate the process and 
make the JPEG images viewable in the NARA Catalog.

1. Remove all metadata tags in post-processed JPEG using FFmpeg
```
    ffmpeg -i {accession-no}.jpg output.jpg
```
2. copy post-processed.jpg to temporary input file using copy command
```
    cp {accession-no}.jpg input.jpg
```
3. extract IPTC tags from post-processed.jpg and embed tags into output.jpg using ExifTool
```
    exiftool -tagsfromfile input.jpg -IPTC:all output.jpg
```
4. copy output.jpg to original filename {accession-no}.jpg using copy command
```
    cp output.jp {accession-no}.jpg
```
5. confirm 0 errors/warnings in new JPEG file using ExifTool
```
    exiftool -validate -warning -error -a {accession-no}.jpg
```
6. list IPTC metadata in new JPEG file using ExifTool
```
    exiftool -a -G0:1 -s {accession-no}.jpg
```
   <sub> Mon 27 May 2024 05:46:42 PM CDT </sub>
