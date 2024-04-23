### Discovery of Bad Offsets and other Malformed Metadata in JPEG images

The following are a collection of bash scripts using ExifTool and various bash utilities that assist in revealing bad offsets and other malformed metadata
in JPEG images that create problems when uploaded to the Catalog. 
<br>

The BlackBoxAI bot reports:
<br>

"The Bad offset for IFD0 ICC_Profile error message suggests that the offset (i.e., the starting position) of the ICC_Profile tag in the IFD0 directory is incorrect or invalid. This can happen if the file has been corrupted or damaged in some way, or if it has been created using an unsupported or non-standard format."
<br>

Phil Harvery, the ExifTool author  [ and a real live human :-)  ] said in the ExifTool Forum:
<br>

" Errors like this may be repaired in JPEG images, but not TIFF images.  The image itself is stored in the IFD for TIFF images, so trying to repair IFD errors has too high a likelihood of corrupting the image."
<br>


```
for file in *.jpg; do
  echo "################"
  echo $file
  echo -n "Number of tags:     "; exiftool -s3 -G1 -n "$file" | wc -l
  exiftool "$file" | grep Modify
done
```

```
for file in *.jpg; do
  echo -n "Number of tags for $file: "; exiftool -s3 -G1 -n "$file" | wc -l
  echo
done
```

```
for file in *.jpg; do
  echo "################"
  echo $file
  exiftool "$file" | grep "Warning"
done
```



Bad offset for IFD0 ICC_Profile


```
for file in *.jpg; do
  echo "################"
  echo $file
  exiftool "$file" | grep "Bad offset for IFD0 ICC_Profile"
done
```


```
for file in *.jpg; do
  echo "################"
  echo $file
  echo -n "Number of tags:     "; exiftool -s3 -G1 -n "$file" | wc -l
  exiftool "$file" | grep Modify
  exiftool "$file" | grep Warning
done
```

Loops through all the JPEGs in the current directory printing the filename, number of tags, Modify Date [if it finds one] and the Warning tag [if it finds one].

  72-1883.jpg  <br>
  Number of tags:     89 <br>
  Modify Date                     : 2023:04:28 09:56:58 <br>
  Warning : Bad ExifOffset SubDirectory start <br>

