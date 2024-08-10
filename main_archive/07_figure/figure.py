from util.getVideo import*
from util.makeVideo import*
from util.plotGraph import*
from util.YTdownload import download_videos
from extractHighlight import*
import librosa
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy import interpolate
from scipy import stats
import json
from collections import defaultdict

def draw_event_cnt(DRAW_EVENT_CNT, cnt_length, target_lst, smoothed_scores_general, T_MIN, T_MAX, dp_prefer_duration, DURATION_WEIGHT,knapsack_length):
    if DRAW_EVENT_CNT:
        cnt_dic = {"DP":[], "Threshold":[]}
        total_times = np.arange(1, cnt_length, 1)

        for total_time in total_times:
            run_higlight_methods = Run(
                smoothed_scores_general, smoothed_scores_general, total_time, T_MIN, T_MAX, dp_prefer_duration, DURATION_WEIGHT
            )
            dp_intervals, threshold_c, threshold_intervals, knapsack_intervals = run_higlight_methods.run_all(knapsack_length)

            # plot_summaries("./", start_minute, smoothed_scores_general, dp_intervals, threshold_intervals, knapsack_intervals, T_MIN, threshold_c)
            
            cnt_dic["DP"].append((interval_time(dp_intervals), event_cnt(dp_intervals, target_lst)))
            cnt_dic["Threshold"].append((interval_time(threshold_intervals), event_cnt(threshold_intervals, target_lst)))
        plot_all(cnt_dic)


def draw_sound_chat_graph(DRAW_SOUND_CHAT_GRAPH, scores, scores_times, sound_path, chat_path, goal, yellow_card):
    if DRAW_SOUND_CHAT_GRAPH:
        x_chat, y_chat, chat_similarity = chat_graph(chat_path, scores)
        best_window_size, sound_similarity, x_sound, y_sound  = sound_graph(sound_path, scores, scores_times)
        pdb.set_trace()
        plt.figure(figsize=(14, 3))
        plt.plot(scores_times, normalize(scores), label='MRD', color='black', linewidth = 2, alpha=0.5)
        plt.plot(x_sound, y_sound, label='Sound', color='blue', linewidth = 2, alpha=0.5)
        plt.plot(x_chat, normalize(y_chat), label='Chat', color='green', linewidth = 2, alpha=0.5)
        for g in goal:
            plt.axvline(x=g, color='black', linestyle='--', linewidth = 2,  alpha=0.5,)
        # for yc in yellow_card:
        #     plt.axvline(x=yc, color='gray', linestyle='-.', alpha=0.7,  label='Yellow Card' if yc == yellow_card[0] else "")
            
        plt.title(f"Sound: 0.79, Chat: {chat_similarity:.2f}", fontsize=16)
        # plt.title(f"Sound: {sound_similarity:.2f}, Chat: {chat_similarity:.2f}", fontsize=16)
        plt.xlabel("Time (minutes)", fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig("./output/sound_chat_graph.png", format='png')


        # print(best_window_size, best_similarity)
        # chat_scores = chat_graph(chat_path)




###### chat ############################################################################
def chat_graph(chat_path, scores):
    chat_data = read_json_file(chat_path)
    message_counts = count_messages_per_minute(chat_data)
    minutes = sorted(message_counts.keys())
    time = np.array(list(message_counts.keys()))
    chat_counts = np.array(list(message_counts.values()))

    # 채팅 갯수의 변화(속도) 계산
    chat_speed = [abs(chat_counts[i] - chat_counts[i - 1]) for i in range(1, len(chat_counts))]
    chat_speed.insert(0, chat_speed[0])  # 첫 번째 값은 0으로
    normalize_data = normalize(chat_speed)
    # x_chat_speed = np.linspace(0, 1, len(minutes))
    # x_scores = np.linspace(0, 1, len(scores))

    # normalize_ma_rms_cropped를 normalize_scores_cropped의 길이에 맞춰 리샘플링
    x_resampled, y_resampled = resample(time, normalize_data, len(scores))
    cos_sim = cosine_similarity(y_resampled.reshape(1, -1), np.array(scores).reshape(1, -1))[0][0]




    return x_resampled, y_resampled, cos_sim


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    return data

def time_to_minutes(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:  # 형식이 "1:11:03"와 같은 경우
        hours, minutes, _ = map(int, parts)
        return hours * 60 + minutes
    elif len(parts) == 2:  # 형식이 "11:03"와 같은 경우
        minutes, _ = map(int, parts)
        return minutes
    else:
        return None  # 알 수 없는 형식

def count_messages_per_minute(messages):
    message_counts = defaultdict(int)
    for message in messages:
        time = message['time']
        minutes = time_to_minutes(time)
        if minutes is not None and minutes >= 0:  # 0초 이상인 경우만 처리
            message_counts[minutes] += 1
    return message_counts

##########################################################################



##### sound ###############################################################

def sound_graph(sound_path, scores, scores_times):
    rms_path = './input/rms.npy'
    sr = 22050  # 기본 샘플링 레이트
    frame_length = int(sr * 0.05)  
    hop_length = int(sr * 0.025)  
    if os.path.exists(rms_path):
        print("load data")
        # rms.npy 파일이 존재하면 로딩
        rms = np.load(rms_path)
    else:
        print("new data")
        # rms.npy 파일이 존재하지 않으면 WAV 파일 로딩
        y, sr = librosa.load(sound_path)
        
        # 소리 크기(RMS) 계산
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)
        rms = rms.squeeze()  

        # RMS 값 저장
        np.save(rms_path, rms)
    # 소리 크기(RMS) 계산
 
    times = librosa.times_like(rms, sr=sr, hop_length=hop_length) / 60
    # best_window_size, best_similarity = find_optimal_window_size(times, rms, scores)
    best_window_size = 4600
    best_similarity = 0.79
    sound_ma = np.convolve(rms, np.ones(best_window_size), 'valid') / best_window_size
    sound_ma_times = times[:len(sound_ma)]
    norm_sound = normalize(sound_ma)
    x_resampled, y_resampled = resample(sound_ma_times, norm_sound, len(scores))

    # print(ma_times, best_window_size, best_similarity)
    return best_window_size, best_similarity, x_resampled, y_resampled

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

def normalize(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def resample(x, y, num_points):
    f = interpolate.interp1d(x, y, kind='linear', fill_value='extrapolate')
    x_new = np.linspace(x.min(), x.max(), num_points)
    y_new = f(x_new)
    return x_new, y_new

def find_optimal_window_size(times, rms, intensity_scores, min_window=100, max_window=10000, step=100):
    best_window_size = min_window
    best_similarity = -1

    for window_size in range(min_window, max_window + 1, step):
        # Calculate moving average
        ma_rms = moving_average(rms, window_size)
        ma_times = times[:len(ma_rms)]

        # Normalize data
        normalize_ma_rms = normalize(ma_rms)
        normalize_scores = normalize(intensity_scores)

        # Resample ma_rms to match the time points of intensity_scores
        x_resampled, y_resampled = resample(ma_times, normalize_ma_rms, len(intensity_scores))

        # Calculate cosine similarity
        cos_sim = cosine_similarity(y_resampled.reshape(1, -1), normalize_scores.reshape(1, -1))[0][0]

        if cos_sim > best_similarity:
            best_similarity = cos_sim
            best_window_size = window_size

    return best_window_size, best_similarity



##### sound ###############################################################