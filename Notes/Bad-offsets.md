### Discovery of Bad Offsets and other Bad Actors in JPEG images

The following are a collection of bash scripts that reveal bad offsets and other malformed metadata 
in JPEG images using exiftool and various bash utilities 
that create problems when uploaded
to the Catalog

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

