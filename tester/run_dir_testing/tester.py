from extract_dump import at_least_one_can_instantiate
from file_util import check_dir, cp_file, rm_dir, save_json
from .tester_util import testerExecInfo
from .tester_util import testerExecPaths
from .tester_util import test_one_tc_old, post_process_arrording_to_diff_reason_update_exec_info
from generate_tcs_by_mutation_util import generate_tcs_by_mutate_bytes
from random import random
from file_util import remove_file_without_exception
from pathlib import Path
from abc import abstractmethod
from log_content_util.get_key_util import rawRuntimeLogs


class Tester:
    @abstractmethod
    def run_testing(self):
        raise NotImplementedError

    def _common_brief_info(self, **kwads):
        paras_parts = [f"<{k}:{v}>" for k, v in kwads.items()]
        paras_part = ' '.join(paras_parts)
        return f'{self.__class__.__name__} {paras_part}'


class noMutationTester(Tester):
    def __init__(self):
        pass

    def run_testing(self, exec_paths, impls, tc_paths_iterator):
        # TODO exec_paths，
        assert isinstance(exec_paths, testerExecPaths)
        para_paths = noMutationTestingPaths.from_testerExecPaths(exec_paths)
        exec_info = testing_without_mutation(para_paths, impls, tc_paths_iterator)
        return exec_info
    
    def __repr__(self):
        return self._common_brief_info()


def testing_without_mutation(exec_paths, impls, tc_paths_iterator):
    # TODO tc_paths_iterator 
    # testing_without_mutation_and_collect_can_init_tc ， noMutationTester
    # ，
    exec_info = testerExecInfo()
    for tc_name, tc_path in tc_paths_iterator:
        try:
            exec_info.ori_tc_num += 1
            tc_dumped_data_dir = check_dir(exec_paths.dumped_data_base_dir / tc_name)
            dumped_results, difference_reason = test_one_tc_old(tc_dumped_data_dir, impls, tc_path)
            can_instantiate_ = at_least_one_can_instantiate(dumped_results)
            exec_info.all_exec_times += 1
            if can_instantiate_:
                exec_info.at_least_one_to_analyze += 1
            post_process_arrording_to_diff_reason_update_exec_info(exec_paths, tc_dumped_data_dir, exec_info, tc_path, tc_name, difference_reason)
        except (RuntimeError, Exception) as e:
            cp_file(tc_path, exec_paths.except_dir)
    return exec_info


def testing_without_mutation_and_collect_can_init_tc(exec_paths, impls, tc_paths_iterator):
    exec_info = testerExecInfo()
    can_init_tc_paths = []
    for tc_name, tc_path in tc_paths_iterator:
        try:
            exec_info.ori_tc_num += 1
            tc_dumped_data_dir = check_dir(exec_paths.dumped_data_base_dir / tc_name)
            dumped_results, difference_reason = test_one_tc_old(tc_dumped_data_dir, impls, tc_path)
            can_instantiate_ = at_least_one_can_instantiate(dumped_results)
            exec_info.all_exec_times += 1
            if can_instantiate_:
                exec_info.at_least_one_to_analyze += 1
                can_init_tc_paths.append(tc_path)
            post_process_arrording_to_diff_reason_update_exec_info(exec_paths, tc_dumped_data_dir, exec_info, tc_path, tc_name, difference_reason)
        except (RuntimeError, Exception) as e:
            raise e
            cp_file(tc_path, exec_paths.except_dir)
    return exec_info, can_init_tc_paths

def testing_without_mutation_and_collect_can_init_tc_log_hash(exec_paths, impls, tc_paths_iterator):
    exec_info = testerExecInfo()
    can_init_tc_paths = []
    hash2tc_path = {}
    tc_path2hash = {}
    for tc_name, tc_path in tc_paths_iterator:
        try:
            exec_info.ori_tc_num += 1
            tc_dumped_data_dir = check_dir(exec_paths.dumped_data_base_dir / tc_name)
            dumped_results, difference_reason = test_one_tc_old(tc_dumped_data_dir, impls, tc_path)
            can_instantiate_ = at_least_one_can_instantiate(dumped_results)
            logs = rawRuntimeLogs.from_dumped_results(dumped_results)
            hash_ = hash(logs)
            tc_path2hash[tc_path] = hash_
            hash2tc_path[hash_] = tc_path
            exec_info.all_exec_times += 1
            if can_instantiate_:
                exec_info.at_least_one_to_analyze += 1
                can_init_tc_paths.append(tc_path)
            post_process_arrording_to_diff_reason_update_exec_info(exec_paths, tc_dumped_data_dir, exec_info, tc_path, tc_name, difference_reason)
        except (RuntimeError, Exception) as e:
            raise e
            cp_file(tc_path, exec_paths.except_dir)
    return exec_info, can_init_tc_paths


class noMutationTestingPaths:
    def __init__(self, dumped_data_base_dir, diff_tc_dir, reason_dir, except_dir):
        self.dumped_data_base_dir = dumped_data_base_dir
        self.diff_tc_dir = diff_tc_dir
        self.reason_dir = reason_dir
        self.except_dir = except_dir
    
    @classmethod
    def from_testerExecPaths(cls, tester_exec_paths):
        return cls(tester_exec_paths.dumped_data_base_dir, tester_exec_paths.diff_tc_dir, tester_exec_paths.reason_dir, tester_exec_paths.except_dir)
