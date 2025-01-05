#!/usr/bin/python3
###################  list-dir-audio-files.py  #################

import os
import glob

print("In the current working directory")

def list_audio_files():
    # Get lists of both mp3 and wav files
    mp3_files = glob.glob('*.mp3')
    wav_files = glob.glob('*.wav')
    
    # Combine the lists
    all_audio_files = mp3_files + wav_files
    
    # Sort alphabetically
    all_audio_files.sort()
    
    # Print results
    if all_audio_files:
        print(f"Found {len(all_audio_files)} audio file(s):")
        print("\nMP3 files:")
        for file in mp3_files:
            print(f"- {file}")
            
        print("\nWAV files:")
        for file in wav_files:
            print(f"- {file}")
    else:
        print("No MP3 or WAV files found in the current directory.")

    # Return the list in case it's needed for further processing
    return all_audio_files

if __name__ == '__main__':
    list_audio_files()
