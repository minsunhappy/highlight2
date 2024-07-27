from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import time


def event_cnt(interval, event_lst):
    cnt = 0

    for elem in interval:
        start, end = elem
        end += 1
        for i in event_lst:
            if start <= i <= end:
                cnt +=1
    return cnt

def interval_time(interval):
    total_duration = 0
    for start, end in interval:
        total_duration += end - start + 1
    return total_duration


def plot_all(dic, min_time):
    plt.figure(figsize=(5, 3))

    for key, value in dic.items():
        times, counts = zip(*value)
        plt.plot(times, counts, label=key, marker='o', linestyle='-', linewidth=1, markersize=3)

    plt.xlabel('Time(minutes)')
    plt.ylabel('Count')
    plt.title(f'DP, Threshold, Knapsack - min time {min_time}')
    plt.legend()
    plt.grid(True)

    plt.savefig('comparison_graph_step.png')


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    source_path = f"{ROOT}/highlight/source/pre_usertest"
    json_root = f"{ROOT}/highlight/json"
    video_ids = video_ids = ["Cbij3MKhdOY"]
    event_lst = [13, 15, 21, 43, 45, 52, 62, 68, 73, 97]

    min_time = 3
    knapsack_length = 3
    cnt_dic = {"DP":[], "Threshold":[], "Knapsack":[]} #시간,  cnt 형태로 담겨 있음
    with open(log_file, "a") as log:
        for video_id in video_ids:
            json_path = f'{json_root}/{video_id}.json'
            print("fetch data!!!")
            data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
            print("fetch data finsihed!!!")
            start_seconds, intensity_scores = process_video_data(data)
            start_minute = 101
            # start_minute = start_seconds/60
            smoothed_intensity_scores = interpolate(start_seconds, intensity_scores)

            print(f"Total lengths:{len(smoothed_intensity_scores)}")
            video_path = os.path.join(source_path, f'{video_id}.mp4')

            total_times = [15]
            # total_times = np.arange(3, 40, 1)
            # total_times = np.arange(1, len(intensity_scores), 1)

            for total_time in total_times:
                message = f"==== id {video_id} original time {len(smoothed_intensity_scores)} total time: {total_time}, min time: {min_time} start!!! ===="
                print(message)
                log.write(message + "\n")
                run_higlight_methods = Run(
                    smoothed_intensity_scores=smoothed_intensity_scores,
                    total_time=total_time,
                    min_time=min_time,
                )
                dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)

                plot_summaries("./", start_minute, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_time, threshold_c)
                
                cnt_dic["DP"].append((interval_time(dp_intervals), event_cnt(dp_intervals, event_lst)))
                cnt_dic["Threshold"].append((interval_time(threshold_intervals), event_cnt(threshold_intervals, event_lst)))
                cnt_dic["Knapsack"].append((interval_time(knapsack_intervals), event_cnt(knapsack_intervals, event_lst)))
            
            # print(cnt_dic)
            plot_all(cnt_dic, min_time)
