from method.dp import*
from method.threshold import threshold
from method.knapsack import knapsack
import time

class Run:
    def __init__(self, smoothed_intensity_scores, total_time, min_time):
        self.scores = smoothed_intensity_scores
        self.total_time = total_time
        self.max_t = total_time
        self.min_t = min_time

    def run_DP(self):
        print("===Start DP===")
        start_time = time.time()
        states = [[State(time=i, count=j, score=self.scores[i]) for j in range(self.max_t + 1)] for i in range(len(self.scores))]
        set_next_states(states, self.min_t, self.max_t)
        dp, trace = DP(states, num_points=self.total_time, max_t = self.max_t) 
        selected_points, max_score = find_path(states, dp, trace, num_points=self.total_time, max_t = self.max_t)
        grouped_points = group_consecutive_points(selected_points)
        dp_intervals = [(group[0], group[-1]) for group in grouped_points]
        end_time = time.time()
        elapsed_time = end_time - start_time
        message = f"DP end with {elapsed_time}"

        with open("process_log.txt", "a") as log:
            log.write(message + "\n")
        print(message)

        return dp_intervals
    

    def run_threshold(self):
        print("===Start threshold===")
        threshold_c, threshold_time, threshold_intervals = threshold(self.scores, self.total_time)
        return threshold_c, threshold_intervals

    
    def run_knapsack(self, segment_length):
        print("===Start knapsack===")
        knapsack_intervals = knapsack(self.scores, segment_length, self.total_time)
        return knapsack_intervals

    def run_all(self, knapsack_length):
        dp_intervals = self.run_DP()
        threshold, threshold_intervals = self.run_threshold()
        knapsack_intervals = self.run_knapsack(knapsack_length)

        return dp_intervals, threshold, threshold_intervals, knapsack_intervals
