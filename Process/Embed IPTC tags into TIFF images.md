# Embed IPTC tags into TIFF images

Using the CSV file output from HST PDB, run the Python3 program write-tags-from-csv.py from the Windows CMD window:
```
python3 write-tags-from-csv.py
```
The program list each file found in the CSV file to the screen

Note: the top row [the column headers] of the CSV file needs to be edited to reflect the corresponding IPTC tag names:

- ObjectName
- Headline
- Credit
- By-line
- SpecialInstructions
- Writer-Editor
- Source
- Caption-Abstract
