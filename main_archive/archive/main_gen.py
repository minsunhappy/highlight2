import requests
import json
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
from scipy.signal import find_peaks
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import concatenate_videoclips, VideoFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip
import os
import time
import pdb

class State:
    def __init__(self, time, count, score):
        self.time = time #frame, f
        self.count = count # 𝑡 is the number of frames played after the last transition
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






def plot_intensity_graph(smoothed_intensity_scores,intensity_scores, video_id, total_time, min_time):
    # peaks, _ = find_peaks(smoothed_intensity_scores, prominence = 0.1)
    max_t = total_time
    scores = smoothed_intensity_scores
    states = [[State(time=i, count=j, score=scores[i]) for j in range(max_t + 1)] for i in range(len(scores))]
    
    print("Setting next states")
    set_next_states(states, min_time, max_t)

    print("Start calculating DP")
    dp, trace = DP(states, num_points=total_time, max_t = max_t) 
    print("End calculating DP")
    
    print("Start findinig path")
    selected_points, max_score = find_path(states, dp, trace, num_points=total_time, max_t = max_t)
    print("End findinig path")
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
    
    output_dir = f'./output/{video_id}_total_time_{total_time}_min_time_{min_time}'
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f'video_{video_id}_total_time_{total_time}_min_time_{min_time}.png')
    plt.savefig(filename)
    plt.close()
    
    return grouped_points, output_dir

def set_next_states(states, min_time, max_t):
    n = len(states)
    for i in range(n):
        for t in range(max_t + 1):
            if i + 1 < n and t + 1 <= max_t :
                states[i][t].next_states.append((i + 1, t + 1))
            if t >= min_time:
                for j in range(i + 2, n):
                    states[i][t].next_states.append((j, 0))

def DP(states, num_points, max_t):
    n = len(states)
    
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

def find_path(states, dp, trace, num_points, max_t):
    n = len(states)
    max_score = -np.inf
    max_index = (-1, -1, -1)
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
    # print(points)
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

def cut_and_concatenate_clips(video_id, grouped_points, output_dir, total_time, min_time):
    video_path = f"./source/{video_id}.mp4"
    clips = []
    colors = [(255, 0, 0), (0, 0, 255)]  # Red and Blue colors in RGB
    for i, group in enumerate(grouped_points):
        start_time = group[0]
        end_time = group[-1]
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        
        bg_clip = ColorClip(size=(clip.w + 20, clip.h + 20), color=colors[i % len(colors)], duration=clip.duration)
        
        bordered_clip = CompositeVideoClip([bg_clip, clip.set_position(('center', 'center'))])
        clips.append(bordered_clip)

    final_clip = concatenate_videoclips(clips)
    output_filename = os.path.join(output_dir, f'output_{video_id}_total_time_{total_time}_min_time_{min_time}.mp4')
    final_clip.write_videofile(output_filename, codec='libx264')

def interpolate(start_seconds, intensity_scores):
    interpolation_function = interp1d(start_seconds, intensity_scores, kind='linear', fill_value="extrapolate")
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    smoothed_intensity_scores = interpolation_function(new_time)
    return smoothed_intensity_scores



########### Threshold ########
def find_intervals(smoothed_intensity_scores, a):
    time = np.arange(len(smoothed_intensity_scores))
    crossings = np.where(np.diff(np.sign(smoothed_intensity_scores - a)))[0]
    
    intervals = []
    total_time = 0
    for i in range(0, len(crossings), 2):
        if i + 1 < len(crossings):
            start = time[crossings[i]]
            end = time[crossings[i+1]]
            intervals.append((start, end))
            time_interval = end - start 
            total_time += time_interval
    
    return total_time, intervals

def find_closest_intervals(smoothed_intensity_scores, t):
    lst = np.arange(0, 1, 0.01)
    closest_diff = float('inf')
    best_a = None
    best_total_time = None
    best_intervals = None
    
    for a in lst:
        total_time, intervals = find_intervals(smoothed_intensity_scores, a)
        diff = abs(total_time - t)
        if diff < closest_diff:
            closest_diff = diff
            best_a = a
            best_total_time = total_time
            best_intervals = intervals
    
    return best_a, best_total_time, best_intervals


#####################################


log_file = "process_log.txt"


if __name__ == "__main__":
    # video_ids = [file.split(".")[0] for file in os.listdir("./source/")]
    video_ids = ["OO2GKqyWi-M"]
    total_times = [40]
    min_times = [2]
    # max_t = 

    with open(log_file, "a") as log:
        for video_id in video_ids:
            data = fetch_video_data(video_id)
            start_seconds, intensity_scores = process_video_data(data)
            smoothed_intensity_scores = interpolate(start_seconds, intensity_scores)
            print(f"Total lengths:{len(smoothed_intensity_scores)}")
            for total_time in total_times:
                for min_time in min_times:
                    start_time = time.time()
                    message = f"==== total time: {total_time}, min time: {min_time} start!!! ===="
                    print(message)
                    log.write(message + "\n")
                    grouped_points, output_dir = plot_intensity_graph(smoothed_intensity_scores, intensity_scores, video_id, total_time, min_time)
                    # grouped_points, output_dir = plot_intensity_graph(smoothed_intensity_scores, intensity_scores, video_id, total_time, min_time, max_t = max_t)
                    cut_and_concatenate_clips(video_id, grouped_points, output_dir, total_time, min_time)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    message = f"==== total time: {total_time}, min time: {min_time} finished in {elapsed_time:.2f} seconds ===="
                    print(message)
                    log.write(message + "\n")