<h3>HST Photo Metadata Process - Version 2 </h3>

- Save NARA/HSTL Google Worksheet as a Googlesheet

- Copy and Paste the Googlesheet URL when running   [ Python code ]

      python google-to-csv.py  {Googlesheet URL}
  
    this creates an export.csv file from the Googlesheet

- Create IPTC metadata set for HST photos
   
   HSTL's IPTC tag set
 ```
           IPTC Tag Names                   HSTL PDB Labels
     - Caption-Abstract                : {description} e.g. Easter Egg Roll at the 2018 Harry's Hop'n Hunt.<br>
     - Writer-Editor                   : {archivist/editor} e.g. LAA
     - Headline                        : {title} e.g. 2018 Harry's Hop n' Hunt
     - By-line                         : {photographer}
     - By-line Title                   : {Institutional Creator}
     - Credit                          : {Credit} Harry S. Truman Library
     - Source                          : {collection} e.g. RG 64
     - Object Name                     : {Accession No} e.g' 2010-365
     - Copyright Notice                : {Restrictions} Public Domain - This item is in the public domain and can be used freely without further permission.
```

- Add IPTC metadata tags to TIFF images  [ Python code ]

- Convert TIFF images to JPEG format  [ ffmeg ]
  
- Scale JPEG images to  max 800 pixels on X or Y axis  [ ffmeg ]

- Add Copyright watermark to 'restricted' photos  [ ffmeg ]


