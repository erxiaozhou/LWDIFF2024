from .mutation_selector import MutationSelector
from ..mutation_selection_util import choose_action_randomly


class RandomMutationSelector(MutationSelector):
    def __init__(self, actions: list, logger=None, *args, **kwads):
        super().__init__(actions, logger)

    def choose_action(self, *args, **kwads):
        return choose_action_randomly(self.actions)

    def update_inner_info(self, *args, **kwads):
        pass

    def dump_inner_info(self, *args, **kwads):
        pass
