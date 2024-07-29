from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import time
import traceback
import sys


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    # source_path = f"{ROOT}/highlight/source/general_sports"
    source_path = f"{ROOT}/highlight/source/general_video"
    OUTPUT = "./output_0729/"
    json_root = f"{ROOT}/highlight/json"
    # video_ids = [file.split(".")[0] for file in os.listdir(source_path) if file.lower().endswith(".mp4")]
    # video_ids = ["92GOCxay1tA"]
    # download_videos(url_lst)
    # video_ids = ["L5x9oyZHKUM"]
    # video_ids = ["3GgxdPhm5cM", "6y_g7UQd2sY","cY04XjQEJyE", "qglffq44cbc", "zoHrtAXPzAk"]
    video_ids = ["2FiouEjnspc", "ksOQZ0z_PSQ","lNpN_FH8_Ac", "VGyhYYzMKdw"]
    TOTAL_LENTHS = [60]
    knapsack_length = 5

    ### parameters ###
    T_MIN = 2
    TOTAL_LENTH = 60
    T_MAX = 20
    PEAK_WEIGHT = 1
    DURATION_WEIGHT = 5
    dp_prefer_duration = (8, 2)     # 영역
    user_params = file_user_params(video_ids, T_MIN, TOTAL_LENTHS)
    ### parameters ###


#     user_params = [
#         ("5mLnuCORMrU",TOTAL_LENTH, T_MIN),
#         ("2FiouEjnspc",TOTAL_LENTH, T_MIN),
#         ("ImntsoxN9_4",TOTAL_LENTH, T_MIN),
#         ("iYZMOa5WAds",TOTAL_LENTH, T_MIN),
#         ("jjgLH_470B4",TOTAL_LENTH, T_MIN),
#         ("ksOQZ0z_PSQ",TOTAL_LENTH, T_MIN),
#         ("lNpN_FH8_Ac",TOTAL_LENTH, T_MIN),
#         ("pfqvBSMxacE",TOTAL_LENTH, T_MIN),
#         ("VGyhYYzMKdw",TOTAL_LENTH, T_MIN),
#         ("Vu4UaoJxK6U",TOTAL_LENTH, T_MIN),      
#     ]

    # max_t = 
    # minimum_length = max(1, min(10, log(total_length / summary_length) * (summary_length / 60)))
    with open(log_file, "a") as log:
        print(f"TOTAL: {len(user_params)}")
        for i, user_param in enumerate(user_params):
            try:
                for j in np.arange(0.1, 1.1, 0.1):
                    DURATION_WEIGHT = j
                    print(f"==={i+1}/{len(user_params)}===")
                    video_id, total_time, t_min = user_param
                    json_path = f'{json_root}/{video_id}.json'
                    data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
                    start_seconds, intensity_scores = process_video_data(data)
                    smoothed_scores_general = interpolate(start_seconds, intensity_scores)
                    smoothed_scores_DP = apply_transform(smoothed_scores_general, PEAK_WEIGHT)
                    total_length = len(smoothed_scores_general)
                    video_path = os.path.join(source_path, f'{video_id}.mp4')

                    # if total_length > 1000:
                    #     print(f"PASS {video_id} due to length {total_length}")
                    #     continue
            
                    output_dir = f'./{OUTPUT}/{video_id}_total_time_{total_time}'
                    
                    # if os.path.exists(output_dir):
                    #     print(f"{output_dir} already exists!!!")
                    #     continue
                    # knapsack_length = t_min
                    message = f"==== id {video_id} original time {total_length} total time: {total_time}, min time: {t_min} start!!! ===="
                    print(message)
                    log.write(message + "\n")
                    run_higlight_methods = Run(
                        smoothed_scores_DP=smoothed_scores_DP,
                        smoothed_scores_general=smoothed_scores_general,
                        total_time=total_time,
                        t_min=t_min,
                        t_max=T_MAX,
                        dp_prefer_duration = dp_prefer_duration, 
                        duration_weight = DURATION_WEIGHT

                    )
                    dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)


                    os.makedirs(output_dir, exist_ok=True)

                    plot_summaries(output_dir, start_seconds, smoothed_scores_general, dp_intervals, threshold_intervals, knapsack_intervals, t_min, T_MAX, threshold_c, dp_prefer_duration, DURATION_WEIGHT, PEAK_WEIGHT)
                    
                    # make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals, t_min, dp_prefer_duration)

            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb = traceback.extract_tb(exc_tb)
                filename, line_number, func_name, text = tb[-1]
                
                error_message = f"Error processing video {video_id} in file {filename}, line {line_number}: {str(e)}\n"
                print(error_message)
                log.write(error_message)
                log.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)) + "\n")  # 상세한 에러 정보를 로그에 기록
                continue

