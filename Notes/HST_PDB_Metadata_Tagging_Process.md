## Truman Library PDB Metadata Tagging Process

<p align="justify"> last update: 2023-12-08 1245 </p>

##### <i>[this documentation is preliminary - a work in progress]</i>

The following describes the steps to apply metadata tags to photos from the Truman Library Photo Database.

### Steps required before the tagging process

Prior to the tagging process

<p> - a CSV file will be generated from the PDB that contains the metadata to be embedded in the TIFF images to be processed </p>
<p> - JPEG images will be generated from the TIFF images </p>
<p> - JPEG images will be resized to 800 pixels max on either the X or Y axis.</p>
<p> - Copyright watermarks will be added to restricted JPEG images </p>

### Tagging process

The directory 'C:\Temp\Metadata-tagging' on the Scanning Workstation has been set aside as the <i>working directory</i> where work associated with the metadata tagging process is performed.

1. Begin by copying the following required files to the C:\Temp\Metadata-tagging directory:
    - CSV metadata file generated from the PDB
    - all the photos listed in the CSV metadata file
    
2. Open a Command Window by pressing Control + t.  The following should appear

     [insert a CMD window image here]

     At the CMD prompt, enter:

     ```menu```
 
     - from this menu, all activities associated with metadata tagging can be performed
  
3. Check that all necessary Python files are installed

     - select ```1 <cr>```  

4.  Update headers on CSV file

     - select ```2 <cr>```  

6. Check for valid dates

     - select ```3 <cr>``` Check for valid dates

7. Tag TIFF images

    - select ```4 <cr>``` Tag TIFF and JPEG files
    
8. Tag JPEG images

    - select ```4 <cr>``` Tag TIFF and JPEG files
          
    - this should work exactly like the TIFF processing except you select JPEG on the opening menu

9. Post-processing spot checks

    <p>Click [here](../Tools/nomacs/Configuring-nomacs.md) for how to configure nomac's 3-panel view</p>
     
    <p>Things to spot-check in TIFF and JPEG images</p>

    - JPEG images have a max 800 pixels on either the X or Y axis
    - copyright watermarks have been added to appropriate JPEG images
    - metadata tags have been applied to both JPEG and TIFF images
      
10. Post-processing file handling

    - move/save tagged TIFF and JPEF images to a 'shared drive' to clear space for the next batch of images to be processed.
    - move/save the REPORT files to an appropriate directory
