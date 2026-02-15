import numpy as np


def knapSack(W, wt, val, n):
	""" Maximize the value that a knapsack of capacity W can hold. You can either put the item or discard it, there is
	no concept of putting some part of item in the knapsack.

	:param int W: Maximum capacity -in frames- of the knapsack.
	:param list[int] wt: The weights (lengths -in frames-) of each video shot.
	:param list[float] val: The values (importance scores) of each video shot.
	:param int n: The number of the shots.
	:return: A list containing the indices of the selected shots.
	"""
	K = [[0 for _ in range(W + 1)] for _ in range(n + 1)]

	# Build table K[][] in bottom up manner
	for i in range(n + 1):
		for w in range(W + 1):
			if i == 0 or w == 0:
				K[i][w] = 0
			elif wt[i - 1] <= w:
				K[i][w] = max(val[i - 1] + K[i - 1][w - wt[i - 1]], K[i - 1][w])
			else:
				K[i][w] = K[i - 1][w]

	selected = []
	w = W
	for i in range(n, 0, -1):
		if K[i][w] != K[i - 1][w]:
			selected.insert(0, i - 1)
			w -= wt[i - 1]

	return selected


# 이어지는 애들끼리는 이어지게
def merge_intervals(intervals):
    if not intervals:
        return []
    
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    for interval in sorted_intervals:
        if not merged or interval[0] > merged[-1][1] + 1:
            merged.append(interval)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], interval[1]))
    
    return merged

def knapsack(smoothed_intensity_scores, segment_length, time):
    total_length = len(smoothed_intensity_scores)
    # segment_frames = int(segment_length * (total_length / new_time[-1]))
    n_segments = total_length // segment_length
    segments = np.array_split(smoothed_intensity_scores, n_segments)
    
    segment_scores = [segment.mean() for segment in segments]
    segment_lengths = [len(segment) for segment in segments]
    picks = knapSack(time, segment_lengths, segment_scores, n_segments)
    
    selected_intervals = []
    for pick in sorted(picks):
        start = pick * segment_length
        end = min((pick + 1) * segment_length, total_length)
        selected_intervals.append((start, end - 1))
    
    return merge_intervals(selected_intervals)

