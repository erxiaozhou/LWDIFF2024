from copy import deepcopy
from extract_dump.retrieve_coverage import CoverageAll
from typing import List, Optional

from run_dir_testing.MABCore.MABUCBT import MABUCBTSelector
from run_dir_testing.components.mutation_selector import MutationSelector
from ..util import caseExecResult
from ..seed_scheduler.seed_select_info_util import SeedSelectInfo
from ..reward_util import has_reward_requires_states, reward_factory, cal_common_reward_for_ci_selector
from ..MABCore.MABSelector import MABSelector
from file_util import check_dir, get_logger, get_time_string
from logging import Logger


class MutateSeqInfo:
    def __init__(self, coverage_summary:CoverageAll, all_success_cov:CoverageAll):
        self.ori_cov = deepcopy(coverage_summary)
        self.all_success_cov = deepcopy(all_success_cov)
        self.case_exec_info_list_list = []
        self.action_idxs = []
        self.iter_idx = 0
        
    def add_case_exec_info_list(self, case_exec_info_list):
        self.case_exec_info_list_list.append(case_exec_info_list)

    def update_an_epoch(self, action_idx, case_exec_info_list):
        self.action_idxs.append(action_idx)
        self.add_case_exec_info_list(case_exec_info_list)
        self.iter_idx += 1

class CIMABUCBTMutationSelector(MutationSelector):
    def __init__(self,  actions: list, logger:Optional[Logger]=None,  *args, **kwds):
        # MABUCBTSelector
        self.selectors: list[MABUCBTSelector] = [MABUCBTSelector(actions) for _ in range(10)]
        cov_log_base_dir = check_dir('/media/hdd8T1/mutation_action_log')
        logger_path = cov_log_base_dir / f'new_cov_{get_time_string()}.log'
        self.new_cov_log = get_logger('new_cov_log', logger_path)
      
        super().__init__(actions, logger=logger)

    # def _calculate_reward(self, case_exec_info_list_list:List[List[caseExecResult]], last_seed_exec_result:SeedSelectInfo, coverage_summary:CoverageAll) -> List[float]:
    #     # for _ in case_exec_info_list:
    #     #     assert len(_) == 1
    #     # case_exec_info_list = [_[0] for _ in case_exec_info_list]
    #     rewards, one_step_new_cov_nums = cal_common_reward_for_ci_selector(case_exec_info_list_list, last_seed_exec_result, coverage_summary)
    #     return rewards, one_step_new_cov_nums

    def dump_inner_info(self, logging_num, data_dir):
        pass

    def choose_action(self, iter_idx):
        selector = self.selectors[iteridx2selector_idx(iter_idx)]
        action, action_idx = selector.choose_action()
        # self.logger.info(f'iter_idx: {iter_idx} ; Scores: {self.selector.scores}')
        return action, action_idx

    def update_inner_info(self, mutation_seq_info:MutateSeqInfo, last_seed_exec_result):
        action_idxs = mutation_seq_info.action_idxs
        case_exec_info_list_list = mutation_seq_info.case_exec_info_list_list
        coverage_summary = mutation_seq_info.ori_cov
        all_success_cov = mutation_seq_info.all_success_cov
        self._update_inner_info_core(action_idxs, case_exec_info_list_list, last_seed_exec_result, coverage_summary, all_success_cov)

    def _update_inner_info_core(self, action_indexs, case_exec_info_list_list:List[List[caseExecResult]], last_seed_exec_result: SeedSelectInfo, coverage_summary: CoverageAll, all_success_cov:CoverageAll):
        # log new cov num
        
        rewards, one_step_new_cov_nums = cal_common_reward_for_ci_selector(case_exec_info_list_list, last_seed_exec_result, coverage_summary, all_success_cov)
        for one_step_new_cov_num, action_idx in zip(one_step_new_cov_nums, action_indexs):
            if one_step_new_cov_num > 0:
                self.new_cov_log.info(f'Action: {self.actions[action_idx]} ; New cov num: {one_step_new_cov_num}')
        for iter_idx, (action_idx, reward) in enumerate(zip(action_indexs, rewards)):
            self.selectors[iteridx2selector_idx(action_idx)].update_inner_info(reward, action_idx)
            self.logger.info(f'Iter: {iter_idx} ; Last chosen action: {self.actions[action_idx]} {action_idx}; reward is {reward}')
        # self.selectors


def iteridx2selector_idx(iter_idx) -> int:
    if iter_idx < 9:
        return iter_idx
    else:
        return 9
