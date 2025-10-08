import csv
import os
import pyexiv2

# Open the CSV file containing the metadata
with open('OriginalTIFs.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    # Loop through each row in the CSV file
    for row in reader:
        # Get the title of the TIFF file from the Title column
        title = row['Title']
        
        # Check if the TIFF file exists
        tiff_file = f"{title}.tif"
        if not os.path.exists(tiff_file):
            continue
        
        # Open the TIFF file and add the metadata as tags
        metadata = {
            'Xmp.dwc.title': row['Title'],
            'Iptc.Application2.Caption': row['Caption-Abstract'],
            'Iptc.Application2.Byline': row['By-line'],
            'Iptc.Application2.Credit': row['Credit'],
            'Iptc.Application2.ObjectName': row['Headline'],
            'Xmp.dc.source': row['Source'],
           # 'Xmp.dc.rights': row['Copyright Notice'],
           # 'Iptc.Application2.SpecialInstructions': row['SpecialInstructions'],
           # 'Xmp.dc.creator': row['Institutional Creator'],
            'Iptc.Application2.WriterEditor': row['Writer-Editor']
        }
        image = pyexiv2.ImageMetadata(tiff_file)
        image.read()
        image.modify_xmp(metadata)
        image.write()

