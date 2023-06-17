import exiftool

filename = "output.jpg"

with exiftool.ExifTool() as et:
    # Set the Credit tag with the value HST for the TIFF file
    et.execute(b"-Credit=Harry S. Truman Library", filename.encode('utf-8'))
    et.execute(b"-By-line=    ", filename.encode('utf-8'))
    et.execute(b"-SpecialInstructions=1944", filename.encode('utf-8'))
    et.execute(b"-ObjectName=XXXX-XXX", filename.encode('utf-8'))
    et.execute(b"-Writer-Editor=LAA", filename.encode('utf-8'))
    et.execute(b"-Source=    ", filename.encode('utf-8'))
    et.execute(b"-Headline=    ", filename.encode('utf-8'))
    et.execute(b"-Caption-Abstract=    ", filename.encode('utf-8'))


    #et.execute(b"-By-line=    ", filename.encode('utf-8'))


