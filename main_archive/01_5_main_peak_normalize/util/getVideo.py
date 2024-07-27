import requests
from scipy.interpolate import interp1d
import numpy as np
import json
from scipy.signal import find_peaks




def fetch_video_data(video_id, json_path, save = False):
    # json_path = f'C:/Users/vml_sub/Documents/Minsun2024/highlight/json/{video_id}.json'
    if save == False:
        url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={video_id}"
        response = requests.get(url)
        data = response.json()
        with open(json_path,'w') as json_file:
            json.dump(data, json_file)
    else:
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
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

    # half_cut = int(len(smoothed_intensity_scores)/2)
    # smoothed_intensity_scores = smoothed_intensity_scores[:half_cut]
    smoothed_intensity_scores = interpolation_function(new_time)
    return smoothed_intensity_scores


def apply_ransform(scores, weight):
    peaks, _ = find_peaks(scores, prominence = 0.2)
    # weight = 2
    # weight = np.sum(scores[peaks])
    scores_copy = scores.copy()
    scores_copy[peaks] += weight

    return scores_copy


# def apply_ransform(scores):
#     scores_copy = scores
#     root_func = lambda x: np.power(x, 1/20)
#     return np.where(scores >= 0.7, root_func(scores_copy), scores_copy)