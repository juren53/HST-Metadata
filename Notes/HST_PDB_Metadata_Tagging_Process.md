## Truman Library PDB Metadata Tagging Process

<p align="justify"> last update: 2023-12-09 1225 </p>

The following describes the steps to apply metadata tags to photos from the Truman Library Photo Database.

### Steps required before the tagging process

Prior to the tagging process

<p> - a CSV file must be generated from the PDB that contains the metadata to be embedded in the TIFF and JPEG images to be processed </p>
<p> - JPEG images must be generated from the TIFF images </p>
<p> - JPEG images must be resized to 800 pixels max on either the X or Y axis.</p>
<p> - Copyright watermarks must be added to restricted JPEG images </p>

### Tagging process

The directory <b>'C:\Temp\Metadata-tagging'</b> on the Scanning Workstation has been set aside as the <i>working directory</i> where work associated with the metadata tagging process is performed.

1. Begin by copying the following required files to the ```C:\Temp\Metadata-tagging``` directory:
    - CSV metadata file generated from the PDB
    - all the photos listed in the CSV metadata file
    
2. Open a Command Window by pressing the Windows Key + R, then type "cmd.".  The following should appear

     ![CMD Window](cmd-window.png)

     A the CMD prompt, enter:

     <b>``` cd c:\Temp\Metadata-tagging <cr>``` </b>    [ changes to the working directory ]

     Next enter:

     <b>```menu <cr>```</b>

    ![menu](menu.png)
 
     - from this menu, all activities associated with metadata tagging can be performed
  
4. Check that all necessary Python files are installed

     - select <b>```1 <cr>``` </b>

     The message: ```All files exist in the current directory. You are good to proceed to the next step.```  speaks for itself.

     If a message like appears:
   
      ```The following file(s) do not exist in the current directory:
          - write-tags-from-csv.py```

      this is not good - - better call Jim :-)

6.  Update headers on CSV file

     - select <b>```2 <cr>``` </b> 

7. Check for valid dates

     - select <b>```3 <cr>```</b> checks for valid dates
    
     ![date](date-check.png)

     Press the ```space bar``` to page through the output.  You are looking for any date in the Converted Date column that does not follow the YYYY-MM--DD format.

   In the above case, line 5 has an invalid date.  You can use MS Excel to edit the date in the <b>export.csv</b> file.  
   
8. Tag TIFF images

    - select <b>```4 <cr>```</b> Tag TIFF and JPEG files
    
     ![date](tagging.png)

    Note: ```Number of lines in the CSV file``` should equal  ```Number of tif files in the directory```

   Once you press ```Enter``` and start the processing, each image takes 1-2 seconds.

   When the processing is complete the following appears and a report is printed to the current working directory.

  ![date](post.png)
   
9. Tag JPEG images

    - select <b>```4 <cr>```</b> Tag TIFF and JPEG files
          
    - this should work exactly like the TIFF processing except you select JPEG on the opening menu

10. Post-processing spot checks

    <p>Click [here](../Tools/nomacs/Configuring-nomacs.md) for how to configure nomac's 3-panel view</p>
     
    <p>Things to spot-check in processed TIFF and JPEG images</p>

    - JPEG images have a max 800 pixels on either the X or Y axis
    - copyright watermarks have been added to appropriate JPEG images
    - metadata tags have been applied to both JPEG and TIFF images
      
11. Post-processing file handling

    - move/save tagged TIFF and JPEF images to a 'shared drive' to clear space for the next batch of images to be processed.
    - move/save the REPORT files to an appropriate directory
