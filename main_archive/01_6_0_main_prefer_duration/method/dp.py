import numpy as np

def DP(states, num_points, max_t):
    n = len(states)
    max_t = num_points
    
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


def find_path(states, dp, trace, num_points=30, min_time=4):

    n = len(states)
    max_score = -np.inf
    max_index = (-1, -1, -1)
    max_t = num_points
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
    def __init__(self, time, count, score, gradient):
        self.time = time
        self.count = count
        self.score = score
        self.gradient = gradient
        self.next_states = []  # 접근할 수 있는 인덱스 저장

    def get_info(self):
        info = f'time: {self.time}, Count: {self.count}, Score: {self.score}, Gradient: {self.gradient}, Next State {self.next_states}'
        print(info)


def create_states(smoothed_intensity_scores, max_t, interval, duration_weight):
    gradient = np.gradient(smoothed_intensity_scores)
    abs_gradient = np.abs(gradient)  # 절대값 사용
    normalized_gradient = (abs_gradient - np.min(abs_gradient)) / (np.max(abs_gradient) - np.min(abs_gradient))
    
    # gradient가 있으나 현재는 쓰지 않음=
    states = [[State(time=i, count=j, score=smoothed_intensity_scores[i] + duration_weight*R_intv(j, interval), gradient=normalized_gradient[i]) 
               for j in range(max_t)] for i in range(len(smoothed_intensity_scores))]
    # states = [[State(time=i, count=j, score=smoothed_intensity_scores[i], gradient=normalized_gradient[i]) 
    #            for j in range(max_t)] for i in range(len(smoothed_intensity_scores))]
    return states

def set_next_states(states, min_time, max_t):
    n = len(states)
    for i in range(n):
        for t in range(max_t):
            if i + 1 < n and t + 1 < max_t :
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


def R_intv(x, interval):
    a, b = interval
    return np.sin(np.pi * (x - a) / (b - a))
    # if x < a:
    #     return -1
    # elif a <= x <= b:
    #     return np.sin(np.pi * (x - a) / (b - a))
    # else:
        # return 0

# def R_intv(t, interval):
#     a, b = interval
#     return np.exp(-((t - a)/b)**2 )

# def R_intv(t, interval):
#     a, b = interval
#     # print(interval, t)
#     # print(((t - a) / b)**2)
#     if ((t - a) / b)**2 != 1:
#         temp = np.exp(-1 / (1 - ((t - a) / b)**2)) * (np.abs(t - a) < b)
#         x = temp/np.exp(-1)
#         # x =  2 * (temp / np.exp(-1)) - 1
#         return x
#     else:
#         return 0
        
# def R_intv(t, interval):
#     a, b = interval
#     # divide = 5
#     if t <= a:
#         return np.exp(-((t - 4)/b)**2 )
#     elif a < t <= b:
#         return 1
#     else:  # t > 150
#         return np.exp(-((t - a)/b)**2 )
