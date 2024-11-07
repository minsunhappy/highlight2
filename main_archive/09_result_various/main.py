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
    OUTPUT = "output/comp_time"
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
    
    T_MAX = 30
    PEAK_WEIGHT = 1
    DURATION_WEIGHT = 0.2
    dp_prefer_duration = (8, 2)     # 영역
    # user_params = file_user_params(video_ids, T_MIN, TOTAL_LENTH)

    
    # user_params = pair_user_params(pkl_path, json_root)
    ### parameters ###
    # user_params = [
    #    ("xJcAcJ6BYLE", T_MIN, 50),
    #    ("phcekstnfb0", T_MIN, 57),
    #    ("nHCBZ_BZZl0", T_MIN, 58),
    #    ("GiHyN5uw4Ho", T_MIN, 45),
    #    ("", T_MIN, 50),
       
    # ]

    TOTAL_LENTHS = [30, 45, 60, 75, 90, 105, 120]
    user_params = [
        ("RwWx5pKS3eA", T_MIN),
        # ("4rp2aLQl7vg", T_MIN),
        # ("MfO1FenJbKI", T_MIN),
        # ("92GOCxay1tA", T_MIN),
        # ("guzahFU3gBU", T_MIN),
        # ("Gz5-NQROQGw", T_MIN),
        # ("NpVJidAKOqc", T_MIN),
        # ("Vw34wMAqWzc", T_MIN),
    ]

    # max_t = 
    # minimum_length = max(1, min(10, log(total_length / summary_length) * (summary_length / 60)))
    # lst = [2, 3, 4, 5]
    dic = {}
    dic_threshold = {}
    with open(log_file, "a") as log:
        print(f"TOTAL: {len(user_params)}")
        for i, user_param in enumerate(user_params):
            video_id, t_min = user_param
            dic_elem = {}
            dic_th_elem = {}
            for length in TOTAL_LENTHS:
                total_time = length

                print(f"==={i+1}/{len(user_params)}===")
                json_path = f'{json_root}/{video_id}.json'
                # data = fetch_video_data(video_id, json_path, save = False)
                data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
                
                start_seconds, intensity_scores = process_video_data(data)
                smoothed_scores_general = interpolate(start_seconds, intensity_scores)
                smoothed_scores_DP = apply_transform(smoothed_scores_general, PEAK_WEIGHT)
                total_length = len(smoothed_scores_general)
                video_path = os.path.join(source_path, f'{video_id}.mp4')


                output_dir = f'./{OUTPUT}/{video_id}_total_time_{total_time}'
                os.makedirs(output_dir, exist_ok=True)


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
                dp_intervals, dp_reward_sum, threshold_c, threshold_intervals, knapsack_intervals, threshold_reward_sum = run_higlight_methods.run_all(knapsack_length)
                dic_elem[total_time] = {"dp": dp_intervals, "reward_sum": dp_reward_sum}
                # 이름만 threshold 인거임 편의상
                dic_th_elem[total_time] = {"threshold": knapsack_intervals, "reward_sum": threshold_reward_sum}
                plot_summaries(output_dir, start_seconds, smoothed_scores_general, dp_intervals, threshold_intervals, knapsack_intervals, t_min, T_MAX, threshold_c, dp_prefer_duration, DURATION_WEIGHT, PEAK_WEIGHT)
            dic[video_id] = [dic_elem]
            dic_threshold[video_id] = [dic_elem]

        print(dic)
        with open("dp_infos4.pkl", 'wb') as f:
            pickle.dump(dic, f)


