from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import time
import traceback


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    OUTPUT = "./output/ks_time_2"
    source_path = f"{ROOT}/highlight/source/all"
    json_root = f"{ROOT}/highlight/json"
    # video_ids = [file.split(".")[0] for file in os.listdir(source_path) if file.lower().endswith(".mp4")]
    # print(f"ALL VIDEOS {len(video_ids)}")
    # video_ids = ["lNpN_FH8_Ac"]
    # download_videos(url_lst)
    # video_ids = ["cY04XjQEJyE"]
    # video_ids = ["1zJ5tMF4YkI", "3GgxdPhm5cM","6y_g7UQd2sY","cY04XjQEJyE", "DN-kU28UYN4", "DzcH9eNFVto", "qglffq44cbc", "zoHrtAXPzAk"]

    video_ids = [
        # "5mLnuCORMrU",
        # "2FiouEjnspc",
        # "ImntsoxN9_4",
        # "iYZMOa5WAds",
        # "jjgLH_470B4",
        # "ksOQZ0z_PSQ",
        # "lNpN_FH8_Ac",
        # "pfqvBSMxacE",
        # "VGyhYYzMKdw",
        # "Vu4UaoJxK6U"
    ]


    # user_params = [
    #     ("5mLnuCORMrU",TOTAL_LENTH, T_MIN),
    #     ("2FiouEjnspc",TOTAL_LENTH, T_MIN),
    #     ("ImntsoxN9_4",TOTAL_LENTH, T_MIN),
    #     ("iYZMOa5WAds",TOTAL_LENTH, T_MIN),
    #     ("jjgLH_470B4",TOTAL_LENTH, T_MIN),
    #     ("ksOQZ0z_PSQ",TOTAL_LENTH, T_MIN),
    #     ("lNpN_FH8_Ac",TOTAL_LENTH, T_MIN),
    #     ("pfqvBSMxacE",TOTAL_LENTH, T_MIN),
    #     ("VGyhYYzMKdw",TOTAL_LENTH, T_MIN),
    #     ("Vu4UaoJxK6U",TOTAL_LENTH, T_MIN),      
    # ]
    user_params = [
        # (60,8),
        # (30,10),
        # (45,5),
        # (30,5),
        (60,4),
        # (60,4),
        # (90,5),
        # (120,10),
        # (120,5),
        # (180,12),
        # (180,5)
    ]
    knapsack_length = 1
    weight = 2
    # max_t = 
    # minimum_length = max(1, min(10, log(total_length / summary_length) * (summary_length / 60)))

    with open(log_file, "a") as log:
        for video_id in video_ids:
            try:
                json_path = f'{json_root}/{video_id}.json'
                data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
                start_seconds, intensity_scores = process_video_data(data)
                smoothed_scores_general = interpolate(start_seconds, intensity_scores)
                smoothed_scores_DP = apply_ransform(smoothed_scores_general, weight)
                total_length = len(smoothed_scores_general)
                # print(f"Total lengths:{total_length}")
                video_path = os.path.join(source_path, f'{video_id}.mp4')
                # if total_length > 1200:
                #     print(f"PASS {video_id} due to length {total_length}")
                #     continue
                
                for user_param in user_params:
                    total_time, min_time = user_param
                    # knapsack_length = min_time
                    message = f"==== id {video_id} original time {total_length} total time: {total_time}, min time: {min_time} start!!! ===="
                    print(message)
                    output_dir = f'{OUTPUT}/{video_id}_total_time_{total_time}'
                    
                    # if os.path.exists(output_dir):
                    #     print(f"{output_dir} already exists!!!")
                    #     continue
                    log.write(message + "\n")
                    run_higlight_methods = Run(
                        smoothed_scores_DP=smoothed_scores_DP,
                        smoothed_scores_general=smoothed_scores_general,
                        total_time=total_time,
                        min_time=min_time,
                    )
                    dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)
                    # grouped_points, output_dir = plot_intensity_graph(smoothed_scores, intensity_scores, video_id, total_time, min_time, max_t = max_t)


                    # output_dir = f'/source/ms/highlight/main_archive/01_2_method_comparision_gen_lastpoint/output_tests/{video_id}_total_time_{total_time}_min_time_{min_time}'
                    os.makedirs(output_dir, exist_ok=True)

                    plot_summaries(output_dir, start_seconds, smoothed_scores_general, dp_intervals, threshold_intervals, knapsack_intervals, min_time, threshold_c)
                    
                    make_each_videos(video_path, output_dir, dp_intervals, threshold_intervals, knapsack_intervals, min_time)
            except Exception as e:
                error_message = f"Error processing video {video_id}: {str(e)}\n"
                print(error_message)
                log.write(error_message)
                log.write(traceback.format_exc() + "\n")  # 상세한 에러 정보를 로그에 기록
                continue
            


