## Truman Library PDB Metadata Tagging

The following describes the steps to apply metadata tags to photos from the Truman Library Photo Database and to prepare JPEG images to be tagged and transmitted to NARA.

### Steps required before the tagging process

There are ~ 54,000 photos in the HST PDB that need to be tagged.  This will probably happen in batches of 3,000 - 5,000 photos.  Prior to the tagging process

<p> - a CSV file will be generated from the PDB that contains the metadata to be embedded in the TIFF images to be processed </p>
<p> - JPEG images will be generated from the TIFF images </p>
<p> - JPEG images will be resized to 800 pixel max on either the X or Y axis.</p>

### Tagging process

1. Establish the working directory and copy the required files:
    - CSV metadata file generated from the PDB
    - all the photos listed in the CSV metadata file
    - python programs
2. Check for valid dates in CSV file
    - open a Command Prompt Window from the Windows Start Menu
    - switch to the current working directory
    - run ```python check-csv-file.py``` from the current working directory

4. Tag TIFF images
    - run ``` python write-tags-from-csv.py``` from the current working directory

6. Tag JPEG images
    - run ``` python write-tags-from-csv.py``` from the current working directory

8. Check images
    Things to spot check in TIFF and JPEG images
    - JPEG images have a max 800 pixels on either the X or Y axis
    - metadata tags have been applied to both JPEG and TIFF images
      
