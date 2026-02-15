import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
import matplotlib.ticker as ticker
from scipy.signal import find_peaks
from sklearn.metrics.pairwise import cosine_similarity



# def plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_duration, max_duration, threshold_value, dp_prefer_duration, duration_weight, peak_weight):
#     total_duration_seconds = start_seconds[-1]
#     new_time = np.arange(0, total_duration_seconds, 1)
#     fig, axs = plt.subplots(2, 1, figsize=(10, 3), sharex=True)
#     methods = [f'Threshold', 'DP']
#     intervals_list = [knapsack_intervals, dp_intervals, ]
#     peaks, _ = find_peaks(smoothed_intensity_scores)
#     for ax, method, intervals in zip(axs, methods, intervals_list):
#         ax.plot(new_time, smoothed_intensity_scores,color='black')
        
#         total_duration = 0
#         for start, end in intervals:
#             start, end = int(start), int(end)
#             # 슬라이싱
#             if 'Threshold' in method:
#                 ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='blue', linewidth=3)
#             else:
#                 ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='red', linewidth=3)
#             duration = end - start + 1
#             total_duration += duration 
#             mid_point = (start + end) // 2
#             ax.text(new_time[mid_point], smoothed_intensity_scores[mid_point], 
#                      f'{duration}s', color='black', fontweight='bold', fontsize=10,
#                      ha='center', va='bottom')
            
#         if 'Threshold Method' in method:
#             ax.axhline(y=threshold_value, color='green', linestyle='--')
#             # ax.text(0, threshold_value, f'Threshold: {threshold_value:.2f}', color='green', 
#             #         fontweight='bold', fontsize=10, va='bottom')
#         for peak in peaks:
#             ax.plot(new_time[peak], smoothed_intensity_scores[peak], 'go')  # 피크에 초록색 점 표시
#             ax.text(new_time[peak], smoothed_intensity_scores[peak], f'{new_time[peak]:.0f}s', 
#                     color='green', fontweight='bold', fontsize=8, ha='center', va='bottom')

            
#         # ax.set_title(f'{method} (Total Duration: {total_duration}s)')
#         # ax.set_ylabel('Intensity')
#         ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
#         ax.xaxis.set_major_locator(ticker.MultipleLocator(120))
#         ax.grid(False)
#         ax.spines['top'].set_color('none')
#         ax.spines['right'].set_color('none')
#         ax.spines['bottom'].set_position('zero')
#         ax.spines['left'].set_position('zero')
#         # ax.set_xlabel('Time (seconds)', fontsize=10)
#         ax.yaxis.set_ticks([])
#     # plt.xticks( fontsize=14)
#     plt.legend().set_visible(False)
#     plt.legend(fontsize=7)

#     # axs[-1].set_xlabel('Time (seconds)')
#     plt.tight_layout()
#     # plt.show()
#     a, b = dp_prefer_duration
#     filename = os.path.join(output_dir, f'figure_min_{min_duration}_max_{max_duration}_dur_{a}_{b}_durweight_{duration_weight}_peak_{peak_weight}.png')
#     plt.savefig(filename)

def plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_duration, max_duration, threshold_value, dp_prefer_duration, duration_weight, peak_weight, MRD_GT, original):
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    fig, ax = plt.subplots(1, 1, figsize=(10, 2))  # DP만 그리도록 하나의 플롯 설정
    method = 'DP'
    intervals = dp_intervals

    ax.plot(new_time, original, color='gray', linewidth=1, linestyle='--', label = 'Original predict MRD' )
    ax.plot(new_time, smoothed_intensity_scores, color='#55A7BC', linewidth=2, label = 'Smoothed predict MRD')
    ax.plot(new_time, MRD_GT, color='black', linewidth=2, alpha=0.7,label = 'GT MRD')
    # numpy 배열로 변환
    vec1 = np.array(smoothed_intensity_scores)
    vec2 = np.array(MRD_GT)

    # 방법 1: numpy를 사용한 코사인 유사도 계산
    cosine_similarity_numpy = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print("Cosine Similarity (numpy):", cosine_similarity_numpy)

    total_duration = 0
    # for start, end in intervals:
    #     start, end = int(start), int(end)
    #     ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='red', linewidth=3)
        
    #     duration = end - start + 1
    #     total_duration += duration
    #     mid_point = (start + end) // 2
    #     ax.text(new_time[mid_point], smoothed_intensity_scores[mid_point], 
    #              f'{duration}s', color='black', fontweight='bold', fontsize=10,
    #              ha='center', va='bottom')
        
    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(120))
    ax.grid(False)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_position('zero')
    ax.yaxis.set_ticks([])
    ax.spines['bottom'].set_linewidth(1)  # x축 굵기
    ax.spines['left'].set_linewidth(1)   # y축 굵기

    # ax.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    a, b = dp_prefer_duration
    filename = os.path.join(output_dir, f'figure_min_{min_duration}_max_{max_duration}_dur_{a}_{b}_durweight_{duration_weight}_peak_{peak_weight}.png')
    plt.savefig(filename)



def plot_basic_mrd(start_seconds, smoothed_scores_general, output_path):
    # Generate the time range based on start_seconds
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(new_time, smoothed_scores_general, color='black')
    
    # Customize the plot
    ax.set_xlabel('Time (seconds)')
    ax.grid(False)
    
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(120))
    ax.grid(False)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_position('zero')

    ax.yaxis.set_ticks([])
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def format_func(value, tick_number):
    minutes = int(value / 60)
    return f'{minutes}'

# def plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_duration, max_duration, threshold_value, dp_prefer_duration, duration_weight, peak_weight):
#     total_duration_seconds = start_seconds[-1]
#     new_time = np.arange(0, total_duration_seconds, 1)
#     fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
#     methods = [f'DP Method (Min Duration: {min_duration}s)', 'Threshold Method', 'Knapsack Method']
#     intervals_list = [dp_intervals, threshold_intervals, knapsack_intervals]

#     for ax, method, intervals in zip(axs, methods, intervals_list):
#         ax.plot(new_time, smoothed_intensity_scores,)
        
#         total_duration = 0
#         for start, end in intervals:
#             start, end = int(start), int(end)
#             # 슬라이싱
#             ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], 'ro', markersize=2, color='red') # 점 표시
#             ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='red', linewidth=1)
#             # ax.plot(new_time[start:end+2], smoothed_intensity_scores[start:end+2], color='red', linewidth=3)
#             duration = end - start + 1
#             total_duration += duration 
#             mid_point = (start + end) // 2
#             ax.text(new_time[mid_point], smoothed_intensity_scores[mid_point], 
#                      f'{duration}s', color='black', fontweight='bold', fontsize=10,
#                      ha='center', va='bottom')
            
#         if 'Threshold Method' in method:
#             ax.axhline(y=threshold_value, color='green', linestyle='--')
#             ax.text(0, threshold_value, f'Threshold: {threshold_value:.2f}', color='green', 
#                     fontweight='bold', fontsize=10, va='bottom')
            
#         ax.set_title(f'{method} (Total Duration: {total_duration}s)')
#         ax.set_ylabel('Intensity Score')
#         ax.grid(True)
#         ax.legend()

#     axs[-1].set_xlabel('Time (seconds)')
#     plt.tight_layout()
#     # plt.show()
#     a, b = dp_prefer_duration
#     filename = os.path.join(output_dir, f'figure_min_{min_duration}_max_{max_duration}_dur_{a}_{b}_durweight_{duration_weight}_peak_{peak_weight}.png')
#     plt.savefig(filename)
    # with open(os.path.join(output_dir,"interval.pkl"), 'wb') as f:
    #     pickle.dump(intervals_list, f)


def normalize_to_0_1(lst):
    min_val = min(lst)
    max_val = max(lst)
    if max_val == min_val:  # 모든 값이 동일할 경우 예외 처리
        return [0.5] * len(lst)  # 모든 값을 0.5로 설정
    return [(x - min_val) / (max_val - min_val) for x in lst]