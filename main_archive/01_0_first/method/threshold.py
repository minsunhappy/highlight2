import numpy as np

def find_intervals(smoothed_intensity_scores, a):
    time = np.arange(len(smoothed_intensity_scores))
    above_threshold = smoothed_intensity_scores > a
    changes = np.diff(above_threshold.astype(int))
    
    starts = time[1:][changes == 1]
    ends = time[1:][changes == -1]
    
    if above_threshold[0]:
        starts = np.insert(starts, 0, 0)
    if above_threshold[-1]:
        ends = np.append(ends, len(time) - 1)
    
    intervals = list(zip(starts, ends))
    total_time = sum(end - start for start, end in intervals)
    
    return total_time, intervals

def threshold(smoothed_intensity_scores, t):
    lst = np.linspace(0, 1, 100) # 100등분함
    closest_diff = float('inf')
    threshold = None
    best_total_time = None
    best_intervals = None
    
    for a in lst:
        total_time, intervals = find_intervals(smoothed_intensity_scores, a)
        diff = abs(total_time - t)
        if diff < closest_diff:
            closest_diff = diff
            threshold = a
            best_total_time = total_time
            best_intervals = intervals
    
    return threshold, best_total_time, best_intervals

