import csv
import exiftool

with open('OriginalTIFs.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Title'] == '2008-901':
            2008-901.tif = # Add the name of the corresponding TIFF file here
            with exiftool.ExifTool() as et:
                et.execute(b"-Credit=" + row['Credit'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-By-line=" + row['By-line'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-SpecialInstructions=" + row['SpecialInstructions'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-ObjectName=" + row['ObjectName'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-Writer-Editor=" + row['Writer-Editor'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-Source=" + row['Source'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-Headline=" + row['Headline'].encode('utf-8'), filename.encode('utf-8'))
                et.execute(b"-Caption-Abstract=" + row['Caption-Abstract'].encode('utf-8'), filename.encode('utf-8'))
            break

