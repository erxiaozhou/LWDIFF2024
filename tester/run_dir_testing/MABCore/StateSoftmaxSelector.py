from .MABSelector import MABSelector
import numpy as np
from .Softmax import SoftmaxSelector

class StateSoftmaxSelector(MABSelector):
    def __init__(self, actions, temperature=0.4, window_size=1000, *args, **kwds):
        super().__init__(actions, *args, **kwds)
        self.temperature = temperature
        self.window_size = window_size
        self.inner_selectors = {}

    def choose_action(self, state_idx):
        if state_idx not in self.inner_selectors:
            self.inner_selectors[state_idx] = SoftmaxSelector(self.actions, self.temperature, self.window_size)
        return self.inner_selectors[state_idx].choose_action()

    def update_inner_info(self, reward, action_index, state_idx):
        assert state_idx in self.inner_selectors
        self.inner_selectors[state_idx].update_inner_info(reward, action_index)

    @property
    def scores(self):
        # TBD
        inner_selector_scores = list(map(lambda x: x.scores, self.inner_selectors.values()))
        return np.array(inner_selector_scores).tolist()
        return 
    


