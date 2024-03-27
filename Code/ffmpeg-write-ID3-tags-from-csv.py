import subprocess

# Path to your input MP3 file
input_mp3_file = "SR59-12 BlackHawkWaltz.mp3"

# Metadata dictionary with ID3 tag keys
metadata = {
    'TIT1': 'TIT1: Title - HST playing pinano',
    'TIT2': 'TIT2: Title - HST playing the Black Hawk Watz',
    'TIT3': 'TIT3: Title - HST playing the Black Hawk Watz in the White House',
    'TPE1': 'TPEI: Artist - Harry Truman',
    'TALB': 'TALB: Album ',
    'TYER': 'TYER: Year 1948',
    'TDAT': 'TDAT: September 30, 1948',
    'TCOP': 'TCOP: Copyright - Restricted',
    'TCMT': 'TCMT: Comment - HST playing piano', 
    'TOWN': 'TOWN: Owner - Harry S. Truman Presidental Library',  
    # Add more ID3 tag fields as needed
}

# Constructing the ffmpeg command for MP3 with ID3 tags
ffmpeg_command = [
    'ffmpeg',
    '-i', input_mp3_file,
]

# Add ID3 tag fields to the ffmpeg command
for key, value in metadata.items():
    ffmpeg_command.extend(['-metadata', f'{key}={value}'])

# Specify ID3v2.3 version for MP3 files
ffmpeg_command.extend(['-id3v2_version', '3'])

# Output MP3 file path
output_mp3_file = "output.mp3"

# Add output file path to the ffmpeg command
ffmpeg_command.append(output_mp3_file)

# Execute the ffmpeg command to embed ID3 tags into the MP3 file
subprocess.run(ffmpeg_command)

