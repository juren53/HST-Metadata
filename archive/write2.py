import wave
from pydub.utils import mediainfo

def write_metadata(file_path, metadata_dict):
    try:
        # Read existing metadata using pydub
        existing_metadata = mediainfo(file_path)

        # Update metadata with new values
        existing_metadata.update(metadata_dict)

        # Open the WAV file for reading and writing
        with wave.open(file_path, 'rb') as wav_file:
            # Retrieve existing metadata
            params = wav_file.getparams()

            # Create a new wave file for writing with the updated metadata
            with wave.open(file_path, 'wb') as new_wav_file:
                new_wav_file.setparams(params)

                # Write the updated metadata to the new wave file
                for key, value in existing_metadata.items():
                    setattr(new_wav_file, key, value)

                # Copy the audio content from the original wave file to the new one
                new_wav_file.writeframes(wav_file.readframes(params.nframes))

    except Exception as e:
        print(f"Error: {e}")

# Example usage
file_path = "SR87-1-2.wav"
metadata_dict = {
    "title": "Your Title",
    "comment": "this is where the comments are printed =====================",
    "album": "Your Album",
    # Add more metadata fields as needed
}

write_metadata(file_path, metadata_dict)

