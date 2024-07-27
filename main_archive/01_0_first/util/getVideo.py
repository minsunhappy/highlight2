import requests
from scipy.interpolate import interp1d
import numpy as np



def fetch_video_data(video_id):
    url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={video_id}"
    response = requests.get(url)
    data = response.json()
    return data

def process_video_data(data):
    markers = data['items'][0]['mostReplayed']['markers']
    start_millis = [marker['startMillis'] for marker in markers]
    intensity_scores = [marker['intensityScoreNormalized'] for marker in markers]
    start_seconds = [millis / 1000 for millis in start_millis]
    return start_seconds, intensity_scores


def interpolate(start_seconds, intensity_scores):
    interpolation_function = interp1d(start_seconds, intensity_scores, kind='linear', fill_value="extrapolate")
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    smoothed_intensity_scores = interpolation_function(new_time)
    return smoothed_intensity_scores
