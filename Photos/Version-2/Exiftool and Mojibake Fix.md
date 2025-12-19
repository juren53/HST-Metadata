# Exiftool and Mojibake Fix

ExifTool does not have a specific built-in function called a "mojibake fixer," but it provides options and flexibility that can help address issues related to incorrect character encoding (mojibake) in metadata. [1]  
Mojibake typically occurs when text is decoded using an incorrect character encoding, resulting in unreadable characters. ExifTool's ability to read, write, and manipulate metadata, along with its options for handling encoding and offsets, can be used to correct such problems. [1, 2, 3, 4, 5]  
Here's how ExifTool relates to character encoding issues: 

• Metadata Manipulation: ExifTool allows users to extract metadata and write it back in a different format or encoding if necessary. 
•  Option for Offsets: In cases where incorrect offsets in maker notes lead to data corruption, the  option can be used to attempt to fix these offsets. While this is primarily for structural issues in the metadata rather than character encoding, it addresses a related type of "fixer" functionality. 
• Specific Encoding Handling: ExifTool can handle various character encodings for different metadata types, such as IPTC character coding. Users can often specify or manage how character sets are handled through various command-line options within the ExifTool application documentation. 
• Custom Scripts: Advanced users can use ExifTool within custom scripts (e.g., Perl) to detect, extract, and re-encode metadata strings that have turned into mojibake using external encoding conversion tools (like ). [1, 2, 6, 7, 8]  

For a dedicated, simple "mojibake fixer" for specific use cases like ZIP file names, separate web-based tools exist, such as the ZIP Mojibake Fixer, but these are not part of the ExifTool software itself. [9]  

AI responses may include mistakes.

[1] https://en.wikipedia.org/wiki/ExifTool
[2] https://superuser.com/questions/1639828/how-to-fix-hebrew-mojibake-in-old-files
[3] https://en.wikipedia.org/wiki/Mojibake
[4] https://www.globalizationpartners.com/2021/06/03/mojibake-question-marks-strange-characters-and-other-issues/
[5] https://cran.r-project.org/web/packages/exiftoolr/refman/exiftoolr.html
[6] https://exiftool.org/faq.html
[7] https://skylight.middlebury.edu/~schar/colormatching/software/Image-ExifTool-7.67/html/faq.html
[8] https://en.wikipedia.org/wiki/ExifTool
[9] https://ianharmon.github.io/mojibake-fixer/


------------------------------------------------------------------------------------------

 "How does ExifTool handle coded character sets?"

[Also see FAQ number 18 for help with special characters in a Windows console.]
Certain meta information formats allow coded character sets other than plain ASCII. When reading, most known encodings are converted to the external character set according to the exiftool "-charset CHARSET" or -L option, or to UTF‑8 by default. When writing, the inverse conversion is performed. Alternatively, special characters may be converted to/from HTML character entities with the -E option.
A distinction is made between the external character set visible to the ExifTool user, and the internal character used to store text in the metadata of a file. These character sets may be specified separately as follows:
The external character set for tag values passed to/from ExifTool is UTF‑8 by default, but it may be changed through any of these command-line options:
-charset CHARSET   or   -charset exiftool=CHARSET   or   -L
The encoding of file and directory names (eg. the FILE argument on the command line) is different. By default, these names are passed straight through to the standard C I/O routines without recoding. On Mac/Linux these routines expect UTF‑8, but on Windows they use the system code page (which is dependent on your system settings). However, as of ExifTool 9.79, the external filename encoding may be specified:
-charset filename=CHARSET
When this is done, file and directory names are converted from the specified encoding to one appropriate for system I/O routines. In Windows, this also has the effect of enabling Unicode filename support via the special Windows wide-character I/O routines if the required Perl modules are available (these are included in the Windows executable version of ExifTool). See WINDOWS UNICODE FILE NAMES in the application documentation for more details.

The internal character set for strings stored in file metadata may be specified for some metadata types:
-charset TYPE=CHARSET
(where TYPE is "exif", "iptc", "id3", "photoshop", "quicktime" or "riff")
Valid CHARSET values are (with aliases given in brackets, case is not significant):
UTF8	(cp65001, UTF‑8)	DOSLatinUS	(cp437)
Latin	(cp1252, Latin1)	DOSLatin1	(cp850)
Latin2	(cp1250)	DOSCyrillic	(cp866)
Cyrillic	(cp1251, Russian)     	MacRoman	(cp10000, Mac, Roman)
Greek	(cp1253)	MacLatin2	(cp10029)
Turkish	(cp1254)	MacCyrillic	(cp10007)
Hebrew	(cp1255)	MacGreek	(cp10006)
Arabic	(cp1256)	MacTurkish	(cp10081)
Baltic	(cp1257)	MacRomanian	(cp10010)
Vietnam	(cp1258)	MacIceland	(cp10079)
Thai	(cp874)	MacCroatian	(cp10082)
The -L option is equivalent to "-charset Latin", "-charset Latin1" and "-charset cp1252".
Type-specific details are given below about the special character handling for EXIF, IPTC, XMP, PNG, ID3, PDF, Photoshop, QuickTime, AIFF, RIFF, MIE and Vorbis information:
EXIF: Most textual information in EXIF is stored in ASCII format (called "string" in the EXIF Tags documentation). By default ExifTool does not convert these strings. However, it is not uncommon for applications to write UTF‑8 or other encodings where ASCII is expected. To deal with these, ExifTool allows the internal EXIF string encoding to be specified with "-charset exif=CHARSET", which causes EXIF string values to be converted from the specified character set when reading, and stored with this character set when writing. The MWG recommends using UTF‑8 encoding for EXIF strings, and in keeping with this the "-use mwg" feature sets the default internal EXIF string encoding to UTF‑8 (ie. "-charset exif=utf8"), but note that this will have no effect unless the external encoding is also set to something other than the default of UTF‑8.
A few EXIF tags (UserComment, GPSProcessingMethod and GPSAreaInformation) support a designated internal text encoding, with values stored as ASCII, Unicode (UCS‑2) or JIS. When reading these tags, ExifTool converts Unicode and JIS to the external character set specified by the -charset or -L option, or to UTF‑8 by default. ASCII text is not converted. When writing, text is stored as ASCII unless the string contains special characters, in which case it is converted from the external character set (UTF‑8 by default), and stored as Unicode. ExifTool writes Unicode in native EXIF byte ordering by default, but the byte order may be specified by setting the ExifUnicodeByteOrder tag (see the Extra Tags documentation).
The EXIF "XP" tags (XPTitle, XPComment, etc) are always stored internally as little-endian Unicode (UCS‑2), and are read and written using the specified external character set.
IPTC†: The value of the IPTC:CodedCharacterSet tag determines how the internal IPTC string values are interpreted. If CodedCharacterSet exists and has a value of "UTF8" (or "ESC % G") then string values are assumed to be stored as UTF‑8. Otherwise the internal IPTC encoding is assumed to be Windows Latin1 (cp1252), but this can be changed with "-charset iptc=CHARSET". When reading, these strings are converted to UTF‑8 by default, or to the external character set specified by the -charset or -L option. When writing, the inverse conversions are performed. No conversion is done if the internal (IPTC) and external (ExifTool) character sets are the same. Note that ISO 2022 character set shifting is not supported. Instead, a warning is issued and the string is not converted if an ISO 2022 shift code is encountered. See the IPTC IIM specification for more information about IPTC character coding.
ExifTool may be used to convert IPTC values to a different internal encoding. To do this, all IPTC tags must be rewritten along with the desired value of CodedCharacterSet. For example, the following command changes the internal IPTC encoding to UTF‑8 (from Windows Latin1 unless CodedCharacterSet was already "UTF8"):
exiftool -tagsfromfile @ -iptc:all -codedcharacterset=utf8 a.jpg
or from Windows Latin2 (cp1250) to UTF‑8:
exiftool -tagsfromfile @ -iptc:all -codedcharacterset=utf8 -charset iptc=latin2 a.jpg
and this command changes it back from UTF‑8 to Windows Latin1 (cp1252):
exiftool -tagsfromfile @ -iptc:all -codedcharacterset= a.jpg
or to Windows Latin2:
exiftool -tagsfromfile @ -iptc:all -codedcharacterset= -charset iptc=latin2 a.jpg
Note that unless CodedCharacterSet is UTF‑8, applications have no reliable way to determine the IPTC character encoding. For this reason, it is recommended that CodedCharacterSet be set to "UTF8" when creating new IPTC.
† Refers to the older IPTC IIM format. The more recent IPTC Photo Metadata Standard actually uses the XMP format (see below).
XMP: Exiftool reads XMP encoded as UTF‑8, UTF‑16 or UTF‑32, and converts them all to UTF‑8 internally. Also, all XML character entity references and numeric character references are converted. When writing, ExifTool always encodes XMP as UTF‑8, converting the following 5 characters to XML character references: & < > ' ". By default no further conversion is performed, however the -charset or -L option may be used to convert text to/from a specified external character set when reading/writing.
PNG: PNG TextualData tags are stored as tEXt, zTXt and iTXt chunks in PNG images. The tEXt and zTXt chunks use ISO 8859-1 encoding, while iTXt uses UTF‑8. When reading, ExifTool converts all PNG textual data to the external character set specified by the -charset or -L option, or to UTF‑8 by default. When writing, ExifTool generates a tEXt chunk (or zTXt with the -z option) if the text doesn't contain special characters or if Latin encoding is specified (-L or -charset latin); otherwise an iTXt chunk is used and the text is converted from the specified external character set and stored as UTF‑8.
JPEG Comment: The encoding for the JPEG Comment (COM segment) is not specified, so ExifTool reads/writes this text without conversion.
ID3: The ID3v1 specification officially supports only ISO 8859‑1 encoding (a subset of Windows Latin1), although some applications may incorrectly use other character sets. By default ExifTool converts ID3v1 text from Latin to the external character set specified by the -charset or -L option, or to UTF‑8 by default. However, the internal ID3v1 charset may be specified with "-charset id3=CHARSET". The encoding for ID3v2 information is stored in the file, so ExifTool converts ID3v2 text from this encoding to the external character set specified by -charset or -L, or to UTF‑8 by default. ExifTool does not currently write ID3 information.
PDF: PDF text strings are stored in either PDFDocEncoding (similar to Windows Latin1) or Unicode (UCS‑2). When reading, ExifTool converts to the external character set specified by the -charset or -L option, or to UTF‑8 by default. When writing, ExifTool encodes input text from the specified character set as Unicode only if the string contains special characters, otherwise PDFDocEncoding is used.
Photoshop: Some Photoshop resource names are stored as Pascal strings with unknown encoding. By default, ExifTool assumes MacRoman encoding and converts this to UTF‑8, but the internal and external character sets may be specified with "-charset Photoshop=CHARSET" and "-charset CHARSET" respectively.
QuickTime: QuickTime text strings may be stored in a variety of poorly documented formats, and ExifTool does its best to decode these according to the -charset option setting. For some QuickTime strings where the internal encoding is not known, ExifTool assumes a default encoding of MacRoman, but this may be changed with "-charset QuickTime=CHARSET". When writing, ExifTool prefers to store as UTF‑8 if possible, and converts to this from the character set specified by the -charset option (UTF‑8 by default).
AIFF: AIFF strings are assumed to be stored in MacRoman, and are converted according to the -charset option when reading.
RIFF: The internal encoding of RIFF strings (eg. in AVI and WAV files) is assumed to be Latin unless otherwise specified by the RIFF CSET chunk or the "-charset RIFF=CHARSET" option.
MIE: MIE strings are stored as either UTF‑8 or ISO 8859‑1. When reading, UTF‑8 strings are converted according to the -charset or -L option, and ISO 8859‑1 strings are never converted. When writing, input strings are converted from the specified character set to UTF‑8. The resulting strings are stored as UTF‑8 if they contain multi-byte UTF‑8 character sequences, otherwise they are stored as ISO 8859‑1.
Vorbis: Vorbis comments are stored as UTF‑8, and are converted to the character set specified by -charset or -L when reading.
Programmers: ExifTool returns all values as byte strings of encoded characters. Perl wide characters are not used. The encoding is UTF‑8 by default, but valid UTF‑8 can not be guaranteed for all values, so the caller must validate the encoding if necessary. The encodings described above are set by the various Charset options of the API.

Note: Some settings of the system PERL_UNICODE environment variable m


