import requests
from scipy.interpolate import interp1d
import numpy as np
import json
from scipy.signal import find_peaks
import pickle
import os
import ast
import isodate
import subprocess
import pdb
import re



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


def get_mrd(video_id, json_path, total_length,  save = False):
    if save == False:
        result = subprocess.run(['node', '/source/ms/highlight/main_archive/01_7_0_main_rintv_revise/util/most_replayed.js', video_id], capture_output=True, text=True)
        # JSON 형식의 데이터를 파싱하여 저장
        if result.stdout:
            data = json.loads(result.stdout)
            
            # 결과를 JSON 파일로 저장
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)
                
            print(f"Heatmap data for video ID {video_id} saved to {video_id}_heatmap_data.json")

        else:
            print(f"No data received for video ID {video_id}")
    else: 
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)

    _, y_values = convert_svg(data["heatMap"], total_length)
    # x_values, y_values = convert_svg(data["heatMap"], total_length)
    x_values = np.linspace(0, total_length, len(y_values))

    return  x_values, y_values 

    return  x_values, y_values 
def convert_svg(data, total_length):
    x_values = []
    y_values = []
    accumulated_x = 0  # 이전 챕터의 마지막 x 값을 누적

    for path in data:
        # 'C '로 구분하여 Bézier 커브 좌표 부분만 추출
        segments = path.split('C ')[1:]  # 'C '로 나눈 후 첫 번째 요소 제거
        seg_len = len(segments) - 1
        for i, segment in enumerate(segments):
            if i != seg_len: 
                # 숫자 패턴을 통해 모든 좌표 값을 찾음
                points = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", segment)))
                
                # 세 번째 x, y 좌표 추출 및 변환
                if len(points) >= 6:
                    x3 = points[4]
                    y3 = points[5]
                    # 변환된 x, y 값 추가, x는 누적된 값으로
                    x_values.append(accumulated_x + (x3 - 5) / 1000)  # 시간 스탬프 누적
                    y_values.append((100 - y3) / 100)  # heat 값 (0 to 1)
        # pdb.set_trace()
        # 마지막 x 값을 누적하여 다음 챕터 시작 위치 설정
        accumulated_x = x_values[-1]


    # x_values_scaled, y_values_scaled  = normalize_to_range_with_y(x_values, y_values, total_length)
    return x_values, y_values


def normalize_to_range_with_y(x_values, y_values, n):
    x_min = min(x_values)
    x_max = max(x_values)
    
    # x_values와 y_values를 정규화
    normalized_x = [(x - x_min) / (x_max - x_min) * n for x in x_values]
    # normalized_y = [(y - min(y_values)) / (max(y_values) - min(y_values)) * n for y in y_values]

    return normalized_x, y_values

def scale_to_n(x_values, n):
    max_x = max(x_values)
    # 모든 값에 대해 n에 맞춰 스케일링
    scaled_x_values = [(n / max_x) * x for x in x_values]
    return scaled_x_values

def process_video_data(data):
    markers = data['items'][0]['mostReplayed']['markers']
    start_millis = [marker['startMillis'] for marker in markers]
    intensity_scores = [marker['intensityScoreNormalized'] for marker in markers]
    start_seconds = [millis / 1000 for millis in start_millis]
    return start_seconds, intensity_scores

def fetch_shorts_data(video_id, json_path, save = False):
    # json_path = f'C:/Users/vml_sub/Documents/Minsun2024/highlight/json/{video_id}.json'
    api_key = "AIzaSyDhIDvZmAIzEYZl5I1C8Y0vKNSqwyTWCUY"
    url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={api_key}"
    # print(url)
    response = requests.get(url)
    data = response.json()
    with open(json_path,'w') as json_file:
        json.dump(data, json_file)

    return data


def interpolate(start_seconds, intensity_scores):
    interpolation_function = interp1d(start_seconds, intensity_scores, kind='linear', fill_value="extrapolate")
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    smoothed_intensity_scores = interpolation_function(new_time)

    # half_cut = int(len(smoothed_intensity_scores)/2)
    # smoothed_intensity_scores = smoothed_intensity_scores[:half_cut]
    smoothed_intensity_scores = interpolation_function(new_time)
    return smoothed_intensity_scores


def apply_transform(scores, weight):
    peaks, _ = find_peaks(scores)
    # weight = 2
    # weight = np.sum(scores[peaks])
    print(peaks)
    scores_copy = scores.copy()
    scores_copy[peaks] *= weight

    return scores_copy

def file_user_params(video_ids, t_min, total_lengths):
    lst = []
    for elem in video_ids:
        for total_length in total_lengths:
            lst.append((elem, total_length, t_min))
    return lst


def pair_user_params(pkl_path,json_root):
    with open(pkl_path, "r") as file:
        data = file.read()
    data = ast.literal_eval(data)

    lst = []
    for short, video in data:
        video_id = video.split("v=")[-1]
        short_id = short.split("v=")[-1]
        json_path = f'{json_root}/{video_id}.json'
        data = fetch_shorts_data(short_id, json_path, save = os.path.exists(json_path))
        duration = data['items'][0]['contentDetails']['duration']
        duration_parsed = isodate.parse_duration(duration)
        seconds = duration_parsed.total_seconds()
        lst.append((video_id, int(seconds), 1))

    return lst



# def apply_ransform(scores):
#     scores_copy = scores
#     root_func = lambda x: np.power(x, 1/20)
#     return np.where(scores >= 0.7, root_func(scores_copy), scores_copy)
def get_video_duration(youtube, video_id):
    # Call the videos().list method to get video details
    response = youtube.videos().list(
        part='contentDetails',
        id=video_id
    ).execute()
    
    # Extract the duration from the response
    duration = response['items'][0]['contentDetails']['duration']
    
    # Parse the duration (ISO 8601 format) using isodate library
    duration_in_seconds = isodate.parse_duration(duration).total_seconds()
    
    return duration_in_seconds

