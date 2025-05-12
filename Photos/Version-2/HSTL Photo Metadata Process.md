<h3>HSTL Photo Metadata Process - Version 2 </h3>

- Create a Google Sheet from the NARA/HSTL Google Worksheet using the `File / Save as Google Sheet` feature

- Convert Google Sheet to a format used to embed metadata  [ Python code ]

      python google-to-csv.py  {Google Sheet URL}
  
    this step creates an `export.csv` a file containing the metadata to be embedded in TIFF images

<!--- Create IPTC metadata set for HST photos -->
 HSTL's IPTC tag set
 ```
           IPTC Tag Names                   HSTL PDB Labels
     - Caption-Abstract                : {description} e.g. Easter Egg Roll at the 2018 Harry's Hop'n Hunt.<br>
     _- Writer-Editor                   : {archivist/editor} e.g. LAA_
     - Headline                        : {title} e.g. 2018 Harry's Hop n' Hunt
     - By-line                         : {photographer}
     - By-line Title                   : {Institutional Creator}
     - Credit                          : {Credit} Harry S. Truman Library
     - Source                          : {collection} e.g. RG 64
     - Object Name                     : {Accession No} e.g' 2010-365
     - Copyright Notice                : {Restrictions} Public Domain - This item is in the public domain and can be used freely without further permission.
```

- Embed IPTC metadata tags to TIFF images  [ Python code ]

- Convert TIFF images to JPEG format [ ffmpeg ]
  
- Scale JPEG images to  max 800 pixels on X or Y axis  [ ffmpeg ]

- Add Copyright watermark to photos  [ ffmpeg ]
       copyright status information obtained from `Copyright Notice` tag
        


