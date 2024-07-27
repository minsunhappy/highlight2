from pytube import YouTube

def download_videos(url_lst):
    yt = YouTube(video_url)
    yt.streams.filter(adaptive=True, file_extension='mp4').first().download()