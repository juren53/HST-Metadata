import subprocess

def add_metadata(input_file, output_file, metadata_tags):
    # Build the ffmpeg command
    command = [
        'ffmpeg',
        '-i', input_file,  # Use the provided input_file parameter here
        '-metadata', f'{metadata_tags[0]}={metadata_tags[1]}',
        # Add more metadata tags if needed
        output_file
    ]

    # Run the ffmpeg command
    subprocess.run(command)

# Example usage
input_wav = 'SR87-1-2.wav'  # Remove unnecessary quotes and file extension
output_wav = 'output_audio.wav'
metadata = [('title', 'HST campaigns'), ('copyright', 'Public Domain'), ('description', 'Harry Truman on a Whistle Stop in Des Moines, Iowa')]

add_metadata(input_wav, output_wav, metadata)

