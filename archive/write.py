from pydub import AudioSegment
from pydub.utils import mediainfo

def write_metadata(file_path, metadata_dict):
    audio = AudioSegment.from_file(file_path, format="wav")

    # Extract existing metadata
    existing_metadata = mediainfo(file_path)

    # Update metadata with new values
    existing_metadata.update(metadata_dict)

    # Convert metadata dictionary to string format
    metadata_string = "\n".join([f"{key}={value}" for key, value in existing_metadata.items()])

    # Write metadata to the file
    audio.export(file_path, format="wav", tags={"metadata": metadata_string})

# Example usage
file_path = "SR87-1-2.wav"
metadata_dict = {
    "title": "Your Title",
    "artist": "Your Artist",
    "album": "Your Album",
    "Description": "Description of Harry Truman event",
    # Add more metadata fields as needed
}

write_metadata(file_path, metadata_dict)

