import subprocess

def add_metadata(input_file, output_file, metadata_tags):
    # Build the ffmpeg command
    command = [
        'ffmpeg',
        '-i', input_file,
        '-metadata', f'{metadata_tags[0]}={metadata_tags[1]}',
        # Add more metadata tags if needed
        output_file
    ]

    # Print the constructed command for debugging
    print(' '.join(command))

    # Run the ffmpeg command
    result = subprocess.run(command, capture_output=True)

    # Print the result for debugging
    print(result.stdout.decode())
    print(result.stderr.decode())

# Example usage
input_wav = 'SR87-1-2.wav'
output_wav = 'output_audio.wav'
metadata = [('title', 'HST on the stump'), ('copyright', 'Public Domain'), ('description', 'Harry Truman on a Whistle Stop in Des Moines, Iowa')]

add_metadata(input_wav, output_wav, metadata)

