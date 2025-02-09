from .MABSelector import MABSelector
import numpy as np
from ..mutation_selection_util import choose_action_with_epsilon_greedy


class SWEGreedySelector(MABSelector):
    def __init__(self, actions, eps=0.3,window_size=1000, *args, **kwds):
        super().__init__(actions, *args, **kwds)
        self.eps = eps
        self.init_score_value = 0
        self.window_size = window_size
        self.arms_rewards = [[] for _ in range(len(self.actions))]
        self.update_times = [0 for _ in range(len(self.actions))]
        self.has_visited = [False for _ in range(len(self.actions))]
        self.scores = [] 

    def choose_action(self):
        for i in range(len(self.actions)):
            if not self.has_visited[i]:
                return self.actions[i], i
        scores = [np.mean(rewards) if rewards else 0.0 for rewards in self.arms_rewards]
        self.scores = scores
        action, action_index = choose_action_with_epsilon_greedy(self.actions, self.eps, scores)
        return action, action_index


    def update_inner_info(self, reward, action_index):
        self.has_visited[action_index] = True
        self.arms_rewards[action_index].append(reward)
        if len(self.arms_rewards[action_index]) > self.window_size:
            self.arms_rewards[action_index].pop(0)
