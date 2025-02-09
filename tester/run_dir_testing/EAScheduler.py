from random import choice
from typing import List, Optional
import numpy as np


class EASolution:
    def __init__(self, actions, time_slots):
        self._actions = actions
        self._time_slots = time_slots

    def as_iter(self):
        return zip(self._actions, self._time_slots)

    def set_actions(self, actions):
        self._actions = actions

    def set_times(self, times):
        self._time_slots = times

    def copy(self):
        return EASolution(self._actions, self._time_slots)
    def __repr__(self) -> str:
        return f'EA Solution({self._actions}, {self._time_slots})'



class EvaPeformance:
    def __init__(self, ori_visited_guards:set[int], ori_visited_all_success_guards:set[int], total_guards_num:int):
        self.ori_visited_guards = ori_visited_guards.copy()
        self.ori_visited_all_success_guards = ori_visited_all_success_guards.copy()
        
        self.new_visited_all_success_guards = set()
        self.new_visited_guards = set()
        
        self.total_guards_num = total_guards_num
        self.testing_time = None

    def set_testing_time(self, t_):
        self.testing_time = t_

    def update_coverage(self, case_exec_info, is_all_success):
        self.new_visited_guards.update(case_exec_info.caseCoverage.unique_visited_guards)
        if is_all_success:
            self.new_visited_all_success_guards.update(case_exec_info.caseCoverage.unique_visited_guards)

    @property
    def unseen_guards_num(self):
        return len(self.new_visited_guards - self.ori_visited_guards)
    @property
    def visited_guards_num(self):
        return len(self.new_visited_guards)
    @property
    def unseen_all_success_guards_num(self):
        return len(self.new_visited_all_success_guards - self.ori_visited_guards)
    
    def score(self, ulimit:Optional[int]=None):
        original_score = self.unseen_guards_num + self.unseen_all_success_guards_num * 2
        if ulimit is None:
            return original_score
        else:
            return min(original_score, ulimit)
    
    def as_data(self):
        return {
            'score': self.score(),
            'unseen_guards_num': self.unseen_guards_num,
            'visited_guards_num': self.visited_guards_num,
            # 'total_guards_num': self.total_guards_num,
            'unseen_all_success_guards_num': self.unseen_all_success_guards_num,
            
        }

    def update_by_other_performance(self, other_performance):
        self.new_visited_guards.update(other_performance.new_visited_guards)
        self.new_visited_all_success_guards.update(other_performance.new_visited_all_success_guards)
    

def determine_the_best_performance_idx(performance_list:List[EvaPeformance]):
    best_idx = 0
    best_score = performance_list[0].score()
    for idx, performance in enumerate(performance_list[1:], start=1):
        if performance.score() > best_score:
            best_idx = idx
            best_score = performance.score()
    return best_idx

# 
class PhaseSchedulerBase:
    def __init__(self) -> None:
        self.phase_names = []  # ，
    def get_a_solution(self, *args, **kwds):
        raise NotImplementedError
    
    def update_by_performance(self, *args, **kwds):
        raise NotImplementedError

class EAPhaseScheduler(PhaseSchedulerBase):
    _soluitons:list[EASolution] = []
    def __init__(self, phase_names, time_slots_list:List[List[float]]):
        self.solution_num = len(time_slots_list)
        for time_slots in time_slots_list:
            self._soluitons.append(EASolution(phase_names, time_slots))
        self.solution_queue = []
        self.solution_info_queue = []
        self.performance_queue = [[] for _ in range(self.solution_num)]
        self.tested_soluitons = [[] for _ in range(self.solution_num)]
        self.last_solution_pos = None
        self.new_solution_num = 3
        # TODO
    @classmethod
    def from_default(cls, actions, solution_num=1):
        time_slots_list = []
        for _ in range(solution_num):
            time_slots_list.append([30]*len(actions))
        return cls(actions, time_slots_list)

    def _generate_solutions_for_soluiton_idx(self, ori_solution_idx):
        ori_solution = self._soluitons[ori_solution_idx]
        new_solutions = []
        for _ in range(self.new_solution_num):
            time_slots = keep_sum_guass_mutate(ori_solution._time_slots, self.solution_num)
            new_solution = EASolution(ori_solution._actions, time_slots)
            new_solutions.append(new_solution)
        return new_solutions

    def generate_solutions_to_evaulate(self, ori_solution_idx):
        new_solutions = self._generate_solutions_for_soluiton_idx(ori_solution_idx)
        ori_solution = self._soluitons[ori_solution_idx]
        new_solutions.append(ori_solution.copy())
        return new_solutions

    def get_a_solution(self, *args, **kwds):
        if len(self.solution_queue) == 0:
            # TODO update the solutions queue first
            self._generate_a_batch_of_solutions() 
        # if self.solution_queue:
        _solution, pos = self.solution_queue.pop(0), self.solution_info_queue.pop(0)
        self.last_solution_pos = pos
        return _solution, pos
        # return self._soluitons[0]
    
    def update_by_performance(self,solution, performance, logger=None):
        assert self.last_solution_pos is not None
        self.performance_queue[self.last_solution_pos['solution_idx']].append(performance)
        self.tested_soluitons[self.last_solution_pos['solution_idx']].append(solution)
        if logger is not None:
            logger.debug(f"self.last_solution_pos['solution_idx']: {self.last_solution_pos['solution_idx']}")
            logger.debug(F"self.performance_queue {[[p.score() for p in ps] for ps in self.performance_queue]}")
            
        if len(self.performance_queue[self.last_solution_pos['solution_idx']]) == self.new_solution_num + 1:
            solution_ix = self.last_solution_pos['solution_idx']
            best_solution_idx = determine_the_best_performance_idx(self.performance_queue[solution_ix])
            self._soluitons[solution_ix] = self.tested_soluitons[solution_ix][best_solution_idx]
            # self.update_by_performance(self.last_solution_pos['solution_idx'])
            self.performance_queue[solution_ix] = []
            self.tested_soluitons[solution_ix] = []
            if logger is not None:
                logger.debug(f"solution_ix: {solution_ix}")
                logger.debug(f"best_solution_idx {best_solution_idx}")

    def inner_size(self):
        d = {
            'last_solution_pos': self.last_solution_pos,
            'performance_size': [len(p) for p in self.performance_queue],
            'solution_size': [len(s) for s in self.tested_soluitons],
            'solution_queue_size': len(self.solution_queue),
        }
        return d
        
        # 

    def _generate_a_batch_of_solutions(self, *args, **kwds):
        # determine the best solution
        # 
        for i in range(self.solution_num):
            generated_solutions = self.generate_solutions_to_evaulate(i)
            for j, new_solution in enumerate(generated_solutions):
                if j == self.new_solution_num:
                    attr = 'ori'
                else:
                    attr = f'new_{j}'
                self.solution_info_queue.append({
                    'solution_idx': i,
                    'new_solution_idx': attr,
                })
                self.solution_queue.append(new_solution)


class RandomPhaseScheduler(PhaseSchedulerBase):
    _soluitons = []
    def __init__(self, phase_names, time_slots):
        self.actions = phase_names
        self.time_slots = time_slots
        self.solution = EASolution(phase_names, time_slots)
        self._soluitons.append(self.solution)
        
    def get_a_solution(self, *args, **kwdsdanda):
        return self.solution, None

    def update_by_performance(self, *args, **kwds):
        pass
    def inner_size(self):
        pass

class FixRatioPhaseScheduler(PhaseSchedulerBase):
    pass


def keep_sum_guass_mutate(ori_list, solution_len):
    # sum_ori = sum(ori_list)
    new_list= []
    for _ in ori_list:
        elem = _ + np.random.normal(0, 10)
        if elem < 0:
            elem = 0
        new_list.append(elem)
    to_add_sum = sum(ori_list) - sum(new_list)
    possible_to_add_idxs = [idx for idx, elem in enumerate(new_list) if elem > -to_add_sum]
    print('possible_to_add_idxs', possible_to_add_idxs)
    print('to_add_sum', to_add_sum)
    print('new_list', new_list)
    to_add_idx = choice(possible_to_add_idxs)
    new_list[to_add_idx] += to_add_sum
    # mutation = np.random.normal(0, 3, solution_len)
    # new_list = [_m+_o for _m, _o in zip(mutation, ori_list)]
    # to_add_sum = -sum(mutation)
    # mutation += to_add_sum / solution_len
    return new_list
    
