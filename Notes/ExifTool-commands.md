### ExifTool Commands

ExifTool Validation/Error Checking Command:
```
exiftool -validate -warning -error -a *.jpg | less
```
ExifTool Detailed Listing:
```
exiftool -a -G0:1 -s *.jpg|more
```
