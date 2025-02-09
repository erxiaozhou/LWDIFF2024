from logging import Logger
from pathlib import Path
from random import random
from typing import List
from extract_dump.retrieve_coverage import CoverageAll, trigger_new_guards
from file_util import read_json
from ..util import caseExecResult
from .util import can_replace_ori_seed
from .seed_select_info_util import SeedSelectInfo
from .seed_analysis_util import trigger_new_cov_tc_idxs
from .trim_util import trim_seed
from file_util import get_time_string


class seedUpdaterCfg:
    def __init__(self,
                    new_tcs_cov:bool=True,
                    replace_:bool=False,
                    max_cov:bool=True,
                    new_all_success_tcs_cov:bool=True,
                    new_seed_cov:bool=True,
                    MC:bool=False,
                    trimming:bool=True,
                    new_all_success_seed_cov:bool=True,
                    trimming_period:int = 10000,
                    **kwds
                 ):
        self.new_tcs_cov = new_tcs_cov
        self.replace_ = replace_
        self.max_cov = max_cov
        self.new_all_success_tcs_cov = new_all_success_tcs_cov
        self.new_seed_cov = new_seed_cov
        self.MC = MC
        self.trimming = trimming
        self.new_all_success_seed_cov = new_all_success_seed_cov
        self.trimming_period = trimming_period

    @classmethod
    def from_json(cls, json_path):
        return cls(**read_json(json_path))


class seedUpdater:
    def __init__(self, seed_pool, seedPath2SeedSelectInfo,cfg:seedUpdaterCfg, logger:Logger):
        self.seed_pool = seed_pool
        self.seedPath2SeedSelectInfo = seedPath2SeedSelectInfo
        self.logger = logger
        self.cfg = cfg
        self.can_init_num2max_cov:dict[int, int] = {}
        self.update_seed_times = 0
        self.last_trimmed_times = 0
        self.last_trimmed_seed_pool_size = len(seed_pool)
        # 
        self.all_success_seed_cov = CoverageAll()
        self.seed_cov = CoverageAll()
        self.trimming_period = cfg.trimming_period
        assert isinstance(self.trimming_period, int)

    def insert_a_seed(self, seed_path, case_exec_result:caseExecResult):
        self.seedPath2SeedSelectInfo.insert_info_from_case_exec_result(seed_path, case_exec_result)
        self.seed_pool.append(str(seed_path))
        assert case_exec_result.caseCoverage is not None
        self.seed_cov.update_coverage_info(case_exec_result.caseCoverage)
        if case_exec_result.all_can_success:
            self.all_success_seed_cov.update_coverage_info(case_exec_result.caseCoverage)

    def update_seed_pool(self, case_exec_info_list: List[caseExecResult], coverage_summary: CoverageAll, all_success_cov_summary:CoverageAll, new_test_cases, seed_path):
        self.update_by_new_seed(case_exec_info_list, coverage_summary, all_success_cov_summary, new_test_cases, seed_path)
        if self.cfg.trimming:
            self.trim_seed_pool()

    
    def trim_seed_pool(self):
        self.update_seed_times += 1
        self.last_trimmed_times+= 1
        need_trim = False
        trim_reason = ''
        # if len(self.seed_pool) > 1.5 * self.last_trimmed_seed_pool_size and self.last_trimmed_times > 1000:
        #     need_trim = True
        #     trim_reason = 'seed pool size'
        if self.last_trimmed_times >= self.trimming_period:
            need_trim = True
            trim_reason = 'last trimmed times'
        if need_trim:
            self.last_trimmed_times = 0
            self.logger.info(f'Conduct Trimming [{get_time_string()}];Reason: {trim_reason} ; ori seed pool size: {len(self.seed_pool)}; Current update_seed_times: {self.update_seed_times}; last_trimmed_times: {self.last_trimmed_times}')
            removed_seeds = trim_seed(self.seed_pool, self.seedPath2SeedSelectInfo, self.logger)
            self.logger.info(f' [{get_time_string()}] new seed pool size: {len(self.seed_pool)}')
            # self.last_trimmed_seed_pool_size = len(self.seed_pool)
            self.logger.info(f' [{get_time_string()}] removed seeds: {removed_seeds}')
            self.logger.info(f'Seed Names:{[Path(p).name for p in self.seed_pool]}')
 
    def update_by_new_seed(self, case_exec_info_list: List[caseExecResult], coverage_summary: CoverageAll, all_success_cov_summary:CoverageAll, new_test_cases, seed_path):
        self_can_be_seed_tc_indexs = [i for i in range(len(case_exec_info_list)) if case_exec_info_list[i].case_can_be_seed]
        can_be_seed_tc_num = len(self_can_be_seed_tc_indexs)
        new_seeds = set()
        for _ in range(1):
            if self.cfg.new_tcs_cov:
                new_seeds.update(self._update_seed_pool_by_add(case_exec_info_list, coverage_summary, new_test_cases, 'by_tc'))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
            if self.cfg.replace_:
                new_seeds.update(self._update_seed_pool_by_replace(case_exec_info_list, new_test_cases, seed_path))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
            if self.cfg.max_cov:
                new_seeds.update(self._update_seed_pool_by_max_cov(case_exec_info_list, new_test_cases))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
            if self.cfg.new_all_success_tcs_cov:
                new_seeds.update(self._update_seed_pool_by_all_success_new_cov(case_exec_info_list, all_success_cov_summary, new_test_cases, 'by_tc'))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
            if self.cfg.new_seed_cov:
                new_seeds.update(self._update_seed_pool_by_add(case_exec_info_list, self.seed_cov, new_test_cases, 'by_seed'))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
            if self.cfg.new_all_success_seed_cov:
                new_seeds.update(self._update_seed_pool_by_all_success_new_cov(case_exec_info_list, self.all_success_seed_cov, new_test_cases, 'by_seed'))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
            if self.cfg.MC:
                new_seeds.update(self._update_seed_pool_by_MC(case_exec_info_list, new_test_cases))
                if len(new_seeds) == can_be_seed_tc_num:
                    break
        return new_seeds            

    def _update_seed_pool_by_MC(self, case_exec_info_list: List[caseExecResult], new_test_cases):
        new_seeds = set()
        for case_path, case_exec_info in zip(new_test_cases, case_exec_info_list):
            if case_exec_info.case_can_be_seed:
                if case_path not in self.seed_pool:
                    if random() < 0.003:
                        new_seeds.add(case_path)
                        self.insert_a_seed(case_path, case_exec_info)
                        self.logger.info(f'new seed by MC: {Path(case_path).name}')
        return new_seeds

    def _update_seed_pool_by_max_cov(self, case_exec_info_list: List[caseExecResult], new_test_cases):
        new_seeds = []
        for case_path, case_exec_info in zip(new_test_cases, case_exec_info_list):
            if case_exec_info.case_can_be_seed:
                if case_path  in self.seed_pool:
                    continue
                can_init_num = case_exec_info.can_init_num
                assert case_exec_info.caseCoverage is not None
                guard_num = case_exec_info.caseCoverage.unique_visited_guard_num
                if (can_init_num not in self.can_init_num2max_cov) or (guard_num > self.can_init_num2max_cov[can_init_num]):
                    self.can_init_num2max_cov[can_init_num] = guard_num
                    new_seeds.append(case_path)
                    self.insert_a_seed(case_path, case_exec_info)
                    self.logger.info(f'new seed by max cov: {Path(case_path).name}')
        return new_seeds

    def _update_seed_pool_by_all_success_new_cov(self, case_exec_info_list: List[caseExecResult], all_success_cov_summary:CoverageAll,  new_test_cases, comment=''):
        new_seeds = []
        for case_path, case_exec_info in zip(new_test_cases, case_exec_info_list):
            if case_exec_info.all_can_success:
                if case_path  in self.seed_pool:
                    continue
                assert case_exec_info.caseCoverage is not None
                if trigger_new_guards(case_exec_info.caseCoverage, all_success_cov_summary):
                    new_seeds.append(case_path)
                    self.insert_a_seed(case_path, case_exec_info)
                    self.logger.info(f'new seed by all success new cov {comment}: {Path(case_path).name}; all_success_cov_rate:{all_success_cov_summary.cov_rate}')
        return new_seeds
        
    def _update_seed_pool_by_add(self, case_exec_info_list, coverage_summary, new_test_cases, comment=''):
        self_can_be_seed_tc_indexs = [i for i in range(len(case_exec_info_list)) if case_exec_info_list[i].case_can_be_seed]
        seed_tc_indexs = trigger_new_cov_tc_idxs(
            case_exec_info_list, coverage_summary, self_can_be_seed_tc_indexs)
        to_append_case_exec_info = [case_exec_info_list[i] for i in seed_tc_indexs]
        new_seeds = [str(new_test_cases[i]) for i in seed_tc_indexs]
        for _seed, _case_exec_info in zip(new_seeds, to_append_case_exec_info):
            if _seed in self.seed_pool:
                continue
            self.insert_a_seed(_seed, _case_exec_info)
            self.logger.info(f'new seed by add {comment}: {Path(_seed).name}')
        return new_seeds

    def _update_seed_pool_by_replace(self, case_exec_info_list, new_test_cases, seed_path):
        self_can_be_seed_tc_indexs = [i for i in range(len(case_exec_info_list)) if case_exec_info_list[i].case_can_be_seed]
        # * update seed pool
        new_seed_paths = []
        # 
        can_replace_idxs = []
        if seed_path not in self.seed_pool:
            return []
        
        for idx in self_can_be_seed_tc_indexs:
            if new_test_cases[idx] in self.seedPath2SeedSelectInfo:
                continue
            cur_case_exec_info = case_exec_info_list[idx]
            if seed_path not in self.seed_pool:
                self.logger.debug(f'debug seedPath2SeedSelectInfo seeds: {self.seedPath2SeedSelectInfo.seed_paths()}')
            if can_replace_ori_seed(SeedSelectInfo.from_caseExecResult(cur_case_exec_info), self.seedPath2SeedSelectInfo[seed_path]):
                can_replace_idxs.append(idx)
        if len(can_replace_idxs) == 0:
            return []
        if len(can_replace_idxs) >= 1:
            for idx in can_replace_idxs:
                cur_case_exec_info = case_exec_info_list[idx]
                new_case_path = str(new_test_cases[idx])
                if new_case_path not in self.seed_pool:
                    new_seed_paths.append(new_case_path)
                    self.insert_a_seed(new_case_path, cur_case_exec_info)
                    self.logger.info(f'new seed by replace: {Path(new_case_path).name}')
            if str(seed_path) in self.seed_pool:
                self.remove_a_seed(seed_path)
                self.logger.info(f'poped seed path {Path(seed_path).name} ')
        return new_seed_paths

    def remove_a_seed(self, seed_path):
        self.seed_pool.remove(str(seed_path))
        self.seedPath2SeedSelectInfo.pop(str(seed_path))
      
