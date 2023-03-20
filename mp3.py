# importing packages
from pytube import YouTube
import os
import subprocess
import time

# url input from user
yt = YouTube(
	str(input("Enter the URL of the video you want to download: \n>> ")))

# extract  128k audio only by the itag id of 140
audio = yt.streams.get_by_itag(140) 

# check for destination to save file
print("Enter the destination (leave blank for current directory)")
destination = str(input(">> ")) or '.'
_filename = yt.title

# download the file
out_file = audio.download(output_path=destination, filename=_filename+'.mp4')
time.sleep(1)
    

mp4 = "'%s'.mp4" % _filename
mp3 = "'%s'.mp3" % _filename
ffmpeg = ('ffmpeg -i %s ' % mp4 + mp3)
subprocess.run(ffmpeg, shell=True)

# result of success
print(yt.title + " has been successfully downloaded.")

