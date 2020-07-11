from pytube import YouTube, Playlist
from unidecode import unidecode
import os

path = ""  # Insert here the chatbot path, or get the current path with os module


def Download_video(link, only_audio=False):
    youtube = YouTube(link)
    if only_audio:
        video = youtube.streams.filter(only_audio=only_audio).first()
    else:
        video = youtube.streams.filter(only_audio=only_audio).get_highest_resolution()
    if video:
        title = video.title
        cod = video.default_filename.split(".")[-1]
        if "video" not in os.listdir(path):
            os.mkdir(f"{path}/video")
        try:
            video.download(f"{path}/video")
            return True
        except:
            try:
                video.download(f"{path}/video", filename=f"{title.unidecode}.{cod}")
                return True
            except:
                return False
    else:
        return False


def Download_playlist(link, only_audio=False):
    playlist = Playlist(link)
    results = []
    for video in playlist:
        results.append(Download_video(link, only_audio=False))
    return all(x for x in results)
