import os
from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
from figure import*
import traceback
import sys
import numpy as np
from scipy.signal import find_peaks
from googleapiclient.discovery import build


log_file = "process_log.txt"
if __name__ == "__main__":
    ROOT = f"/source/ms"
    source_path = f"{ROOT}/highlight/source/all"
    INFO = False
    OUTPUT = f"./output/1113_{INFO}"
    json_root = f"{ROOT}/highlight/json"
    api_key = os.environ["YOUTUBE_API_KEY"]
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = [
        # # "BF2TZq-ntRQ",
        ("Cbij3MKhdOY", []), 
        # ("gCr4Pg9mEA4",  []),
        # ("w2itwFJCgFQ",  []),
        # ("094y1Z2wpJg", []),
        # ("4SSVr3EKTlM", []),
        # ("VB5ZRVky0Yw", []),
        # ("OBG50aoUwlI", []),
        # ("LlY79zjud-Q", []),
        # 
        # ("kMhle4o0uk0", []),
        # ("OBG50aoUwlI", []),
        # ("2MJY_ptQW1o", []),

        ]
    TOTAL_LENTHS = [60]
    # goal = [15, 43, 52, 62, 68, 73, 97]
    # yellow_card = [13]
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
    # target_lst = goal

    DRAW_SOUND = False
    DRAW_CHAT = False
    # video_id
    #######
    dp_prefer_duration = (8, 2)     # 영역
    user_params = file_user_params(video_ids, T_MIN, TOTAL_LENTHS)
    knapsack_length = T_MIN

    sound_window = 4600
    with open(log_file, "a") as log:
        for i, user_param in enumerate(video_ids):
            # try:
            
            video_id, goal = user_param
            print(f"========{video_id}========")
            sound_path = f"./input/{video_id}.wav"
            chat_path = f"./input/chatlog_replay_{video_id}.json"
                
            # download_audio_as_wav(video_id, sound_path, DRAW_SOUND)
            json_path = f'{json_root}/{video_id}.json'
            total_length = int(get_video_duration(youtube, video_id))
            # start_seconds, intensity_scores = get_mrd(video_id, json_path, total_length, save = False)
            start_seconds, intensity_scores = get_mrd(video_id, json_path, total_length, save = os.path.exists(json_path))
            # intensity_scores와 start_seconds를 하나의 리스트로 묶음
            # intensity_scores가 0.1 이하인 항목 필터링
            filtered_data = [(start, score) for start, score in zip(start_seconds, intensity_scores) if score <= 0.1]


            ########## 랜덤
            # selected = []
            # for start, score in filtered_data:
            #     if not selected or all(abs(start - s) >= 10 for s in selected):
            #         selected.append(start)

            # if len(selected) > 5:
            #      selected = random.sample(selected, 5)
            # print(selected)
            random.shuffle(start_seconds)
            chosen = []
            for time in start_seconds:
                # 이미 선택된 모든 시점과 비교해 10초 이상 차이가 나야 함
                if all(abs(time - c) >= 10 for c in chosen):
                    chosen.append(time)
                    if len(chosen) == 5:
                        break
            
            # 선택된 시점들을 정렬해서 리턴
            chosen.sort()
            print(chosen)


            peaks, _ = find_peaks(intensity_scores)
            # print(peaks)
            smoothed_scores_general = interpolate_(start_seconds, intensity_scores)
            print(f"Total lengths:{len(smoothed_scores_general)}")
            # smoothed_scores_DP = apply_transform(smoothed_scores_general, PEAK_WEIGHT)
            total_length = len(smoothed_scores_general)
            video_path = os.path.join(source_path, f'{video_id}.mp4')

            
            # draw_event_cnt(DRAW_EVENT_CNT, cnt_length, target_lst, smoothed_scores_general, T_MIN, T_MAX, dp_prefer_duration, DURATION_WEIGHT,knapsack_length)
            draw_sound_chat_graph(video_id, DRAW_SOUND, DRAW_CHAT, intensity_scores, smoothed_scores_general, start_seconds, sound_path, chat_path, sound_window, OUTPUT, goal, INFO)
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

