## Truman Library PDB Metadata Tagging Process from the shared S: Drive

<p align="justify"> last update: 2024-12-17 1040 </p>

The following describes the steps to apply IPTC metadata tags to photos from the Truman Library Photo Database (PDB).

### Steps required before the tagging process can begin

Before the tagging process can begin, the following steps must be completed:

<p> - a CSV data file must be generated from the PDB that contains the metadata to be embedded in the TIFF and JPEG images </p>
<p> - JPEG images must be generated from the TIFF images </p>
<p> - JPEG images must be resized to 800 pixels max on either the X or Y axis </p>
<p> - Copyright watermarks must be added to restricted JPEG images </p>

### Tagging process

The directory <b>'S:\SCAN\HSTL-Metatagging\Photo'</b> on the shared S:drive has been set aside as the <b><i>working directory</i></b> where work associated with the HSTL photo metadata tagging process is performed.

1. Begin by copying the following required files to the <b>```S:\SCAN\HSTL-Metatagging\Photo```</b> directory:
    - CSV metadata file generated from the PDB
    - all the photos listed in the CSV metadata file
    
2. Open a Command Window by pressing the Windows Key + R, then type <b>```cmd```</b>.  The following new window should appear

     ![CMD Window](cmd-window.png)

     - Change to the Current Working Directory by entering:
  
     <b>``` S: <cr>``` </b>    [ changes to the S: drive ] 

     <b>``` cd SCAN\HSTL-Metatagging\Photo <cr>``` </b>    [ changes to the working directory ]

     - Next, enter:

     <b>```menu <cr>```</b> and the following should appear:

    ![menu](menu.png)
 
     - from this menu, all activities associated with metadata tagging can be performed
  
3. Check that all necessary Python files are installed

     - select <b>```1 <cr>``` </b>

     The message: ``` All files exist in the current directory. You are good to proceed to the next step.```  speaks for itself.

     If a message like this appears:

     ```The following file(s) do not exist in the current directory:```
         
      this is not good!!!! better call Jim :-) . . . [it's his fault]

      ... or you can try downloading ```install-files.py``` from the HST GitHub repository and run the command ```python install-files.py ``` in the current working directory

4.  Update headers on the CSV data file

     - select <b>```2 <cr>``` </b>
  
     - This step creates an ``` export.csv ``` file with the corrected header names that the tagging process requires.

5. Check for valid dates

     - select <b>```3 <cr>```</b> checks for valid dates
    
     ![date](date-check.png)

     Press the ```space bar``` to page through the output.  You are looking for any date in the Converted Date column that does not follow the YYYY-MM-DD format.

   In the above case, line 5 has an invalid date.  You can use MS Excel to edit the date in the <b>export.csv</b> file.

   When you are through reviewing the dates, press Q to exit this section and return to the menu.
   
7. Tag TIFF images

    - select <b>```4 <cr>```</b> Tag TIFF and JPEG files
    
     ![date](tagging.png)

    Note: ```Number of lines in the CSV file``` should equal  ```Number of tif files in the directory```

   Once you press ```Enter``` and start the processing, each image takes 1-2 seconds.

   When the processing is complete the following appears and a report is printed to the current working directory.

  ![date](post.png)

   Note: This report obviously contains some errors i.e. missing images - - here's hoping your run does not :-).
   
7. Tag JPEG images

    - select <b>```4 <cr>```</b> Tag TIFF and JPEG files
          
    - this should work exactly like the TIFF processing except you select JPEG on the opening menu
  
    Note: if at any time you need to interrupt the tagging process, you can do so by pressing <b>```CTRL + C```</b>.

   A message <b>```Terminate batch job (Y/N)?```</b> will appear.  Press Y and you will exit to the command line prompt.  

   Enter <b>```menu <cr>```</b> to restart the process.

 9. Post-processing spot checks

    <p> Post-processing review of TIFF and JPEG images can be easily accomplished using <b>nomacs</b>, an image viewer that allows metadata to be displayed next to the image. Nomacs is installed on the Scanning Workstation but you will need to configure nomacs.  You can do so by selecting <b>Panels</b> from the top menu and then tick <b>File Explorer</b> and <b>Metadata Info</b> options.  This will create a 3-panel view that allows you to review TIFF and JPEG images as shown below.</p>

    ![menu](nomacs-panels.png)

    <p>Some things to spot-check in processed TIFF and JPEG images:</p>

    - JPEG images should have a max 800 pixels on either the X or Y axis
    - copyright watermarks should have been added to appropriate JPEG images
    - IPTC metadata tags should have been applied to both JPEG and TIFF images
      
11. Post-processing file handling

    - move/save tagged TIFF and JPEG images to a 'shared drive' to clear space for the next batch of images to be processed.
    - move/save the REPORT files to an appropriate directory
    - move/save the PDB CSV file 
