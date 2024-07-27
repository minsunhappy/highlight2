import numpy as np

def DP(states, num_points, max_t):
    n = len(states)
    # max_t = num_points
    
    dp = np.full((n, max_t + 1, num_points + 1), -np.inf)
    dp[:, 0, 0] = 0
    trace = np.full((n, max_t + 1, num_points + 1, 4), -1, dtype=int)

    for i in range(n):
        for t in range(max_t):
            for k in range(1, num_points + 1):
                if dp[i, t, k - 1] != -np.inf:
                    for next_i, next_t in states[i][t].next_states:
                        if next_i < n and next_t < max_t:
                            new_score = dp[i, t, k - 1] + states[next_i][next_t].score
                            if new_score > dp[next_i, next_t, k]:
                                dp[next_i, next_t, k] = new_score
                                trace[next_i, next_t, k] = (i, t, next_i, next_t)

    return dp, trace

def find_path(states, dp, trace, num_points, min_time, max_time):

    n = len(states)
    max_score = -np.inf
    max_index = (-1, -1, -1)
    max_t = max_time
    for i in range(n):
        for t in range(max_t + 1):
            if t >= min_time: #마지막 점 최소 길이 넘겨야 함
                if dp[i, t, num_points] > max_score:
                    max_score = dp[i, t, num_points]
                    max_index = (i, t, num_points)

    selected_points = []
    k = num_points
    while max_index != (-1, -1, -1) and k > 0:
        max_index = tuple(trace[max_index[0], max_index[1], k])
        selected_points.append(max_index[0])
        # print(k, max_index)
        k -= 1
    
    selected_points.reverse()

    return selected_points, max_score


class State:
    def __init__(self, time, count, score):
        self.time = time #frame, f
        self.count = count # 𝑡 is the number of frames played after the last transition
        self.score = score
        self.frame = 0
        self.next_states = [] # 접근할 수 있는 인덱스 저장

    def get_info(self):
        info = f'time: {self.time}, Count: {self.count},  Next State {self.next_states}'
        print(info)


def set_next_states(states, min_time, max_t):
    n = len(states)
    for i in range(n):
        for t in range(max_t):
            if i + 1 < n and t + 1 <= max_t :
                states[i][t].next_states.append((i + 1, t + 1))
            if t >= min_time:
                for j in range(i + 2, n):
                    states[i][t].next_states.append((j, 0))


def group_consecutive_points(points):
    grouped_points = []
    group = [points[0]]
    for i in range(1, len(points)):
        if points[i] == points[i-1] + 1:
            group.append(points[i])
        else:
            grouped_points.append(group)
            group = [points[i]]
    grouped_points.append(group)
    return grouped_points