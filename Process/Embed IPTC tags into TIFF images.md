# Embed IPTC tags into TIFF images

Using the CSV file output from HST PDB, the Python3 program, *write-tags-from-csv.py*, extracts IPTC tags from the CSV file and embeds the IPTC tags into each TIFF file in the the current directory


Note: the top row [column headers] of the CSV file needs to be edited to reflect the corresponding IPTC tag names before the command listed below is run:

- ObjectName
- Headline
- Credit
- By-line
- SpecialInstructions
- Writer-Editor
- Source
- Caption-Abstract

Once the CSV file headers have been edited, execute the following command from the Windows CMD window in the directory with (1) all the TIFF images, (2) the edited CSV file and (3) the Python program, *write-tags-from-csv.py* :

```
python3 write-tags-from-csv.py
```
The program lists each file found in the CSV file to the screen.
