from .MABCore.MABSelector import MABSelector
from .EAScheduler import EASolution, EvaPeformance, PhaseSchedulerBase
from .MABCore.MABUCBT import MABUCBTSelector
import random

class MABSolutionSelector(PhaseSchedulerBase):
    def __init__(self, phase_names, selector:MABSelector):
        
        # self.selector = MABUCBTSelector(phase_names)
        self.selector = selector
        self.phase_names = phase_names
        assert self.phase_names == selector.actions
        self.basic_time_slot = 30
        self.phase_solutions = []
        for phase_name in phase_names:
            self.phase_solutions.append(EASolution([phase_name], [self.basic_time_slot]))
        self.last_phase_idx = None

    def get_a_solution(self, *args, **kwds):
        phase_name, phase_idx = self.selector.choose_action()
        # return super().get_a_solution(*args, **kwds)
        self.last_phase_idx = phase_idx
        return self.phase_solutions[phase_idx], None

    @property
    def _soluitons(self):
        return self.selector.scores
    
    def update_by_performance(self, performanc, logger):
        assert self.last_phase_idx is not None
        # score = sum([p.score() for p in performance_list])
        score = performanc.score(20)
        logger.info(f'Phase {self.last_phase_idx} {self.phase_names[self.last_phase_idx]}: {score}')
        self.selector.update_inner_info(score, self.last_phase_idx)
