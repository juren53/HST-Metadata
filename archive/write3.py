from pydub import AudioSegment

def add_metadata_to_wav(input_file, output_file, metadata_dict):
    # Load the WAV file
    audio = AudioSegment.from_wav(input_file)

    # Add metadata to the audio file
    for key, value in metadata_dict.items():
        audio = audio.set_frame_metadata(key.encode(), value.encode())

    # Export the modified audio to a new WAV file
    audio.export(output_file, format="wav")

# Example usage:
input_wav_file = "SR87-1-2.wav"
output_wav_file = "output_audio_with_metadata.wav"
metadata = {"title": "Sample Title", "artist": "Sample Artist", "year": "2022"}

add_metadata_to_wav(input_wav_file, output_wav_file, metadata)

