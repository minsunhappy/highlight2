from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import time


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    OUTPUT = "output"
    source_path = f"{ROOT}/highlight/source/"
    json_root = f"{ROOT}/highlight/json"
    # video_ids = ["ImntsoxN9_4"]
    video_ids = [file.split(".")[0] for file in os.listdir(source_path)]
    # defined length, min , max
    user_params = [
        (60, 2, 20),
    ]
    knapsack_length = 5

    for video_id in video_ids:
        json_path = f'{json_root}/{video_id}.json'
        print( f" ==================== id {video_id} ====================")
        # print("fetch data!!!")
        data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
        # print("fetch data finsihed!!!")
        start_seconds, intensity_scores = process_video_data(data)
        smoothed_intensity_scores = interpolate(start_seconds, intensity_scores)
        total_length = len(smoothed_intensity_scores)
        print(f"Total lengths:{total_length}")
        video_path = os.path.join(source_path, f'{video_id}.mp4')
        if total_length > 1200:
            print(f"PASS {video_id} due to length {total_length}")
            continue
        for user_param in user_params:
            total_time, min_time, max_time = user_param
            # knapsack_length = min_time
            message = f"id {video_id} original time {total_length} total time: {total_time}, min time: {min_time}, max: {max_time} start!!!"
            print(message)
            with open(log_file, "a") as log:
                log.write(message + "\n")
            run_higlight_methods = Run(
                smoothed_intensity_scores=smoothed_intensity_scores,
                total_time=total_time,
                min_time=min_time,
                max_time=max_time,
                # max_time=total_length
            )
            dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)
            # grouped_points, output_dir = plot_intensity_graph(smoothed_intensity_scores, intensity_scores, video_id, total_time, min_time, max_t = max_t)


            output_dir = f'./{OUTPUT}/{video_id}_total_time_{total_time}_min_time_{min_time}'
            os.makedirs(output_dir, exist_ok=True)

            plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_time, threshold_c)
            
            # make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals)