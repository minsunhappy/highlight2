from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import time


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    OUTPUT = "output_0715_1"
    source_path = f"{ROOT}/highlight/source/0715_1"
    json_root = f"{ROOT}/highlight/json"
    video_ids = ["92GOCxay1tA"]
    # video_ids = [file.split(".")[0] for file in os.listdir(source_path)]
    user_params = [
        (60,5),
    ]
    # min_times = [6]
    # knapsack_length = 5
    # max_t = 
    # minimum_length = max(1, min(10, log(total_length / summary_length) * (summary_length / 60)))

    with open(log_file, "a") as log:
        for video_id in video_ids:
            json_path = f'{json_root}/{video_id}.json'
            print( f" ==================== id {video_id} ====================")
            print("fetch data!!!")
            data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
            print("fetch data finsihed!!!")
            start_seconds, intensity_scores = process_video_data(data)
            smoothed_intensity_scores, new_time = interpolate(start_seconds, intensity_scores)

            print(f"Total lengths:{len(smoothed_intensity_scores)}")
            video_path = os.path.join(source_path, f'{video_id}.mp4')

            for user_param in user_params:
                total_time, min_time = user_param
                # knapsack_length = min_time
                message = f"id {video_id} original time {len(smoothed_intensity_scores)} total time: {total_time}, min time: {min_time} start!!!"
                print(message)
                log.write(message + "\n")
                original = Run(
                    smoothed_intensity_scores=smoothed_intensity_scores,
                    total_time=total_time,
                    min_time=min_time, new_time = new_time
                )

                include_points = [104, 162]
                custom1 = Run(
                    smoothed_intensity_scores=smoothed_intensity_scores,
                    total_time=total_time,
                    min_time=min_time,
                    custom = [include_points, None, None, None],
                    new_time = new_time# 점 포함, 구간 포함, 점 제외, 구간 제외 => 점, (구간1, 구간2)
                )

                exclude_interval = [200, 400]
                include_points2 = [617]
                custom2 = Run(
                    smoothed_intensity_scores=smoothed_intensity_scores,
                    total_time=total_time,
                    min_time=min_time,
                    custom = [include_points2, None, None, exclude_interval],
                    new_time = new_time
                )

                include_interval3 = [104, 162]
                exclude_point3 = [32]
                custom3 = Run(
                    smoothed_intensity_scores=smoothed_intensity_scores,
                    total_time=total_time,
                    min_time=min_time,
                    custom = [None, include_interval3, exclude_point3, None], 
                    new_time = new_time
                )

                
                original_intervals = original.run_DP()
                custom1_intervals = custom1.run_DP()
                custom2_intervals = custom2.run_DP()
                custom3_intervals = custom3.run_DP()
                # grouped_points, output_dir = plot_intensity_graph(smoothed_intensity_scores, intensity_scores, video_id, total_time, min_time, max_t = max_t)

                interval_lst = [original_intervals, custom1_intervals, custom2_intervals, custom3_intervals]
                plot_customs(start_seconds, interval_lst, smoothed_intensity_scores)

                # output_dir = f'./{OUTPUT}/{video_id}_total_time_{total_time}_min_time_{min_time}'
                # os.makedirs(output_dir, exist_ok=True)

                # plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_time, threshold_c)
                
                # make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals)