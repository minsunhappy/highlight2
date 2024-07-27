from method.dp import*
from method.threshold import threshold
from method.knapsack import knapsack
import time

class Run:
    def __init__(self, smoothed_intensity_scores, total_time, min_time, new_time, custom = False):
        self.scores = smoothed_intensity_scores
        self.total_time = total_time
        self.max_t = total_time
        self.min_t = min_time
        self.custom = custom
        self.sigma = 10
        self.new_time = new_time
        if custom is not False:
            self.scores = self.DP_customization(self.scores)

    def run_DP(self):
        print("===Start DP===")
        start_time = time.time()
        states = [[State(time=i, count=j, score=self.scores[i]) for j in range(self.max_t + 1)] for i in range(len(self.scores))]
        set_next_states(states, self.min_t, self.max_t)
        dp, trace = DP(states, num_points=self.total_time) 
        selected_points, max_score = find_path(states, dp, trace, num_points=self.total_time, min_time = self.min_t)
        grouped_points = group_consecutive_points(selected_points)
        dp_intervals = [(group[0], group[-1]) for group in grouped_points]
        end_time = time.time()
        elapsed_time = end_time - start_time
        message = f"DP end with {elapsed_time}"

        with open("process_log.txt", "a") as log:
            log.write(message + "\n")
        print(message)

        return dp_intervals
    
    def DP_customization(self, scores):
        include_points, include_interval, exclude_points, exclude_interval = self.custom

        if include_points is not None:
            for point in include_points:
                scores = self.DP_include_point(point, scores)
        if include_interval is not None:
            scores = self.DP_include_interval(include_interval, scores)

        if exclude_points is not None:
            for point in exclude_points:
                scores = self.DP_exclude_point(point, scores) 
        if exclude_interval is not None:
            scores = self.DP_exclude_interval(exclude_interval, scores)
        
        return scores

    def DP_include_point(self, point, scores):
        max_peak_value = max(scores)
        C = max_peak_value/scores[point + 1]
        gaussian = np.exp(-((self.new_time - point) ** 2) / (2 * self.sigma ** 2))
        gaussian = gaussian / gaussian.max() * C
        adjusted_scores = scores.copy()
        adjusted_scores*= (1 + gaussian)  
        return adjusted_scores

    def DP_exclude_point(self, point, scores):
        max_peak_value = max(scores)
        C = max_peak_value/scores[point + 1]
        gaussian = np.exp(-((self.new_time - point) ** 2) / (2 * self.sigma ** 2))
        gaussian = gaussian / gaussian.max() * C
        gaussian = -gaussian
        adjusted_scores = scores.copy()
        adjusted_scores*= (1 + gaussian)  
        return adjusted_scores


    def DP_include_interval(self, include_interval, scores):
        start_interval, end_interval = include_interval
        interval_scores = scores[start_interval:end_interval+1]
        average_importance_score = np.min(interval_scores)
        max_peak_value = max(scores)
        C = max_peak_value/average_importance_score
        gaussian = 0
        for i in range(start_interval, end_interval):
            gaussian += np.exp(-((self.new_time - i) ** 2) / (2 * self.sigma ** 2))
        gaussian = gaussian / gaussian.max() * (C)
        adjusted_scores = scores.copy()
        # gaussian = -gaussian
        adjusted_scores*= (1 + gaussian)
        return adjusted_scores

    
    
    def DP_exclude_interval(self, exclude_interval, scores):
        start_interval, end_interval = exclude_interval
        interval_scores = scores[start_interval:end_interval+1]
        average_importance_score = np.min(interval_scores)
        max_peak_value = max(scores)
        C = max_peak_value/average_importance_score
        gaussian = 0
        for i in range(start_interval, end_interval):
            gaussian += np.exp(-((self.new_time - i) ** 2) / (2 * self.sigma ** 2))
        gaussian = gaussian / gaussian.max() * (C)
        adjusted_scores = scores.copy()
        gaussian = -gaussian
        adjusted_scores*= (1 + gaussian)
        return adjusted_scores


    def run_threshold(self):
        print("===Start threshold===")
        threshold_c, threshold_time, threshold_intervals = threshold(self.scores, self.total_time)
        return threshold_c, threshold_intervals

    
    def run_knapsack(self, segment_length):
        print("===Start knapsack===")
        knapsack_intervals = knapsack(self.scores, segment_length, self.total_time)
        return knapsack_intervals

    def run_all(self, knapsack_length):
        threshold, threshold_intervals = self.run_threshold()
        knapsack_intervals = self.run_knapsack(knapsack_length)
        dp_intervals = self.run_DP()

        return dp_intervals, threshold, threshold_intervals, knapsack_intervals
