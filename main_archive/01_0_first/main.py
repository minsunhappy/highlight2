from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from extractHighlight import*
import time


log_file = "process_log.txt"
if __name__ == "__main__":
    source_path = "C:/Users/vml_sub/Documents/Minsun2024/highlight/source"
    video_ids = [file.split(".")[0] for file in os.listdir(source_path)]
    
    # video_ids = ["OO2GKqyWi-M"]
    total_times = [60]
    min_times = [4]
    knapsack_length = 5
    # max_t = 

    with open(log_file, "a") as log:
        for video_id in video_ids:
            print("fetch data!!!")
            data = fetch_video_data(video_id)
            print("fetch data finsihed!!!")
            start_seconds, intensity_scores = process_video_data(data)
            smoothed_intensity_scores = interpolate(start_seconds, intensity_scores)

            print(f"Total lengths:{len(smoothed_intensity_scores)}")
            video_path = os.path.join(source_path, f'{video_id}.mp4')

            for total_time in total_times:
                for min_time in min_times:
                    message = f"==== id {video_id} original time {len(smoothed_intensity_scores)} total time: {total_time}, min time: {min_time} start!!! ===="
                    print(message)
                    log.write(message + "\n")
                    run_higlight_methods = Run(
                        smoothed_intensity_scores=smoothed_intensity_scores,
                        total_time=total_time,
                        min_time=min_time,
                    )
                    dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)
                    # grouped_points, output_dir = plot_intensity_graph(smoothed_intensity_scores, intensity_scores, video_id, total_time, min_time, max_t = max_t)


                    output_dir = f'./output/{video_id}_total_time_{total_time}_min_time_{min_time}'
                    os.makedirs(output_dir, exist_ok=True)

                    plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_time, threshold_c)
                    
                    make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals)