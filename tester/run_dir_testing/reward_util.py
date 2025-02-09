from functools import lru_cache
from pathlib import Path
from typing import List
from extract_dump.retrieve_coverage import CoverageAll, trigger_new_guards
from file_util import get_logger
from .seed_scheduler.seed_select_info_util import SeedSelectInfo
from .util import caseExecResult, guards1_cover_more_or_equal_than_guards2, new_guards_meet_new_guard, new_guards_meet_new_rare_guard


SUPPORT_REWARD_TYPES = ['common', 'log', 'common_another']
REWARD_TYPES_REQ_STATES = ['log']


def has_reward_requires_states(reward_type_list:List[str]) -> bool:
    for reward_type in reward_type_list:
        assert reward_type in SUPPORT_REWARD_TYPES
        if reward_type in REWARD_TYPES_REQ_STATES:
            return True
    return False


def reward_factory(reward_type_list:List[str], case_exec_info_list, states=None, last_seed_exec_result=None, coverage_summary=None):
    total_reward = 0
    for reward_type in reward_type_list:
        assert reward_type in SUPPORT_REWARD_TYPES
        if reward_type == 'common':
            assert last_seed_exec_result is not None
            total_reward += cal_common_reward(case_exec_info_list, last_seed_exec_result, coverage_summary)
        elif reward_type == 'log':
            raise NotImplementedError
        elif reward_type == 'common_another':
            assert last_seed_exec_result is not None
            assert coverage_summary is not None
            total_reward += cal_common_reward_another(case_exec_info_list, last_seed_exec_result, coverage_summary)
    return total_reward


def cal_common_reward_for_ci_selector(case_exec_info_list_list:List[List[caseExecResult]], last_seed_exec_result:SeedSelectInfo, coverage_summary:CoverageAll, all_success_cov:CoverageAll):
    pass
    ori_unique_guards = coverage_summary.visited_guards.copy()
    all_success_unique_guards = all_success_cov.visited_guards.copy()
    one_iter_guards = [last_seed_exec_result.unique_visited_guards.copy()]
    all_success = []
    for case_exec_info_list in case_exec_info_list_list[::-1]:
        if len(case_exec_info_list) == 0:
            unique_guards = set()
            all_success.append(False)
        else:
            assert len(case_exec_info_list) == 1
            unique_guards = case_exec_info_list[0].caseCoverage.unique_visited_guards
            all_success.append(case_exec_info_list[0].all_can_success)
        one_iter_guards.append(unique_guards)
  
    # calculate one step reward
    one_step_rewards = [0] * len(case_exec_info_list_list)
    one_step_new_cov_nums = [] 
    for idx in range(len(one_iter_guards)-1):
        trigger_all_success_new_cov = False
        trigger_new_cov = False
        ori_unique_guards.update(one_iter_guards[idx])
        if all_success[idx]:
            all_success_unique_guards.update(one_iter_guards[idx])
            all_success_new_cov_num = len(one_iter_guards[idx+1] - all_success_unique_guards)
        else:
            all_success_new_cov_num = 0
        new_guard_num = len(one_iter_guards[idx+1] - ori_unique_guards)
        one_step_new_cov_nums.append(new_guard_num)
        trigger_new_cov = new_guard_num > 2
        trigger_all_success_new_cov = all_success_new_cov_num > 2
        reward = 0
        if trigger_new_cov:
            if all_success[idx]:
                reward = 100
            else:
                reward = 50
        elif trigger_all_success_new_cov:
            reward += 50
            
        # if new_guard_num > 2:
        #     # if case_exec_info_list
        #     reward = 100 if all_success[idx] else 50
        one_step_rewards[idx] += reward
    final_rewards = []
    for idx in range(len(one_step_rewards)):
        final_rewards.append(cal_dec_reward(tuple(one_step_rewards[idx:]), 0.933))
    return final_rewards, one_step_new_cov_nums
        
        
        


@lru_cache
def cal_dec_reward(one_step_rewards, rate):
    sum_ = 0
    for idx, reward in enumerate(one_step_rewards):
        sum_ += reward * (rate**idx)
    return sum_


def cal_common_reward(case_exec_info_list:List[caseExecResult], last_seed_exec_result:SeedSelectInfo, coverage_summary:CoverageAll) -> float:
    logger = get_logger('reward_logger', 'tt/reward.log')
    for _ in case_exec_info_list:
        assert not _.trigger_tester_exception
    if len(case_exec_info_list) == 0:
        return  0
    assert last_seed_exec_result is not None
    invalid_reward = 0  # -0.5
    failed_case_reward = 0  # -0.5
    worse_reward = 0 #-1
    new_cov_reward = 0
    all_success_new_cov_reward = 2 * new_cov_reward
    more_success_reward = 0
    global_new_cov_reward = 50
    
    failed_case_num = 0
    worse_case_num = 0
    new_cov_num = 0
    all_success_new_cov_num = 0
    more_success_num = 0
    global_new_cov_num = 0
    invalid_num = 0
    common_unique_guards = coverage_summary.common_guards
    last_rare_unique_guards = last_seed_exec_result.unique_visited_guards - common_unique_guards
    

    for case_exec_info in case_exec_info_list:
        new_rare_guards = case_exec_info.caseCoverage.unique_visited_guards - common_unique_guards

        
        assert case_exec_info.caseCoverage is not None
        new_guard_num = trigger_new_guards(case_exec_info.caseCoverage, coverage_summary)
        if new_guard_num:
            logger.info(f'new guard num: {new_guard_num}')
        if new_guard_num>1:
            global_new_cov_num += 1 #min(max(new_guard_num-2, 0), 10)
            if case_exec_info.all_can_success:
                global_new_cov_num += 1
            continue
        if case_exec_info.can_success_num == 0:
            failed_case_num += 1
        if guards1_cover_more_or_equal_than_guards2( last_rare_unique_guards, new_rare_guards):
            worse_case_num += 1
        if new_guards_meet_new_guard(new_rare_guards, last_rare_unique_guards) and case_exec_info.at_least_two_success:
            if case_exec_info.all_can_success:
                all_success_new_cov_num += 1
            else:
                new_cov_num += 1
        if case_exec_info.can_success_num > last_seed_exec_result.can_success_num:
            more_success_num += 1
        if not case_exec_info.is_valid:
            invalid_num += 1
    total_reward = 0
    total_reward += all_success_new_cov_num * all_success_new_cov_reward
    total_reward += invalid_reward * invalid_num
    total_reward += global_new_cov_num * global_new_cov_reward
    total_reward += failed_case_num * failed_case_reward
    total_reward += worse_case_num * worse_reward
    total_reward += new_cov_num * new_cov_reward
    total_reward += more_success_num * more_success_reward
    return total_reward



def cal_common_reward_another(case_exec_info_list:List[caseExecResult], last_seed_exec_result:SeedSelectInfo, coverage_summary:CoverageAll) -> float:
    for _ in case_exec_info_list:
        assert not _.trigger_tester_exception
    if len(case_exec_info_list) == 0:
        return  0
    assert last_seed_exec_result is not None
    failed_case_reward = -0.5
    worse_reward = -1
    new_cov_reward = 0.5
    
    failed_case_num = 0
    worse_case_num = 0
    new_cov_num = 0

    for case_exec_info in case_exec_info_list:
        assert case_exec_info.caseCoverage is not None
        if case_exec_info.can_success_num == 0:
            failed_case_num += 1
        if guards1_cover_more_or_equal_than_guards2( last_seed_exec_result.unique_visited_guards, case_exec_info.caseCoverage.unique_visited_guards):
            worse_case_num += 1
        elif trigger_new_guards(case_exec_info.caseCoverage, coverage_summary):
            new_cov_num += 1
    total_reward = 0
    total_reward += failed_case_num * failed_case_reward
    total_reward += worse_case_num * worse_reward
    total_reward += new_cov_num * new_cov_reward
    return total_reward
