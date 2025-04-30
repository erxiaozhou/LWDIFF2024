from pathlib import Path
import random


class SeedSchedulerBase:
    def __init__(self, seed_pool, logger=None) -> None:
        self.seed_pool = [str(s) for s in seed_pool]
        self.ori_seeds = set(self.seed_pool)
        self.logger = logger

    def select_seed_and_energy(self, *args, **kwds):
        raise NotImplementedError

    def update_seed_pool(self, *args, **kwds) -> list[str]:
        raise NotImplementedError

    def is_ori_seed(self, seed_path):
        return str(seed_path) in self.ori_seeds

    def has_seeds(self):
        raise NotImplementedError

    def trim_seed_pool(self):
        raise NotImplementedError

    def _select_seed_and_exec(self):
        raise NotImplementedError

    def _select_a_seed(self, *args, **kwds):
        raise NotImplementedError

    def _case_can_be_seed(self, *args, **kwds):
        raise NotImplementedError

    @classmethod
    def from_seed_dir(cls, seed_dir, *args, **kwds):
        raise NotImplementedError
