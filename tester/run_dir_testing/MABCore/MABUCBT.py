from random import choice
import numpy as np
import math
from .MABSelector import MABSelector


class MABUCBTSelector(MABSelector):
    def __init__(self, actions, *args, **kwds):
        self.action_num = len(actions)
        self.values = np.zeros(self.action_num, dtype=np.float32)
        self.counts = np.zeros(self.action_num, dtype=np.float32)
        self.squares = np.zeros(self.action_num, dtype=np.float32)
        self.total_counts = 0
        super(MABUCBTSelector, self).__init__(actions, *args, **kwds)

    def choose_action(self):
        # ensure each action can be execued 100 times
        candi_action_idxs = [idx for idx in range(len(self.actions)) if self.counts[idx] < 1]
        if len(candi_action_idxs) > 0:
            action_index = choice(candi_action_idxs)
            action = self.actions[action_index]
            return action, action_index

        ucb_values = np.zeros(self.action_num, dtype=np.float32)
        for arm in range(self.action_num):
            average_reward = self.values[arm]
            variance_estimate = self.squares[arm] - average_reward**2
            exploration_term = math.sqrt(2 * math.log(self.total_counts) / self.counts[arm])
            ucb_values[arm] = average_reward + math.sqrt(min(1/4, variance_estimate + exploration_term))

        action_index = np.argmax(ucb_values)
        action = self.actions[action_index]
        return action, action_index

    @property
    def scores(self):
        return self.values

    def update_inner_info(self, reward, action_index):
        self.counts[action_index] += 1
        self.total_counts += 1
        n = self.counts[action_index]
        value = self.values[action_index]
        square = self.squares[action_index]
        # 
        self.values[action_index] = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        # ，
        self.squares[action_index] = ((n - 1) / float(n)) * square + (1 / float(n)) * reward *reward
