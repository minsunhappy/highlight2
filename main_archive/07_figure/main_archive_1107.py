from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
from figure_archive_1107 import*
import traceback
import sys
import numpy as np
from scipy.signal import find_peaks

log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = "/source/ms"
    source_path = f"{ROOT}/highlight/source/all"
    OUTPUT = "output/0801_real_final"
    json_root = f"{ROOT}/highlight/json"

    video_ids = [
        "s5o2H3n6B-8",
        # "LPDnemFoqVk",
        # "u9HeRxo1Y74",
        # "fh7Ro3BNSOE",
        # "SvV6aUki6LU"
    ]
    TOTAL_LENTHS = [60]
    goal = [15, 43, 52, 62, 68, 73, 97]
    yellow_card = [13]
    # all_lst = [13, 15, 21, 43, 45, 52, 54, 62, 68, 73, 76, 77, 97] #일단 골로 먼저 해보자.
    # knapsack_length = 5

    ### parameters ###
    T_MIN = 1
    T_MAX = 30
    PEAK_WEIGHT = 1
    DURATION_WEIGHT = 0.2

    ########
    DRAW_EVENT_CNT = False
    cnt_length = 30
    target_lst = goal

    DRAW_SOUND_CHAT_GRAPH = True
    # video_id
    #######
    dp_prefer_duration = (8, 2)     # 영역
    user_params = file_user_params(video_ids, T_MIN, TOTAL_LENTHS)
    knapsack_length = T_MIN

    sound_window = 4600
    with open(log_file, "a") as log:
        for i, user_param in enumerate(user_params):
            # try:
            
            video_id, _, _ = user_param
            print(f"========{video_id}========")
            sound_path = f"./input/{video_id}.wav"
            chat_path = f"./input/chatlog_replay_{video_id}.json"
                
            json_path = f'{json_root}/{video_id}.json'
            data = fetch_video_data(video_id, json_path, save = os.path.exists(json_path))
            start_seconds, intensity_scores = process_video_data(data)
            # start_minute = 101
            peaks, _ = find_peaks(intensity_scores)
            # print(peaks)
            new_time, smoothed_scores_general = interpolate2(start_seconds, intensity_scores)
            print(f"Total lengths:{len(smoothed_scores_general)}")
            # smoothed_scores_DP = apply_transform(smoothed_scores_general, PEAK_WEIGHT)
            total_length = len(smoothed_scores_general)
            video_path = os.path.join(source_path, f'{video_id}.mp4')

            
            draw_event_cnt(DRAW_EVENT_CNT, cnt_length, target_lst, smoothed_scores_general, T_MIN, T_MAX, dp_prefer_duration, DURATION_WEIGHT,knapsack_length)
            draw_sound_chat_graph(video_id, DRAW_SOUND_CHAT_GRAPH, smoothed_scores_general, new_time/60 , sound_path, chat_path, goal, yellow_card, sound_window)
            total_times = np.arange(1, total_length, 1)

            # except Exception as e:
            #     exc_type, exc_value, exc_tb = sys.exc_info()
            #     tb = traceback.extract_tb(exc_tb)
            #     filename, line_number, func_name, text = tb[-1]
                
            #     error_message = f"Error processing video {video_id} in file {filename}, line {line_number}: {str(e)}\n"
            #     print(error_message)
            #     log.write(error_message)
            #     log.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)) + "\n")  # 상세한 에러 정보를 로그에 기록
            #     continue

