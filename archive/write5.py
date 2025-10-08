import subprocess

def add_metadata(input_file, output_file, metadata_tags):
    # Build the ffmpeg command
    command = [
        'ffmpeg',
        '-i', "SR87-1-2.wav",
        '-metadata', f'{metadata_tags[0]}={metadata_tags[1]}',
        # Add more metadata tags if needed
        output_file
    ]

    # Run the ffmpeg command
    subprocess.run(command)

# Example usage
input_wav = '"SR87-1-2.wav".wav'
output_wav = 'output_audio.wav'
metadata = [('title', 'HST campaings'), ('copyright', 'Public Domain'), ('description', 'Harry Truman on a Whistle Stop in Des Moines, Iowa')]

add_metadata(input_wav, output_wav, metadata)

