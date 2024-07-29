from moviepy.editor import concatenate_videoclips, VideoFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip
import os

def make_video(video_path, output_dir, name, intervals):
    # video_path = f"./source/{video_id}.mp4"
    # video_outout_dir = os.path.join(output_dir, f"{name}.mp4")
    clips = []
    colors = [(255, 0, 0), (0, 0, 255)]  # Red and Blue colors in RGB
    for i, interval in enumerate(intervals):
        start_time, end_time = interval
        end_time += 1
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        
        bg_clip = ColorClip(size=(clip.w + 20, clip.h + 20), color=colors[i % len(colors)], duration=clip.duration)
        
        bordered_clip = CompositeVideoClip([bg_clip, clip.set_position(('center', 'center'))])
        clips.append(bordered_clip)

    final_clip = concatenate_videoclips(clips)
    output_filename = os.path.join(output_dir, f'{name}.mp4')
    print(f"Video FPS: {final_clip.fps}")
    final_clip.write_videofile(output_filename, codec='libx264')



def make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals, min_time, dp_prefer_duration):

    a, b = dp_prefer_duration
    make_video(video_path, output_dir, 'threshold', threshold_intervals)
    make_video(video_path, output_dir, f'dp_min_{min_time}_dur_{a}_{b}', dp_intervals)
    # make_video(video_path, output_dir, 'knapsack', knapsack_intervals)
