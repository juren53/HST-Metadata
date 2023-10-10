## Truman Library PDB Metadata Tagging

<p align="justify"> 2023-10-10 </p>

[Preliminary - work in progress]

The following describes the steps to apply metadata tags to photos from the Truman Library Photo Database and to prepare JPEG images to be tagged and transmitted to NARA.

### Steps required before the tagging process

There are ~ 54,000 photos in the HST PDB that need to be tagged.  Adding metadata tags will probably occurr in batches of 3,000 - 5,000 photos.  Prior to the tagging process

<p> - a CSV file will be generated from the PDB that contains the metadata to be embedded in the TIFF images to be processed </p>
<p> - JPEG images will be generated from the TIFF images </p>
<p> - JPEG images will be resized to 800 pixel max on either the X or Y axis.</p>
<p> - Copyright watermarks will be added to restricted JPEG images </p>

### Tagging process

1. Establish the working directory and copy the required files:
    - CSV metadata file generated from the PDB
    - all the photos listed in the CSV metadata file
    - python programs
2. Check for valid dates in CSV file
    - open a Command Prompt Window from the Windows Start Menu
    - switch to the current working directory
    - run ```python check-csv-file.py | more``` from the current working directory
    - edit dates in the CSV file that do not conform to the YYYY-MM-DD format

4. Tag TIFF images
    - run ``` python write-tags-from-csv.py``` from the current working directory

5. Tag JPEG images
    - run ``` python write-tags-from-csv.py``` from the current working directory

6. Check images using nomacs

    <p>Click [here](https://github.com/juren53/HST-Metadata/blob/master/Tools/nomacs/Configuring-nomacs.md) for how to configure nomac's 3-panel view</p>
     
    <p>Things to spot check in TIFF and JPEG images</p>

    - JPEG images have a max 800 pixels on either the X or Y axis
    - copyright watermarks have been added to appropriate JPEG images
    - metadata tags have been applied to both JPEG and TIFF images
      
