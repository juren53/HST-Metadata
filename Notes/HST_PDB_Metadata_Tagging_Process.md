## Truman Library PDB Metadata Tagging

<p align="justify"> last update: 2023-10-16 1850 </p>

##### <i>[this documentation is preliminary - work in progress]</i>

The following describes the steps to apply metadata tags to photos from the Truman Library Photo Database and to prepare JPEG images to be tagged and transmitted to NARA.

### Steps required before the tagging process

There are ~ 54,000 photos in the HST PDB that need to be tagged.  Adding metadata tags will probably occurr in batches of 3,000 - 5,000 photos.  Prior to the tagging process

<p> - a CSV file will be generated from the PDB that contains the metadata to be embedded in the TIFF images to be processed </p>
<p> - JPEG images will be generated from the TIFF images </p>
<p> - JPEG images will be resized to 800 pixel max on either the X or Y axis.</p>
<p> - Copyright watermarks will be added to restricted JPEG images </p>

### Tagging process

The directory 'C:\Temp\Metadata-tagging' on the Scanning Workstation has been set aside as the <i>working directory</i> for the metadata tagging process.

1. Begin by copying he following required files to the C:\Temp\Metadata-tagging directory:
    - CSV metadata file generated from the PDB
    - all the photos listed in the CSV metadata file
    - the required python programs [ check-csv-file.py & write-tags-from-csv.py ]

2. Open a Command Window by pressing Control + t.  The following should appear

     [insert a CMD window image here]

     At the CLI prompt, enter:

     ```cd C:\Temp\Metadata-tagging```

3. Check for valid dates in CSV file
    
    - from the current working directory, run:
      
      ```python check-csv-file.py | more```
      
 
     - edit dates in the CSV file that do not conform to the YYYY-MM-DD format

6. Tag TIFF images

    - from the current working directory, run:

      ``` python write-tags-from-csv.py``` from the current working directory
      
      [insert the opening screen from write-tags-from-csv.py]

7. Tag JPEG images
    - from the current working directory, run:
    
      ``` python write-tags-from-csv.py``` from the current working directory
      
    - this should work exactly like the TIFF processing except you select JPEG on the opening menu

8. Post-processing spot checks using nomacs

    <p>Click [here](../Tools/nomacs/Configuring-nomacs.md) for how to configure nomac's 3-panel view</p>
     
    <p>Things to spot check in TIFF and JPEG images</p>

    - JPEG images have a max 800 pixels on either the X or Y axis
    - copyright watermarks have been added to appropriate JPEG images
    - metadata tags have been applied to both JPEG and TIFF images
      
