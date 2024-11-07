import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
import matplotlib.ticker as ticker



def plot_summaries(output_dir, start_seconds, smoothed_intensity_scores, dp_intervals, threshold_intervals, knapsack_intervals, min_duration, max_duration, threshold_value, dp_prefer_duration, duration_weight, peak_weight, a_include, b_include):
    total_duration_seconds = start_seconds[-1]
    new_time = np.arange(0, total_duration_seconds, 1)
    fig, ax = plt.subplots(1, 1, figsize=(10, 2), sharex=True)
    methods = ['DP']
    # methods = [f'DP', 'Threshold']
    intervals_list = [dp_intervals, knapsack_intervals]

    ax.plot(new_time, smoothed_intensity_scores, color='black')
    
    total_duration = 0
    for start, end in dp_intervals:
        start, end = int(start), int(end)
        # 슬라이싱
        # ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='red', 'ro', markersize=2, color='red') # 점 표시
        ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='blue', linewidth=3)
        # ax.plot(new_time[start:end+1], smoothed_intensity_scores[start:end+1], color='red', linewidth=3)
        # ax.plot(new_time[start:end+2], smoothed_intensity_scores[start:end+2], color='red', linewidth=3)
        duration = end - start + 1
        total_duration += duration 
        mid_point = (start + end) // 2
        ax.text(new_time[mid_point], smoothed_intensity_scores[mid_point], 
                     f'{duration}s', color='black', fontweight='bold', fontsize=10,
                     ha='center', va='bottom')
        
    # ax.set_title(f'{method} (Total Duration: {total_duration}s)')
    # ax.set_ylabel('MRD')
    ax.grid(False)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_position('zero')
    print(len(smoothed_intensity_scores))
    ax.scatter(a_include, [smoothed_intensity_scores[x] for x in a_include], color='red', label='a_include', zorder=3)

    # b_include 위치에 파란색 점 표시
    ax.scatter(b_include, [smoothed_intensity_scores[x] for x in b_include], color='blue', label='b_include', zorder=3)

    ax.yaxis.set_ticks([])

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(180))
    plt.xticks()
    plt.legend(fontsize=7)
    ax.legend().set_visible(False)


    # axs[-1].set_xlabel('Time (seconds)')
    plt.tight_layout()
    # plt.show()
    a, b = dp_prefer_duration
    filename = os.path.join(output_dir, f'figure_min_{min_duration}_max_{max_duration}_dur_{a}_{b}_durweight_{duration_weight}_peak_{peak_weight}.png')
    plt.savefig(filename)



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