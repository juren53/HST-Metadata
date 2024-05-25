## CLI Image Metadata Commands

The following is a list of CLI comands with brief descriptions to aid in viewing and diagnosing metadata issues.  

CLI - Commands Line Interface i.e. terminal commands.

| Commands | Description |
|:------|---------------|
|       |ExifTool commands|
| exiftool -a -G0:1 -s *.jpg | Detail metadata listing  (ExifTool)           |
| exiftool -iptc:all *.jpg|  List just IPTC tags (ExifTool)             |
| exiftool -validate -warning -error -a *.jpg | Detailed metadata error/warning listing  (ExifTool)              |
|       |exiv2 commands|
| exiv2 -pt *.jpg    |   Detail metadata listing  (exiv2)              |
| exiv2 -pa -k "warning" -k "error" *.jpg|  Detailed metadata error/warning listing  (exiv2)             |
|     -|               |
| exiftool -tagsfromfile input.jpg -IPTC:all output.jpg | Extracts just IPTC tags from input.jpg and embeds them in output.jpg   |


Fri 24 May 2024 03:17:35 PM CDT
