#Move EXIF tags from TIFF to JPEG files

The following command move all EXIF tags, which includes IPTC tags, from TIFF files to corresponding JPEG files.  
This assumes the TIFF and corresponding JPEG files are in the current directory.

```
exiftool -ext tif -overwrite_original -TagsFromFile %d%f.tif "-all:all>all:all" -r -ext jpg /path/to/images
```
