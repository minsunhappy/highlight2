import requests
import json
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
from scipy.signal import find_peaks
import pdb

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

def plot_intensity_graph(start_seconds, intensity_scores, video_id, total_time, min_time,event_lst ):
    interpolation_function = interp1d(start_seconds, intensity_scores, kind='linear', fill_value="extrapolate")
    total_duration_seconds = start_seconds[-1]
    total_duration_minutes = total_duration_seconds / 60
    new_time = np.arange(0, total_duration_minutes, 1) * 60 
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
    
    
    for group, size in zip(grouped_points, group_sizes):
        mid_point = group[len(group) // 2]
        plt.text(mid_point, smoothed_intensity_scores[mid_point], str(size), color='black', fontsize=25, ha='center')
    
    # print( selected_points)
    event_cnt = 0
    for group in grouped_points:
        for i in range(len(group) -1 ):
            # plt.plot([group[i], group[i + 1]], [smoothed_intensity_scores[group[i]], smoothed_intensity_scores[group[i + 1]]], color='r', linewidth=3)

            if group[i] in event_lst:
                event_cnt += 1

    

    return event_cnt

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
        max_index = tuple(trace[max_index[0], max_index[1], k])
        selected_points.append(max_index[0])
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

def save_event_time_graph(video_id, event_cnt_lst):
    plt.figure(figsize=(10, 3))
    plt.step(range(len(event_cnt_lst)), event_cnt_lst, where='post',linewidth= 2)

    # plt.plot(event_cnt_lst, label='Event Count')

    plt.title(f'Event Count Graph - Video ID: {video_id}')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Event Count')
    plt.grid(True)
    plt.legend()

    # 그래프를 파일로 저장
    plt.savefig('./event_count_graph.png')
    # plt.show()
    plt.close()


if __name__ == "__main__":
    video_ids = ["Cbij3MKhdOY"]
    # total_times =  np.arange(5, 105, 5)
    min_times = [4]
    root = "/source/ms"
    event_lst = [13, 15, 21, 43, 45, 52, 62, 68, 73, 97]

    evnet_cnt_lst = []
    
    for video_id in video_ids:
        json_path = f'{root}/highlight/json/{video_id}.json'
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
        start_seconds, intensity_scores = process_video_data(data)
        # total_times = np.arange(5, len(intensity_scores)+5, 5)
        total_times = np.arange(1, len(intensity_scores), 1)
        for total_time in total_times:
            for min_time in min_times:
                # print(f"====total time:{total_time}, min time:{min_time} start!!! ====")
                evnet_cnt = plot_intensity_graph(start_seconds, intensity_scores, video_id, total_time, min_time, event_lst)
                evnet_cnt_lst.append(evnet_cnt)
                print(f"====total time:{total_time}, min time:{min_time} end!!! ====")
        
        print(evnet_cnt_lst)
        save_event_time_graph(video_id, evnet_cnt_lst)
