import os
import json
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip
import librosa
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.zeros_like(arr)
    normalized_arr = (arr - min_val) / (max_val - min_val)
    return normalized_arr

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

def process_video(video_id, json_dir, video_dir, output_dir):
    # Load MRD data
    json_path = os.path.join(json_dir, f"{video_id}.json")
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    markers = data['items'][0]['mostReplayed']['markers']
    start_millis = [marker['startMillis'] for marker in markers]
    intensity_scores = [marker['intensityScoreNormalized'] for marker in markers]
    start_seconds = [millis / 1000 for millis in start_millis]

    # Interpolate MRD data
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    interpolation_function = interp1d(start_seconds, intensity_scores, kind='linear', fill_value="extrapolate")
    smoothed_intensity_scores = interpolation_function(new_time)
    normalized_scores = normalize_array(smoothed_intensity_scores)

    # Process audio
    video_path = os.path.join(video_dir, f"{video_id}.mp4")
    video = VideoFileClip(video_path)
    audio = video.audio
    temp_audio_path = os.path.join(output_dir, "temp_audio.wav")
    audio.write_audiofile(temp_audio_path)

    y, sr = librosa.load(temp_audio_path)
    os.remove(temp_audio_path)

    frame_length = int(sr * 0.05)
    hop_length = int(sr * 0.025)
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length).squeeze()
    times = librosa.times_like(rms, sr=sr, hop_length=hop_length)

    # Smooth and normalize audio data
    window_size = 201
    smoothed_rms = savgol_filter(rms, window_size, 3)
    normalized_rms = normalize_array(smoothed_rms)

    # Moving average of audio data
    ma_window_size = 600
    ma_rms = moving_average(rms, ma_window_size)
    normalized_ma_rms = normalize_array(ma_rms)
    ma_times = times[:len(normalized_ma_rms)]

    # Plot the combined graph
    plt.figure(figsize=(20, 6))
    plt.plot(new_time / 60, normalized_scores, color='red', linewidth=2, label='Most Replayed')
    plt.plot(ma_times / 60, normalized_ma_rms, color='green', linewidth=2, label='Audio Volume (MA)')
    plt.plot(times / 60, normalized_rms, color='blue', alpha=0.7, linewidth=2, label='Audio Volume (Raw)')

    plt.title(f'Audio Volume and Most Replayed Graph - Video ID: {video_id}', fontsize=16)
    plt.xlabel('Time (minutes)', fontsize=12)
    plt.ylabel('Normalized Score', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(np.arange(0, total_duration_seconds / 60 + 1, 5))
    plt.legend()
    plt.tight_layout()

    # Save the plot
    output_path = os.path.join(output_dir, f"{video_id}_combined_graph.png")
    plt.savefig(output_path)
    plt.close()

    print(f"Processed and saved graph for video ID: {video_id}")

def main():
    json_dir = "/source/ms/highlight/json"
    video_dir = "./source"
    output_dir = "./output"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process all JSON files in the directory
    for filename in os.listdir(video_dir):
        if filename.endswith(".mp4"):
            video_id = filename.split(".")[0]  # Remove .json extension
            if os.path.exists(os.path.join(json_dir, f"{video_id}.json")):
                process_video(video_id, json_dir, video_dir, output_dir)
            else:
                print(f"Video file not found for ID: {video_id}")

if __name__ == "__main__":
    main()