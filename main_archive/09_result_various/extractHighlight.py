from method.dp import*
from method.threshold import threshold
from method.knapsack import knapsack
import time

class Run:
    def __init__(self, smoothed_scores_DP, smoothed_scores_general, total_time, t_min, t_max, dp_prefer_duration, duration_weight):
        self.scores_DP = smoothed_scores_DP
        self.scores_general =  smoothed_scores_general
        self.total_time = total_time
        self.max_t = t_max
        self.min_t = t_min
        self.interval = dp_prefer_duration
        self.duration_weight = duration_weight

    def run_DP(self):
        print("start DP")
        start_time = time.time()
        states = create_states(self.scores_DP , self.max_t, self.interval, self.duration_weight)
        set_next_states(states, self.min_t, self.max_t)
        dp, trace = DP(states, self.total_time, self.max_t, self.duration_weight, self.interval) 
        selected_points, max_score = find_path(states, dp, trace, num_points=self.total_time, min_time = self.min_t, max_time = self.max_t)
        grouped_points = group_consecutive_points(selected_points)
        dp_intervals = [(group[0], group[-1]) for group in grouped_points]
        end_time = time.time()
        elapsed_time = end_time - start_time
        message = f"DP end with {elapsed_time}"

        with open("process_log.txt", "a") as log:
            log.write(message + "\n")
        print(message)
        dp_reward_sum = 0
        for idx in selected_points:
            dp_reward_sum += self.scores_DP[idx]
        return dp_intervals, dp_reward_sum
    

    def run_threshold(self):
        # print("===Start threshold===")
        threshold_c, threshold_time, threshold_intervals = threshold(self.scores_general, self.total_time)
        return threshold_c, threshold_intervals

    
    def run_knapsack(self, segment_length):
        # print("===Start knapsack===")
        knapsack_intervals = knapsack(self.scores_general, segment_length, self.total_time)
        threshold_reward_sum = 0
        for elem in knapsack_intervals:
            start, end = elem
            for i in list(range(start, end+1)):
                threshold_reward_sum += self.scores_DP[i]
        return knapsack_intervals, threshold_reward_sum

    def run_all(self, knapsack_length):
        threshold, threshold_intervals = self.run_threshold()
        # knapsack_intervals = []
        knapsack_intervals, threshold_reward_sum = self.run_knapsack(knapsack_length)
        # dp_intervals, dp_reward_sum = self.run_knapsack(knapsack_length)
        dp_intervals, dp_reward_sum = self.run_DP()

        return dp_intervals, dp_reward_sum, threshold, threshold_intervals, knapsack_intervals, threshold_reward_sum
