import numpy as np
from .dp import group_consecutive_points

def find_intervals(smoothed_intensity_scores, a):
    time = np.arange(len(smoothed_intensity_scores))
    above_threshold = smoothed_intensity_scores > a
    points = time[above_threshold]
    # print(points)
    if len(points) != 0:
        grouped_points = group_consecutive_points(points)

        total_time = len(points)
        
        intervals = [(group[0], group[-1]) for group in grouped_points]
    else:
        total_time = float('inf')
        intervals = None
    
    return total_time, intervals

def threshold(smoothed_intensity_scores, t):
    lst = np.linspace(0, 1, 101) # 100등분함
    closest_diff = float('inf')
    threshold = None
    best_total_time = None
    best_intervals = None
    
    for a in lst:
        total_time, intervals = find_intervals(smoothed_intensity_scores, a)
        diff = abs(total_time - t)
        # print(a)
        if diff < closest_diff:
            closest_diff = diff
            threshold = a
            best_total_time = total_time
            best_intervals = intervals
    # print(best_intervals)
    return threshold, best_total_time, best_intervals

