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



def plot_intensity_graph(smoothed_intensity_scores,intensity_scores, video_id, total_time, min_time, max_t):
    # peaks, _ = find_peaks(smoothed_intensity_scores, prominence = 0.1)
    
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




log_file = "process_log.txt"


if __name__ == "__main__":
    video_ids = [file.split(".")[0] for file in os.listdir("./source/")]
    # video_ids = ["OO2GKqyWi-M"]
    total_times = [180]
    min_times = [5]
    max_t = 20

    with open(log_file, "a") as log:
        for video_id in video_ids:
            data = fetch_video_data(video_id)
            start_seconds, intensity_scores = process_video_data(data)
            smoothed_intensity_scores = interpolate(start_seconds, intensity_scores)
            print(f"Total lengths:{len(smoothed_intensity_scores)}")
            for total_time in total_times:
                for min_time in min_times:
                    start_time = time.time()
                    message = f"==== total time: {total_time}, min time: {min_time}, max time: {max_t} start!!! ===="
                    print(message)
                    log.write(message + "\n")
                    grouped_points, output_dir = plot_intensity_graph(smoothed_intensity_scores, intensity_scores, video_id, total_time, min_time, max_t = max_t)
                    cut_and_concatenate_clips(video_id, grouped_points, output_dir, total_time, min_time)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    message = f"==== total time: {total_time}, min time: {min_time}, max time: {max_t} finished in {elapsed_time:.2f} seconds ===="
                    print(message)
                    log.write(message + "\n")