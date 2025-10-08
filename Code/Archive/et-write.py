import exiftool

with exiftool.ExifTool() as et:
    # Set the Credit tag with the value HST for the TIFF file
    et.execute(b"-Credit=Harry S. Truman Library", b"2022-747.tif")
    et.execute(b"-By-line=   ", b"2022-747.tif")
    et.execute(b"-SpecialInstructions=1944", b"2022-747.tif")
    et.execute(b"-ApplicationRecordVersion=", b"2022-747.tif")

