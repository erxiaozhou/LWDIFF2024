from logging import Logger
from pathlib import Path
from typing import List, Optional
from extract_dump.analyze_exec_instant import _get_can_instantiate, at_least_one_can_instantiate
from extract_dump.data_comparer import diffResult
from extract_dump import dumpData
from file_util import check_dir, cp_file, save_json
from log_content_util.get_key_util import rawRuntimeLogs
from util.util import execStatus
from extract_dump.retrieve_coverage import CoverageAll, oneExecCoverage


class caseExecResult:
    def __init__(self, trigger_tester_exception,
                 difference_reason: Optional[diffResult] = None,
                 dumped_results: Optional[List[dumpData]] = None,
                 is_valid:Optional[bool]=None,
                 caseCoverage:Optional[oneExecCoverage]=None
                 ) -> None:
        self.trigger_tester_exception = trigger_tester_exception
        self.difference_reason = difference_reason
        self.dumped_results = dumped_results
        self.is_valid = is_valid
        self.caseCoverage = caseCoverage
        if trigger_tester_exception:
            self.can_success_num = 0
        else:
            self.can_success_num = sum([_.is_success for _ in self.exec_statuss])
            print('#@$VDFVDFSBDSFGBG', 'self.can_success_num', self.can_success_num)

    def copy(self):
        return caseExecResult(
            trigger_tester_exception=self.trigger_tester_exception,
            difference_reason=self.difference_reason,
            dumped_results=self.dumped_results,
            is_valid=self.is_valid,
            caseCoverage=self.caseCoverage
        )

    @property
    def can_instantiate_(self):
        assert self.dumped_results is not None
        return self.can_init_num > 0

    @property
    def can_init_num(self):
        assert self.dumped_results is not None
        return _get_can_instantiate(self.dumped_results)

    @property
    def exec_statuss(self)-> list[execStatus]:
        assert self.dumped_results is not None
        exec_statuss = []
        for _ in self.dumped_results:
            assert _.cli_result is not None
            cli_result = _.cli_result
            assert cli_result.exec_status is not None
            exec_statuss.append(cli_result.exec_status)
        return exec_statuss

    @property
    def all_can_success(self):
        return self.can_success_num == len(self.exec_statuss)

    @property
    def at_least_two_success(self):
        return self.can_success_num >= 2

    @property
    def at_least_one_success(self):
        return self.can_success_num > 0

    @property
    def has_timeout(self):
        return any([_.is_timeout for _ in self.exec_statuss])

    @property
    def has_crash(self):
        return any([_.is_crash for _ in self.exec_statuss])

    @property
    def case_can_be_seed(self):
        if self.trigger_tester_exception:
            # print('trigger_tester_exception')
            return False
        if self.has_timeout:
            # print('has_timeout')
            return False
        if not self.is_valid:
            # print('not self.is_valid')
            return False
        if not self.can_instantiate_:
            # print('not self.can_instantiate_')
            return False
        # if self.has_crash:  #  ，diff， mutate  
        #     return False
        return self.at_least_two_success


def init_case_info_in_db(collection, actions):
    # *   necessary for tester to log
    generated_cases_info_init = {"all": 0, "success": 0, "cause_diff": 0, "can_init": 0, "mutate_times":0, "cur_test_time":0}
    for action in actions:
        query: dict[str, Union[str, int]] = get_case_exec_info_query(action) # type: ignore
        # d = {"action": action}
        query.update(generated_cases_info_init)
        collection.insert_one(query)


def update_cases_info(collection, action, non_tester_exception_case_paths, case_exec_info_list, cur_test_time):
    query = get_case_exec_info_query(action)
    generated_cases_info_update = generated_cases_info_update = {
        "all": len(non_tester_exception_case_paths), 
        "success": len([1 for _ in case_exec_info_list if _.at_least_one_success]), 
        "can_init": len([1 for _ in case_exec_info_list if _.can_instantiate_]), 
        "cause_diff": len([1 for _ in case_exec_info_list if not _.difference_reason.no_diff]),
        "mutate_times": 1
    }
    collection.update_one(query, {"$inc": generated_cases_info_update})
    collection.update_one(query, {"$set": {"cur_test_time": cur_test_time}})


def save_cannot_init_cases(custom_log_dir, seed_path, action, case_exec_info_list, non_tester_exception_case_paths):
    return 
    store_case_dir = check_dir(custom_log_dir / 'debug_cases')
    if action in ['non_v128_block_mutate', 'deep_block_mutate', 'deep_block_mutate2']:
        for _exec_info, path in zip(case_exec_info_list, non_tester_exception_case_paths):
            if not _exec_info.can_instantiate_:
                new_path = store_case_dir / Path(path).name
                cp_file(path, new_path)
                # print('=-=-=-=-=' * 20)
                # assert 0
                new_seed_path = store_case_dir / f'{Path(path).stem}_seed.wasm'
                if not new_seed_path.exists():
                    cp_file(seed_path, new_seed_path)
    sop_case_dir = check_dir(custom_log_dir / 'sop_cases')
    if action == 'special_op_mutate':
        for _exec_info, path in zip(case_exec_info_list, non_tester_exception_case_paths):
            if not _exec_info.can_instantiate_:
                new_path = sop_case_dir / Path(path).name
                cp_file(path, new_path)
                new_seed_path = sop_case_dir / f'{Path(path).stem}_seed.wasm'
                if not new_seed_path.exists():
                    cp_file(seed_path, new_seed_path)



def guards1_cover_more_or_equal_than_guards2(guards1, guards2):
    if len(guards1 - guards2) >= 0 and len(guards2 - guards1) == 0:
        return True
    return False


def new_guards_meet_new_guard(new_case_guards, ori_case_guards):
    if len(new_case_guards - ori_case_guards) > 2:
        return True
    return False


def new_guards_meet_new_rare_guard(new_case_guards, ori_case_guards, rare_guards):
    new_rare_guards = new_case_guards.intersection(rare_guards)
    ori_rare_guards = ori_case_guards.intersection(rare_guards)
    if len(new_rare_guards - ori_rare_guards) > 0:
        return True
    return False

def get_case_exec_info_query(action):
    return {
        'type': 'case_exec_info',
        'action': action
    }


def get_each_epoch_status_query(action, cov_rate, cluster_num, time):
    return {
        'type': 'each_epoch_status',
        'action': action,
        'cov_rate': cov_rate,
        'cluster_num': cluster_num,
        'time': time
    }


def get_can_be_seed_check_query(p, can_be_seed, seed_len):
    p = str(p)
    return {
        'type': 'can_be_seed_check',
        'file_name': p,
        'can_be_seed': can_be_seed,
        'seed_len': seed_len
    }
    
def get_popped_seed_query(p, trigger_tester_exception, has_timeout, is_valid, at_least_one_success):
    p = str(p)
    return {
        'type': 'popped_seed',
        'file_name': p,
        'trigger_tester_exception': trigger_tester_exception,
        'has_timeout': has_timeout,
        'is_valid': is_valid,
        'at_least_one_success': at_least_one_success
        
    }

def update_guards_in_collection(collection, visited_guards, total_guard_num):
    visited_guards = list(visited_guards)
    collection.update_one({'type': 'code_cov_unique_guards'}, {'$set': {'visited_guards': visited_guards, 'total_guard_num': total_guard_num}}, upsert=True)

def update_cov_after_exec_new_cases(coverage_summary:CoverageAll, all_success_cov:CoverageAll, case_exec_info_list:List[caseExecResult]):
    # * necessary for tester to maintain some information
    for case_exec_info in case_exec_info_list:
        assert case_exec_info.caseCoverage is not None
        coverage_summary.update_coverage_info(case_exec_info.caseCoverage)
        if case_exec_info.all_can_success:
            all_success_cov.update_coverage_info(case_exec_info.caseCoverage)
