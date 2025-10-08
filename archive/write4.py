from pydub import AudioSegment
from pydub.utils import mediainfo

# Load the WAV audio file
audio = AudioSegment.from_file("SR87-1-2.wav", format="wav")

# Get the existing metadata
metadata = mediainfo("your_audio.wav")

# Update or add new metadata tags
metadata['title'] = "Your Title"
metadata['artist'] = "Your Artist"
metadata['album'] = "Your Album"
# Add more tags as needed

# Export the audio with the updated metadata
audio.export("output_audio.wav", format="wav", tags=metadata)

