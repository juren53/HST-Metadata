from pydub.utils import mediainfo

def get_wav_metadata(file_path):
    try:
        # Get metadata information using pydub
        metadata = mediainfo(file_path)

        # Print metadata information
        print("Metadata for WAV file:", file_path)
        for key, value in metadata.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
file_path = "SR87-1-2.wav"
get_wav_metadata(file_path)

