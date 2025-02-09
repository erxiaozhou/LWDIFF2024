from .MABSelector import MABSelector
import numpy as np


class SoftmaxSelector(MABSelector):
    def __init__(self, actions, temperature=0.4, window_size=1000, *args, **kwds):
        super().__init__(actions, *args, **kwds)
        self.temperature = temperature
        self.action_num = len(actions)
        self.window_size = window_size
        # self.scores = np.zeros(self.action_num, dtype=np.float32)
        self.arms_rewards = [[] for _ in range(self.action_num)]
        self.has_visited = [False for _ in range(self.action_num)]
        self.scores = np.zeros(self.action_num, dtype=np.float32)  # Q(a)
        self.counts = np.zeros(self.action_num, dtype=np.int64)  # Count of each action

    def choose_action(self):
        for i in range(len(self.actions)):
            if not self.has_visited[i]:
                return self.actions[i], i
        # Calculate the probabilities of each action
        values = np.array([np.mean(rewards) if rewards else 0.0 for rewards in self.arms_rewards])
        values[values>500] = 500
        exp_values = np.exp(values / self.temperature)

        sum_ = np.sum(exp_values) 
        if sum_ == 0:
            probabilities = np.ones(self.action_num) / self.action_num
        else:
            probabilities = exp_values / np.sum(exp_values)
        self.scores = [values.tolist(), probabilities.tolist()]
        # Select an action based on the probabilities
        # print(probabilities, values, exp_values)
        action_index = np.random.choice(self.action_num, p=probabilities)
        action = self.actions[action_index]
        
        return action, action_index

    def update_inner_info(self, reward, action_index):
        self.has_visited[action_index] = True
        self.arms_rewards[action_index].append(reward)
        if len(self.arms_rewards[action_index]) > self.window_size:
            self.arms_rewards[action_index].pop(0)
