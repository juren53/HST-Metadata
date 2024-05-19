### ExifTool Commands

##### ExifTool Validation/Error Checking Command:

ExifTool can list just the error and warning messages for each file in a directory
```
exiftool -validate -warning -error -a *.jpg 
```
produces a report that look like:
```

======== 85-8-1.jpg
Validate                        : OK
======== 85-8-2.jpg
Validate                        : OK
======== 72-3113.jpg
Validate                        : 2 Warnings (1 minor)
Warning                         : IPTCDigest is not current. XMP may be out of sync
Warning                         : [minor] XMP is missing xpacket wrapper
======== 2022-747_800pixels.jpg
Validate                        : 15 Warnings (12 minor)
Warning                         : [minor] Odd offset for IFD0 tag 0x0132 ModifyDate
Warning                         : [minor] Odd offset for IFD0 tag 0x013b Artist
Warning                         : [minor] Odd offset for IFD0 tag 0x8298 Copyright
Warning                         : [minor] IPTC TimeCreated too short (6 bytes; should be 11)
Warning                         : Missing required JPEG ExifIFD tag 0x9000 ExifVersion
Warning                         : Missing required JPEG ExifIFD tag 0x9101 ComponentsConfiguration
Warning                         : Missing required JPEG ExifIFD tag 0xa000 FlashpixVersion
Warning                         : [minor] IFD0 tag 0x0100 ImageWidth is not allowed in JPEG
Warning                         : [minor] IFD0 tag 0x0101 ImageHeight is not allowed in JPEG
Warning                         : [minor] IFD0 tag 0x0102 BitsPerSample is not allowed in JPEG
Warning                         : [minor] IFD0 tag 0x0103 Compression is not allowed in JPEG
Warning                         : [minor] IFD0 tag 0x0106 PhotometricInterpretation is not allowed in JPEG
Warning                         : [minor] IFD0 tag 0x0115 SamplesPerPixel is not allowed in JPEG
Warning                         : [minor] IFD0 tag 0x011c PlanarConfiguration is not allowed in JPEG
Warning                         : [minor] Missing required JPEG IFD0 tag 0x0213 YCbCrPositioning
```

##### exiv2 Error & Warning Listing:

The following command lists all the errors and warnings for an image file

```
exiv2 -pa -k "warning" -k "error" <path_to_your_image.jpg>
```

```
error" 72-88.jpg
warning: Failed to open the file
-k: Failed to open the file
error: Failed to open the file
Warning: Directory Image, entry 0x0111: Strip 0 is outside of the data area; ignored.
Error: Directory Image, entry 0x8769 Sub-IFD pointer 0 is out of bounds; ignoring it.
Warning: Ignoring XMP information encoded in the Exif data.
72-88.jpg             Exif.Image.NewSubfileType                    Long        1  Primary image
72-88.jpg             Exif.Image.ImageWidth                        Long        1  645
72-88.jpg             Exif.Image.ImageLength                       Long        1  800
72-88.jpg             Exif.Image.BitsPerSample                     Short       1  8
72-88.jpg             Exif.Image.Compression                       Short       1  Uncompressed
72-88.jpg             Exif.Image.PhotometricInterpretation         Short       1  Black Is Zero
72-88.jpg             Exif.Image.StripOffsets                      Long        1  11442
72-88.jpg             Exif.Image.SamplesPerPixel                   Short       1  1
72-88.jpg             Exif.Image.RowsPerStrip                      Short       1  2925
72-88.jpg             Exif.Image.StripByteCounts                   Long        1  6894225
72-88.jpg             Exif.Image.XResolution                       Rational    1  100
72-88.jpg             Exif.Image.YResolution                       Rational    1  100
72-88.jpg             Exif.Image.ResolutionUnit                    Short       1  inch
72-88.jpg             Exif.Image.Software                          Ascii      29  Adobe Photoshop Elements 2.0
72-88.jpg             Exif.Image.DateTime                          Ascii      20  2012:05:14 08:31:32
72-88.jpg             Exif.Image.XMLPacket                         Byte      5036  60 63 120 112 97 99 107 101 116 32 98 101 103 105 110 61 39 239 187 191 39 32 105 100 61 39 87 53 77 .
72-88.jpg             Exif.Image.ImageResources                    Byte      6110  56 66 73 77 4 37 0 0 0 0 0 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 56 66 73 77 3 237 0 0 0 0 0 16 1 44 0  
72-88.jpg             Exif.Image.ExifTag                           Long        1  6905668

```

##### ExifTool Detailed Listing:

ExifTool can report a detailed list of all tags, pesudo tags and waring or error messages showing which group each tag belongs too. 
```
exiftool -a -G0:1 -s *.jpg|more
```
produces a report that looks like:
```
======== 84-06-02.jpg
[ExifTool]      ExifToolVersion                 : 12.70
[ExifTool]      Warning                         : Bad ExifOffset SubDirectory start
[ExifTool]      Warning                         : IPTCDigest is not current. XMP may be out of sync
[File:System]   FileName                        : 84-06-02.jpg
[File:System]   Directory                       : .
[File:System]   FileSize                        : 422 kB
[File:System]   FileModifyDate                  : 2023:08:11 12:58:06-05:00
[File:System]   FileAccessDate                  : 2024:04:26 19:49:20-05:00
[File:System]   FileInodeChangeDate             : 2023:11:28 19:01:09-06:00
[File:System]   FilePermissions                 : -rw-r--r--
[File]          FileType                        : JPEG
[File]          FileTypeExtension               : jpg
[File]          MIMEType                        : image/jpeg
[File]          ExifByteOrder                   : Little-endian (Intel, II)
[File]          CurrentIPTCDigest               : 6084be7016f0309f6c4d7fefec2af4f4
[File]          ImageWidth                      : 800
[File]          ImageHeight                     : 648
[File]          EncodingProcess                 : Progressive DCT, Huffman coding
[File]          BitsPerSample                   : 8
[File]          ColorComponents                 : 3
[File]          YCbCrSubSampling                : YCbCr4:2:0 (2 2)
[JFIF]          JFIFVersion                     : 1.01
[JFIF]          ResolutionUnit                  : inches
[JFIF]          XResolution                     : 100
[JFIF]          YResolution                     : 100
[EXIF:IFD0]     SubfileType                     : Full-resolution image
[EXIF:IFD0]     ImageWidth                      : 800
[EXIF:IFD0]     ImageHeight                     : 648
[EXIF:IFD0]     BitsPerSample                   : 8 8 8
[EXIF:IFD0]     Compression                     : Uncompressed
[EXIF:IFD0]     PhotometricInterpretation       : RGB
[EXIF:IFD0]     StripOffsets                    : 26922
[EXIF:IFD0]     Orientation                     : Horizontal (normal)
[EXIF:IFD0]     SamplesPerPixel                 : 3
[EXIF:IFD0]     RowsPerStrip                    : 2379
[EXIF:IFD0]     StripByteCounts                 : 20961369
[EXIF:IFD0]     XResolution                     : 100
[EXIF:IFD0]     YResolution                     : 100
[EXIF:IFD0]     PlanarConfiguration             : Chunky
[EXIF:IFD0]     ResolutionUnit                  : inches
[EXIF:IFD0]     Software                        : Adobe Photoshop CS6 (Windows)
[EXIF:IFD0]     ModifyDate                      : 2016:05:02 10:33:08
[XMP:XMP-x]     XMPToolkit                      : Adobe XMP Core 5.3-c011 66.145661, 2012/02/06-14:56:27
[XMP:XMP-xmp]   CreatorTool                     : Adobe Photoshop CS6 (Windows)
[XMP:XMP-xmp]   CreateDate                      : 2016:05:02 10:33:08-05:00
[XMP:XMP-xmp]   MetadataDate                    : 2016:05:02 10:33:08-05:00
[XMP:XMP-xmp]   ModifyDate                      : 2016:05:02 10:33:08-05:00
[XMP:XMP-dc]    Format                          : image/tiff
[XMP:XMP-xmpMM] InstanceID                      : xmp.iid:4B8BBEC07A10E611899AAEEE00E10DA8
[XMP:XMP-xmpMM] DocumentID                      : xmp.did:4B8BBEC07A10E611899AAEEE00E10DA8
[XMP:XMP-xmpMM] OriginalDocumentID              : xmp.did:4B8BBEC07A10E611899AAEEE00E10DA8
[XMP:XMP-xmpMM] HistoryAction                   : created
[XMP:XMP-xmpMM] HistoryInstanceID               : xmp.iid:4B8BBEC07A10E611899AAEEE00E10DA8
[XMP:XMP-xmpMM] HistoryWhen                     : 2016:05:02 10:33:08-05:00
[XMP:XMP-xmpMM] HistorySoftwareAgent            : Adobe Photoshop CS6 (Windows)
[XMP:XMP-photoshop] ColorMode                   : RGB
[XMP:XMP-photoshop] ICCProfileName              : sRGB IEC61966-2.1
[Photoshop]     IPTCDigest                      : 00000000000000000000000000000000
[Photoshop]     XResolution                     : 300
[Photoshop]     DisplayedUnitsX                 : inches
[Photoshop]     YResolution                     : 300
[Photoshop]     DisplayedUnitsY                 : inches
[Photoshop]     PrintStyle                      : Centered
[Photoshop]     PrintPosition                   : 0 0
[Photoshop]     PrintScale                      : 1
[Photoshop]     GlobalAngle                     : 4294967146
[Photoshop]     GlobalAltitude                  : 30
[Photoshop]     URL_List                        : 
[Photoshop]     SlicesGroupName                 : 
[Photoshop]     NumSlices                       : 1
[Photoshop]     PixelAspectRatio                : 1
[Photoshop]     PhotoshopThumbnail              : (Binary data 7083 bytes, use -b option to extract)
[Photoshop]     HasRealMergedData               : Yes
[Photoshop]     WriterName                      : Adobe Photoshop
[Photoshop]     ReaderName                      : Adobe Photoshop CS6
[ICC_Profile:ICC-header] ProfileCMMType         : Linotronic
[ICC_Profile:ICC-header] ProfileVersion         : 2.1.0
[ICC_Profile:ICC-header] ProfileClass           : Display Device Profile
[ICC_Profile:ICC-header] ColorSpaceData         : RGB
[ICC_Profile:ICC-header] ProfileConnectionSpace : XYZ
[ICC_Profile:ICC-header] ProfileDateTime        : 1998:02:09 06:49:00
[ICC_Profile:ICC-header] ProfileFileSignature   : acsp
[ICC_Profile:ICC-header] ConnectionSpaceIlluminant: 0.9642 1 0.82491
[ICC_Profile:ICC-header] ProfileCreator         : Hewlett-Packard
[ICC_Profile:ICC-header] ProfileID              : 0
[ICC_Profile]   ProfileCopyright                : Copyright (c) 1998 Hewlett-Packard Company
[ICC_Profile]   ProfileDescription              : sRGB IEC61966-2.1
[ICC_Profile]   MediaWhitePoint                 : 0.95045 1 1.08905
[ICC_Profile]   MediaBlackPoint                 : 0 0 0
[ICC_Profile]   RedMatrixColumn                 : 0.43607 0.22249 0.01392
[ICC_Profile]   GreenMatrixColumn               : 0.38515 0.71687 0.09708
[ICC_Profile]   BlueMatrixColumn                : 0.14307 0.06061 0.7141
[ICC_Profile]   DeviceMfgDesc                   : IEC http://www.iec.ch
[ICC_Profile]   DeviceModelDesc                 : IEC 61966-2.1 Default RGB colour space - sRGB
[ICC_Profile]   ViewingCondDesc                 : Reference Viewing Condition in IEC61966-2.1
[ICC_Profile]   Luminance                       : 76.03647 80 87.12462
[ICC_Profile]   Technology                      : Cathode Ray Tube Display
[ICC_Profile]   RedTRC                          : (Binary data 2060 bytes, use -b option to extract)
[ICC_Profile]   GreenTRC                        : (Binary data 2060 bytes, use -b option to extract)
[ICC_Profile]   BlueTRC                         : (Binary data 2060 bytes, use -b option to extract)
[ICC_Profile:ICC-view] ViewingCondIlluminant    : 19.6445 20.3718 16.8089
[ICC_Profile:ICC-view] ViewingCondSurround      : 3.92889 4.07439 3.36179
[ICC_Profile:ICC-view] ViewingCondIlluminantType: D50
[ICC_Profile:ICC-meas] MeasurementObserver      : CIE 1931
[ICC_Profile:ICC-meas] MeasurementBacking       : 0 0 0
[ICC_Profile:ICC-meas] MeasurementGeometry      : Unknown
[ICC_Profile:ICC-meas] MeasurementFlare         : 0.999%
[ICC_Profile:ICC-meas] MeasurementIlluminant    : D65
[IPTC]          Headline                        : Rear of Truman Home in Snow
[IPTC]          ApplicationRecordVersion        : 4
[IPTC]          Credit                          : Harry S. Truman Library
[IPTC]          SpecialInstructions             : None
[IPTC]          ObjectName                      : 84-06-02
[IPTC]          Source                          : HST Papers: Family, Business, an
[IPTC]          Caption-Abstract                : Rear of the Truman home showing steps leading down from the back porch and the arbor in the backyard.  The house is in snow, taken some time before 1954.  The photo is from original slide 2119.  From:  Truman house.
[IPTC]          DateCreated                     : 0000:00:00
[IPTC]          CopyrightNotice                 : Unrestricted
[Composite]     ImageSize                       : 800x648
[Composite]     Megapixels                      : 0.518


```
