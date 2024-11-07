from moviepy.editor import concatenate_videoclips, VideoFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip
import os
import random

# def make_video(video_path, output_dir, name, intervals):
#     # video_path = f"./source/{video_id}.mp4"
#     # video_outout_dir = os.path.join(output_dir, f"{name}.mp4")
#     clips = []
#     colors = [(255, 0, 0), (0, 0, 255)]  # Red and Blue colors in RGB
#     for i, interval in enumerate(intervals):
#         start_time, end_time = interval
#         end_time += 1
#         clip = VideoFileClip(video_path).subclip(start_time, end_time)
        
#         bg_clip = ColorClip(size=(clip.w + 20, clip.h + 20), color=colors[i % len(colors)], duration=clip.duration)
        
#         bordered_clip = CompositeVideoClip([bg_clip, clip.set_position(('center', 'center'))])
#         clips.append(bordered_clip)

#     final_clip = concatenate_videoclips(clips)
#     output_filename = os.path.join(output_dir, f'{name}.mp4')
#     print(f"Video FPS: {final_clip.fps}")
#     final_clip.write_videofile(output_filename, codec='libx264')

def make_video(video_path, output_dir, name, intervals):
    clips = []
    for interval in intervals:
        start_time = interval[0] 
        end_time = interval[-1]
        end_time += 1
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    output_filename = os.path.join(output_dir, f'{name}.mp4')
    print(f"Video FPS: {final_clip.fps}")
    final_clip.write_videofile(output_filename, codec='libx264')

def make_random_lst(dp_intervals, total_time, total_length):
    chunk_num = len(dp_intervals)
    count_num = total_time / chunk_num
    count_num_int = int(total_time / chunk_num)
    available_starts = list(range(1, total_length - count_num_int + 2))
    result = []
    
    for _ in range(chunk_num):
        if not available_starts:
            break
        
        start = random.choice(available_starts)
        group = (start, start + count_num - 1)
        result.append(group)
        
        # 선택된 그룹과 겹치는 시작점들을 제거
        available_starts = [x for x in available_starts if x > start + count_num - 1 or x + count_num - 1 < start]
    
    # 결과를 시작 숫자를 기준으로 정렬
    result.sort(key=lambda x: x[0])
    
    return result



def make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals, min_time, dp_prefer_duration, weight, total_time, total_length):

    random_interval = make_random_lst(dp_intervals, total_time, total_length)
    print(random_interval)
    make_video(video_path, output_dir, 'random', random_interval)
    a, b = dp_prefer_duration
    # make_video(video_path, output_dir, 'threshold', threshold_intervals)
    # make_video(video_path, output_dir, f'dp_min_{min_time}_dur_{a}_{b}_weight_{weight}', dp_intervals)
    # make_video(video_path, output_dir, 'knapsack', knapsack_intervals)

    #random video
