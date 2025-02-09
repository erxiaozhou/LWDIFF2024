class MABSelector:
    def __init__(self, actions, *args, **kwds):
        self.actions = actions

    def choose_action(self, *args, **kwads):
        raise NotImplementedError

    def update_inner_info(self, *args, **kwads):
        raise NotImplementedError