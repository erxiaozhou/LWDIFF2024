from time import time
from typing import Any, Optional
from tqdm import tqdm
from extract_dump import at_least_one_can_instantiate
from file_util import check_dir, cp_file, get_logger
from run_dir_testing.util import get_each_epoch_status_query
from .tester_util import test_one_tc_new, testerExecInfo
from .tester_util import post_process_arrording_to_diff_reason_update_exec_info
from .tester import Tester
from generate_tcs_by_mutation_util import generate_tcs_by_mutate_bytes
from random import random
from pathlib import Path
from config import MONGO_HOST, MONGO_PORT
from pymongo import MongoClient
from extract_dump.retrieve_coverage import CoverageAll


class randomByteMutationTester(Tester):
    def __init__(self, one_tc_limit=50, mutate_num=5, mutate_prob=1) -> None:
        '''
        1.  tcs  tc ( ori_seeds)，  tc  mutate_prob   mutate
        2. mutation ： ori_seeds tc  tc  mutate one_tc_limit (，，，)； tc  mutate_num 
        '''
        self.one_tc_limit = one_tc_limit
        self.mutate_num = mutate_num
        # ! mutate_prob ，
        self.mutate_prob = mutate_prob
        
    
    def run_testing(self, exec_paths, impls, tc_paths_iterator, testing_time, id_name, need_cov=True, *args, **kwds):
        # 
        self.logger = get_logger('randomByteMutationTester',exec_paths.diff_tc_dir.parent / 'randomByteMutationTester.log')
        db = MongoClient(MONGO_HOST, MONGO_PORT)['CP912Cur']
        collection = db[f'CP910_{id_name}']
        # 
        start_time = time()
        if need_cov:
            cov_summary = CoverageAll()
        else:
            cov_summary = None
        exec_info, can_init_tc_paths, cov_summary = testing_without_mutation_and_collect_can_init_tc(exec_paths, impls, tc_paths_iterator, collection, start_time, cov_summary=cov_summary)
        # assert 0
        self.logger.info('Start mutation !!!')
        exec_info.mutation_ori_tc_num = len(can_init_tc_paths)
        need_cov = cov_summary is not None
        for ori_seed in tqdm(can_init_tc_paths):
            if time()- start_time > testing_time:
                break
            self.cur_seed_mutant_num = 0
            self.possible_m = []
            if random() < self.mutate_prob:
                self.mutate_and_update_log(exec_paths, exec_info, ori_seed)
            while self.possible_m:
                try:
                    if time()- start_time > testing_time:
                        break
                    tc_path = self.possible_m.pop()
                    tc_name = Path(tc_path).stem
                    tc_dumped_data_dir = check_dir(exec_paths.dumped_data_base_dir / tc_name)
                    # 
                    exec_result, difference_reason = test_one_tc_new(
                        tc_dumped_data_dir, 
                        impls, tc_path,
                        need_coverage=need_cov,
                        need_validate_info=False
                    )
                    dumped_results = exec_result.dumped_results
                    # 
                    exec_info.all_exec_times += 1
                    # update coverage
                    if need_cov:
                        cov_summary.update_coverage_info(exec_result.coverage_data) # type: ignore
                        if exec_info.all_exec_times % 1000 == 0:
                            _log_cov(collection, cov_summary, start_time)
                    # 
                    
                    # if cov_summary is not None:
                        
                    can_instantiate_ = at_least_one_can_instantiate(dumped_results)
                    if can_instantiate_:
                        exec_info.at_least_one_to_analyze += 1
                    if self._need_mutate(can_instantiate_):
                        self.mutate_and_update_log(exec_paths, exec_info, tc_path)

                    post_process_arrording_to_diff_reason_update_exec_info(exec_paths, tc_dumped_data_dir, exec_info, tc_path, tc_name, difference_reason)
                    assert Path(tc_path).parent == exec_paths.new_tc_dir
                    # remove_file_without_exception(tc_path)
                except (RuntimeError, Exception) as e:
                    # raise e
                    self.logger.warning(f'Exception in run_testing {e}')
                    cp_file(tc_path, exec_paths.except_dir)
        if cov_summary is not None:
            _log_cov(collection, cov_summary, start_time)
        return exec_info
    
    def __repr__(self):
        return self._common_brief_info(**{
            'one_tc_limit': self.one_tc_limit,
            'mutate_num': self.mutate_num,
            'mutate_prob': self.mutate_prob
        })

    def mutate_and_update_log(self, exec_paths, exec_info, tc_path):
        self.cur_seed_mutant_num += self.mutate_num
        self.possible_m.extend(self.generate_tcs(tc_path, exec_paths.new_tc_dir))
        exec_info.mutation_times += self.mutate_num
    
    def generate_tcs(self, ori_tc, new_tc_dir):
        return generate_tcs_by_mutate_bytes(ori_tc, self.mutate_num, new_tc_dir)

    def _need_mutate(self, can_instantiate_):
        if can_instantiate_:
            if self.one_tc_limit > self.cur_seed_mutant_num:
                return True
        return False


def _log_cov(collection, cov_summary:CoverageAll, time0):
    # query = {
    #     'type': 'cov_info',  # v19_tcs_30k_seed_base_cov
    #     'time': int(time()-time0),
    #     'cov_rate': cov_summary.cov_rate
    # }
    query = get_each_epoch_status_query('', cov_summary.cov_rate, 0, int(time()-time0))
    collection.insert_one(query)


def testing_without_mutation_and_collect_can_init_tc(
    exec_paths, 
    impls, 
    tc_paths_iterator,
    collection, start_time,
    cov_summary:Optional[CoverageAll]
    ) -> tuple[testerExecInfo, list[Any], Optional[CoverageAll]]:
    exec_info = testerExecInfo()
    can_init_tc_paths = []
    need_cov = cov_summary is not None
    for tc_name, tc_path in tqdm(tc_paths_iterator):
        try:
            exec_info.ori_tc_num += 1
            tc_dumped_data_dir = check_dir(exec_paths.dumped_data_base_dir / tc_name)
            exec_result, difference_reason = test_one_tc_new(
                tc_dumped_data_dir, 
                impls, tc_path,
                need_coverage=need_cov,
                need_validate_info=False
            )
            can_instantiate_ = at_least_one_can_instantiate(exec_result.dumped_results)
            # update coverage
            if need_cov:
                cov_summary.update_coverage_info(exec_result.coverage_data) # type: ignore
            # 
            exec_info.all_exec_times += 1
            if can_instantiate_:
                exec_info.at_least_one_to_analyze += 1
                can_init_tc_paths.append(tc_path)
            post_process_arrording_to_diff_reason_update_exec_info(exec_paths, tc_dumped_data_dir, exec_info, tc_path, tc_name, difference_reason)
        except (RuntimeError, Exception) as e:
            raise e
            cp_file(tc_path, exec_paths.except_dir)
        if need_cov:
            if exec_info.all_exec_times % 1000 == 0:
                _log_cov(collection, cov_summary, start_time)
    if need_cov:
        _log_cov(collection, cov_summary, start_time)
    return exec_info, can_init_tc_paths,cov_summary 
