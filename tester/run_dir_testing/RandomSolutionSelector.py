from typing import List
from .EAScheduler import EASolution, EvaPeformance, PhaseSchedulerBase
import random


class RandomSolutionSelector(PhaseSchedulerBase):
    def __init__(self, phase_names):
        self.phase_names = phase_names
        self.basic_time_slot = 30
        self.phase_solutions = []
        self._soluitons = []
        for phase_name in phase_names:
            self.phase_solutions.append(EASolution([phase_name], [self.basic_time_slot]))

    def get_a_solution(self, *args, **kwds):
        phase_idx = random.randint(0, len(self.phase_names)-1)
        return self.phase_solutions[phase_idx], None

    def update_by_performance(self, performanc, logger):
        pass
    