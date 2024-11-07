import requests
import json
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
from scipy.signal import find_peaks

class State:
    def __init__(self, time, count, score):
        self.time = time
        self.count = count
        self.score = score
        self.frame = 0
        self.next_states = [] # 접근할 수 있는 인덱스 저장

    def get_info(self):
        info = f'time: {self.time}, Count: {self.count},  Next State {self.next_states}'
        print(info)

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

def plot_intensity_graph(start_seconds, intensity_scores, video_id, total_time, min_time):
    interpolation_function = interp1d(start_seconds, intensity_scores, kind='linear', fill_value="extrapolate")
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    smoothed_intensity_scores = interpolation_function(new_time)
    peaks, _ = find_peaks(smoothed_intensity_scores, prominence = 0.1)
    
    scores = smoothed_intensity_scores
    max_t = total_time
    states = [[State(time=i, count=j, score=scores[i]) for j in range(max_t + 1)] for i in range(len(scores))]
    
    set_next_states(states, min_time, max_t)
    dp, trace = DP(states, num_points=total_time) 
    selected_points, max_score = find_path(states, dp, trace, num_points=total_time)
    selected_smoothed_scores = [smoothed_intensity_scores[i] for i in selected_points]
    grouped_points = group_consecutive_points(selected_points)
    group_sizes = [len(group) for group in grouped_points]
    
    for group in grouped_points:
        group.append(group[-1]+1)
    
    plt.figure(figsize=(25, 6))
    plt.plot(start_seconds, intensity_scores, label='Intensity Scores')
    plt.scatter(selected_points, selected_smoothed_scores, color='r', label='Selected Points', s=25, zorder=5)
    
    for group, size in zip(grouped_points, group_sizes):
        mid_point = group[len(group) // 2]
        plt.text(mid_point, smoothed_intensity_scores[mid_point], str(size), color='black', fontsize=25, ha='center')
    
    for group in grouped_points:
        for i in range(len(group) -1 ):
            plt.plot([group[i], group[i + 1]], [smoothed_intensity_scores[group[i]], smoothed_intensity_scores[group[i + 1]]], color='r', linewidth=3)
    
    title = f'Most Replayed Graph - Video ID: {video_id}, Total Time: {total_time}, Min Time: {min_time}'
    plt.title(title)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Intensity Score')
    plt.grid(True)
    plt.legend()
    
    filename = f'video_{video_id}_total_time_{total_time}_min_time_{min_time}.png'
    plt.savefig(filename)
    plt.close()

def set_next_states(states, min_time, max_t):
    n = len(states)
    for i in range(n):
        for t in range(max_t + 1):
            if i + 1 < n and t + 1 <= max_t :
                states[i][t].next_states.append((i + 1, t + 1))
            if t >= min_time:
                for j in range(i + 2, n):
                    states[i][t].next_states.append((j, 0))

def DP(states, num_points=30):
    n = len(states)
    max_t = num_points
    
    dp = np.full((n, max_t + 1, num_points + 1), -np.inf)
    dp[:, 0, 0] = 0
    trace = np.full((n, max_t + 1, num_points + 1, 4), -1, dtype=int)

    for i in range(n):
        for t in range(max_t + 1):
            for k in range(1, num_points + 1):
                if dp[i, t, k - 1] != -np.inf:
                    for next_i, next_t in states[i][t].next_states:
                        if next_i < n and next_t <= max_t:
                            new_score = dp[i, t, k - 1] + states[next_i][next_t].score
                            if new_score > dp[next_i, next_t, k]:
                                dp[next_i, next_t, k] = new_score
                                trace[next_i, next_t, k] = (i, t, next_i, next_t)

    return dp, trace

def find_path(states, dp, trace, num_points=30):
    n = len(states)
    max_score = -np.inf
    max_index = (-1, -1, -1)
    max_t = num_points
    for i in range(n):
        for t in range(max_t + 1):
            if dp[i, t, num_points] > max_score:
                max_score = dp[i, t, num_points]
                max_index = (i, t, num_points)

    selected_points = []
    k = num_points
    while max_index != (-1, -1, -1) and k > 0:
        selected_points.append(max_index[0])
        max_index = tuple(trace[max_index[0], max_index[1], k])
        k -= 1
    
    selected_points.reverse()
    return selected_points, max_score

def group_consecutive_points(points):
    grouped_points = []
    group = [points[0]]
    for i in range(1, len(points)):
        if points[i] == points[i-1] + 1:
            group.append(points[i])
        else:
            grouped_points.append(group)
            group = [points[i]]
    grouped_points.append(group)

    return grouped_points

video_ids = ["RvSg6kOPKKU", "RwWx5pKS3eA", "EOCZYxmi7ho", "OO2GKqyWi-M"]
total_times = [30, 60, 90, 120]
min_times = [2, 5, 7, 9]

for video_id in video_ids:
    data = fetch_video_data(video_id)
    start_seconds, intensity_scores = process_video_data(data)
    for total_time in total_times:
        for min_time in min_times:
            print(f"====total time:{total_time}, min time:{min_time} start!!! ====")
            plot_intensity_graph(start_seconds, intensity_scores, video_id, total_time, min_time)
            print(f"====total time:{total_time}, min time:{min_time} end!!! ====")
