from .MABSelector import MABSelector
from ..mutation_selection_util import choose_action_with_epsilon_greedy


class EpsGreedySelector(MABSelector):
    def __init__(self, actions, eps=0.1, init_score_value=0.0, *args, **kwds):
        super(EpsGreedySelector, self).__init__(actions, *args, **kwds)
        self.eps = eps
        self.init_score_value = init_score_value
        self.scores = [self.init_score_value for _ in range(len(self.actions))]
        self.update_times = [0 for _ in range(len(self.actions))]

    def choose_action(self):
        for i in range(len(self.actions)):
            if self.update_times[i] == 0:
                return self.actions[i], i
            
        action, action_index = choose_action_with_epsilon_greedy(self.actions, self.eps, self.scores)
        return action, action_index

    def update_inner_info(self, reward, action_index):
        self.update_times[action_index] += 1
        n = self.update_times[action_index]
        ori_state_value = self.scores[action_index]
        add_value = (reward - ori_state_value) / (n * 1.0)
        self.scores[action_index] += add_value
