from typing import Tuple


class MutationSelector:
    def __init__(self, actions: list, logger):
        self.actions = actions
        for action in actions:
            assert isinstance(action, str)
        assert logger is not None
        self.logger = logger

    def choose_action(self, *args, **kwds) -> Tuple[str, int]:
        raise NotImplementedError

    def update_inner_info(self, *args, **kwads):
        raise NotImplementedError

    def dump_inner_info(self, *args, **kwads):
        raise NotImplementedError

    def _calculate_reward(self, *args, **kwads):
        raise NotImplementedError
