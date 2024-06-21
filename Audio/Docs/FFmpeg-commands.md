## FFmpeg Commands for Audio Files


### Metadata tags with FFmpeg

```
ffmpeg -i \
"SR65-33-3.wav" \
-metadata ICOP="Unrestricted" \
-metadata ISRC="Harry S. Truman Library" \
-metadata ICRD="October 8, 1948" \
-metadata ISBJ=" " \
-metadata ICMT="Rear platform remarks, President Truman, Albany, NY" \
-metadata INAM="INAM SR59-12" \
-metadata IPRD="IPRD SR59-12" \
"SR65-33-3.wav_tagged.wav"
```
```
ICOP="Copyright [Public Domain or Restricted?]"
ISRC="Source [credit - Truman Library?]"
ICRD="Date [ date strings accepted ]"
ISBJ="Subject"
ICMT="Comment"
INAM="Title"
IPRD="Name [could be used for an Accession Number?]"
```


```
ffmpeg -i \
"SR59-12 BlackHawkWaltz.mp3" \
-metadata ICOP="Copyright" \
-metadata ISRC="Source" \
-metadata ICRD="Date" \
-metadata ISBJ="Subject" \
-metadata ICMT="Comment" \
output.mp3
```

```
ffmpeg -i \
"SR65-33-3.wav" \
-metadata ICOP="Unrestricted" \
-metadata ISRC="Harry S. Truman Library" \
-metadata ICRD="October 8, 1948" \
-metadata ISBJ=" " \
-metadata ICMT="Rear platform remarks, President Truman, Albany, NY" \
-metadata INAM="INAM SR59-12" \
-metadata IPRD="IPRD SR59-12" \
"SR65-33-3.wav_tagged.wav"
```

ICOP="Copyright [Public Domain or Restricted?]"
ISRC="Source [credit - Truman Library?]"
ICRD="Date [ date strings accepted ]"
ISBJ="Subject"
ICMT="Comment"
INAM="Title"
IPRD="Name [could be used for an Accession Number?]"




ffmpeg -i \
"SR59-12 BlackHawkWaltz.mp3" \
-metadata ICOP="Copyright" \
-metadata ISRC="Source" \
-metadata ICRD="Date" \
-metadata ISBJ="Subject" \
-metadata ICMT="Comment" \
output.mp3





####  FFmpeg commands listing metadata

To list metadata tags for an MP3 file using ffmpeg, you can use the following command:
```
bash
ffmpeg -i output.mp3 -f ffmetadata
```
Replace input.mp3 with the name of your MP3 file.

When you run this command, ffmpeg will output metadata information for the specified MP3 file in the ffmetadata format, including tags like artist, title, album, duration, etc.

You can also use the following command to display metadata in a more human-readable format:
```
bash
ffprobe -i input.mp3 -show_format -show_streams
```

#### ID3V2 tags

A crucial ffmpeg switch for mp3 tags

```
-id3v2_version 3
```
### Embedding Album Art in MP3 files

To embed album art in an MP3 file using FFmpeg in a way that is compatible with Windows Media Player, you can follow these steps:

    Ensure you have the album art image file (e.g., album_art.jpg) ready.

    - Use FFmpeg to embed the album art into the MP3 file. 
    - You can do this with the -i option to specify the input MP3 file, 
    - and the -i option again to specify the album art image file. 
    - Then, use the -map option to map the album art image to the APIC (Attached Picture) tag in the MP3 file. 
    - Finally, specify the output MP3 file.

Here's the command:

bash
```
ffmpeg -i input.mp3 -i album_art.jpg -map 0 -map 1 -c copy -id3v2_version 3 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (Front)" output.mp3
```
Replace input.mp3 with the name of your input MP3 file, and album_art.jpg with the name of your album art image file. Ensure that output.mp3 is the desired name for your output MP3 file.

This command will copy both the audio and the album art into the output file without re-encoding (-c copy). It also sets the ID3v2 version to 3 (-id3v2_version 3), which is widely supported by media players including Windows Media Player.

Once you run this command, the album art should be embedded in the output MP3 file and should display correctly when played in Windows Media Player, VidoLan VLC, Apple iTunes, and WinAmp.


Here is the same command parsed into descrete commands to make it readable and still executable from a command line:

```
ffmpeg -i "SR59-12 BlackHawkWaltz_tagged.mp3"
-i output.jpg -map 0 -map 1 -c copy 
-id3v2_version 3 
-metadata title="Album cover" -metadata comment="Cover (Front)" 
output.mp3
```

#### Adding Accession Numbers to thumbnails

To make each thumbnail unique before embedding in an mp3 file, the Accession Number can be embedded in a copy of the 'standard thumbnail' so that users/researchers 
who may have a collection of Truman Library audio files can differentiate the files by the thumbnail.
```
ffmpeg -i HST-thumbnail.jpg 
-vf "drawtext=text='SR59-12':x=10:y=10:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5" 
output.jpg
```
Then the 'temporary' output.jpg thumbnail can be used to embed in the mp3 file.
