
import subprocess

cmd = ['ffmpeg', '-i', 'output.mp3', '-i', 'output.jpg', '-map', '0', '-map', '1', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (Front)"', 'output-2.mp3']
subprocess.run(cmd)


