from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import time
import traceback
import sys
import pdb

log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    # source_path = f"{ROOT}/highlight/source/general_sports"
    source_path = f"{ROOT}/highlight/source/all"
    # source_path = f"{ROOT}/highlight/source/0812_entertainment"
    OUTPUT = "output/custom_change_0905"
    json_root = f"{ROOT}/highlight/json"
    pkl_path = "./data.txt"
    video_ids = [file.split(".")[0] for file in os.listdir(source_path) if file.lower().endswith(".mp4")]
    # print(video_ids)
    # video_ids = [
    #     "cKKjZHb80ak"
    # ]
    # TOTAL_LENTHS = [60]
    knapsack_length = 1

    ### parameters ###
    T_MIN = 1
    TOTAL_LENTH = 30
    T_MAX = 30
    CUSTOM_WEIGHT = 10
    DURATION_WEIGHT = 0.2
    dp_prefer_duration = (8, 2)     # 영역



    user_params = [

        # ("LrsH9vWq0Xg",60, T_MIN),
        ("ZD1QrIe--_Y",90, T_MIN),
    ]

    # 변주1. 구본찬이 10점 쏜것만
    # a_custom = [ 5, 180]
    # a_include= [162, 186, 344, 458, 601, 754]
    a_include= [264, 431, 559, 642, 717]
#     a_include= [138, 162, 186, 344, 458, 489, 601, 755]
    a_exclude = []

    b_include = [172, 443, 565, 589, 717]
    b_exclude = []
    include = a_include
    exclude = a_exclude


    with open(log_file, "a") as log:
        print(f"TOTAL: {len(user_params)}")
        for i, user_param in enumerate(user_params):
            try:
                # print(user_params)
                print(f"==={i+1}/{len(user_params)}===")
                video_id, total_time, t_min = user_param
                json_path = f'{json_root}/{video_id}.json'
                # data = fetch_video_data(video_id, json_path, save = False)
                data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
                
                start_seconds, intensity_scores = process_video_data(data)
                smoothed_scores_general = interpolate(start_seconds, intensity_scores)
                smoothed_scores_DP = apply_transform(smoothed_scores_general, CUSTOM_WEIGHT, include = include, exclude= exclude)
                total_length = len(smoothed_scores_general)
                smoothed_scores_DP[:10] = 0
                video_path = os.path.join(source_path, f'{video_id}.mp4')

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
                # smoothed_scores_DP[:100] = 0

                message = f"==== id {video_id} original time {total_length} total time: {total_time}, min time: {t_min} start!!! ===="
                print(message)
                log.write(message + "\n")
                if not os.path.exists(lst_name):
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
                    # pdb.set_trace()
                    with open(lst_name, 'wb') as f:
                        pickle.dump([dp_intervals, threshold_c, threshold_intervals, knapsack_intervals], f)
                        print("save pickle!!!")

                else:
                    with open(lst_name, 'rb') as f:
                        print("import pickle!!!")
                        dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = pickle.load(f)


                plot_summaries(output_dir, start_seconds, smoothed_scores_general, dp_intervals, threshold_intervals, knapsack_intervals, t_min, T_MAX, threshold_c, dp_prefer_duration, DURATION_WEIGHT, CUSTOM_WEIGHT, a_include, b_include)
                
                make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals, t_min, dp_prefer_duration, DURATION_WEIGHT, total_time, total_length)

            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb = traceback.extract_tb(exc_tb)
                filename, line_number, func_name, text = tb[-1]
                
                error_message = f"Error processing video {video_id} in file {filename}, line {line_number}: {str(e)}\n"
                print(error_message)
                log.write(error_message)
                log.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)) + "\n")  # 상세한 에러 정보를 로그에 기록
                continue

