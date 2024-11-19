from util.getVideo import*
from util.makeVideo import*
from util.plotGraph_hisum import*
from util.YTdownload import*
from extractHighlight import*
import time
import traceback
import sys
import pdb
from googleapiclient.discovery import build
from scipy.signal import medfilt


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    source_path = f"{ROOT}/highlight/source/all"
    OUTPUT = "./hisum/output/1115_sports"
    hisum_json_path = "./hisum/json_sports"
    json_root = f"{ROOT}/highlight/json"
    pkl_path = "./data.txt"
    api_key = 'AIzaSyB6RFVgm-O4VQzMms8ZteXsIRVFsj3hnMg'
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = [file.split(".")[0] for file in os.listdir(source_path) if file.lower().endswith(".mp4")]
    # print(video_ids)
    # video_ids = [
    #     "cKKjZHb80ak"
    # ]
    # TOTAL_LENTHS = [60]
    knapsack_length = 1

    ### parameters ###
    T_MIN = 1
    total_time = 30
    T_MAX = 30
    PEAK_WEIGHT = 1
    DURATION_WEIGHT = 0.2
    dp_prefer_duration = (8, 2)     # 영역
    # user_params = file_user_params(video_ids, T_MIN, TOTAL_LENTH)


    user_params = [
        # ("tB6M6wmMcuI",60, T_MIN, ),
        ("tB6M6wmMcuI",90, T_MIN, ),
        # ("tB6M6wmMcuI", 120, T_MIN, ),
]
    
    top_files = get_top_100_json_files_by_key(hisum_json_path, key="aP15")
    # max_t = 
    # minimum_length = max(1, min(10, log(total_length / summary_length) * (summary_length / 60)))
    # lst = [2, 3, 4, 5]
    with open(log_file, "a") as log:
        print(f"TOTAL: {len(top_files)}")
        for i, json_elem in enumerate(top_files):
            try:
                # print(user_params)
                print(f"==={i+1}/{len(top_files)}===")
                video_id = json_elem.split(".")[0]
                json_path = f'{json_root}/{video_id}.json'
                # data = fetch_video_data(video_id, json_path, save = False)
                download_youtube_video(video_id, source_path)
                with open(f'{hisum_json_path}/{video_id}.json', 'r') as f:
                    data = json.load(f)


                total_length = data['duration']
                intensity_scores = normalize_to_0_1(medfilt(data['predict'], kernel_size=9))
                MRD_GT = data['gt']
                start_seconds = list(range(total_length + 1))
                smoothed_scores_general = intensity_scores
                smoothed_scores_DP = smoothed_scores_general
                video_path = os.path.join(source_path, f'{video_id}.mp4')
                # plot_basic_mrd(start_seconds, smoothed_scores_general, f"{OUTPUT}/{video_id}.png")
                # pdb.set_trace()

                # if total_length > 1000:
                #     print(f"PASS {video_id} due to length {total_length}")
                #     continue
        
                output_dir = f'./{OUTPUT}/{video_id}_total_time_{total_time}'
                os.makedirs(output_dir, exist_ok=True)

                lst_name = output_dir+"/interval.pkl"
                
                # if os.path.exists(output_dir):
                #     print(f"{output_dir} already exists!!!")
                #     continue
                # knapsack_length = t_min
                # smoothed_scores_DP[:10] = 0

                message = f"==== id {video_id} original time {total_length} total time: {total_time}, min time: {T_MIN} start!!! ===="
                print(message)
                log.write(message + "\n")
                # if not os.path.exists(lst_name):
                run_higlight_methods = Run(
                    smoothed_scores_DP=smoothed_scores_DP,
                    smoothed_scores_general=smoothed_scores_general,
                    total_time=total_time,
                    t_min=T_MIN,
                    t_max=T_MAX,
                    dp_prefer_duration = dp_prefer_duration, 
                    duration_weight = DURATION_WEIGHT

                )
                dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)
                    # pdb.set_trace()
                    # with open(lst_name, 'wb') as f:
                    #     pickle.dump([dp_intervals, threshold_c, threshold_intervals, knapsack_intervals], f)
                    #     print("save pickle!!!")

                # else:
                #     with open(lst_name, 'rb') as f:
                #         print("import pickle!!!")
                #         dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = pickle.load(f)


                plot_summaries(output_dir, start_seconds, smoothed_scores_general, dp_intervals, threshold_intervals, knapsack_intervals, T_MIN, T_MAX, threshold_c, dp_prefer_duration, DURATION_WEIGHT, PEAK_WEIGHT, MRD_GT)
                
                make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals, T_MIN, dp_prefer_duration, DURATION_WEIGHT, total_time, total_length)
            except Exception as e:
                error_message = f"Error processing video_id {video_id}: {str(e)}"
                print(error_message)
                log.write(error_message + "\n")
                continue


