from pathlib import Path
import random
from typing import List, Optional, Tuple
from extract_dump.retrieve_coverage import CoverageAll, oneExecCoverage, trigger_new_guards
from .seed_pool_updater import seedUpdaterCfg
from .seed_pool_updater import seedUpdater

from ..util import caseExecResult
from ..seed_scheduler.seed_select_info_util import SeedSelectInfo, Path2SeedSelectInfoClass
from ..util import get_can_be_seed_check_query, get_popped_seed_query
from .SeedSchedulerBase import SeedSchedulerBase
from file_util import get_time_string
from .util import cal_selected_time_factor, get_init_seeds


class V1SeedSchedulerBase(SeedSchedulerBase):
    def __init__(self, seed_pool, seedPath2SeedSelectInfo: Path2SeedSelectInfoClass, seed_updater_json:Optional[str], logger):
        super().__init__(seed_pool, logger)
        self.seedPath2SeedSelectInfo:Path2SeedSelectInfoClass = seedPath2SeedSelectInfo
        self.proper_max_selected_time = 8
        self.energy_base_N = 4
        assert logger is not None
        self.logger = logger
        
        self.max_factor = 10  # ，seed pool
        self.init_seeds = get_init_seeds(seed_pool)
        if seed_updater_json is None:
            seed_update_cfg = seedUpdaterCfg(new_tcs_cov=True, replace_=True, max_cov=True, new_all_success_tcs_cov=True)
        else:
            seed_update_cfg = seedUpdaterCfg.from_json(seed_updater_json)
        self.seed_updater = seedUpdater(self.seed_pool, seedPath2SeedSelectInfo, seed_update_cfg, logger)

    @classmethod
    def from_seed_dir(cls, seed_dir, seedPath2SeedSelectInfo, seed_updater_json:Optional[str], logger=None):
        seed_pool = [str(p) for p in Path(seed_dir).iterdir()]
        return cls(seed_pool, seedPath2SeedSelectInfo, seed_updater_json, logger)

    def has_seeds(self):
        return len(self.seed_pool) > 0

    def _insert_a_seed(self, seed_path, case_exec_result):
        self.seed_updater.insert_a_seed(seed_path, case_exec_result)

    def _remove_a_seed(self, seed_path):
        self.seed_updater.remove_a_seed(seed_path)

    def update_seed_pool(self, case_exec_info_list: List[caseExecResult], coverage_summary: CoverageAll, all_success_cov_summary:CoverageAll, new_test_cases, seed_path):
        self.seed_updater.update_seed_pool(case_exec_info_list, coverage_summary, all_success_cov_summary, new_test_cases, seed_path)

    def _seed_is_unselected(self, seed_path):
        if seed_path not in self.seedPath2SeedSelectInfo:
            return True
        if self.seedPath2SeedSelectInfo[seed_path].selected_num == 0:
            return True
        return False
    
    def get_unselected_seeds(self):
        seeds = []
        for seed in self.seed_pool:
            if self._seed_is_unselected(seed):
                seeds.append(seed)
        return seeds

    def select_seed_and_energy(self, exec_engine, collection, coverage_summary, all_success=False):
        if all_success:
            assert self.has_all_success_seed()
            seed_path = self.get_a_random_all_success_seed()
            case_exec_result = None
            # self.logger.info(f'get a random all success seed: {Path(seed_path).name}')
        else:   
            seed_path, case_exec_result = self._select_seed_and_exec(
            exec_engine, collection, coverage_summary)
        energy = self._get_energy(seed_path, coverage_summary)
        self.logger.info(
            f'[{get_time_string()}] seed_path: {Path(seed_path).name}; all_success: {all_success}; len(seedPath2SeedSelectInfo): {len(self.seedPath2SeedSelectInfo)}; len(self.seed_pool): {len(self.seed_pool)}')
        self.seedPath2SeedSelectInfo[seed_path].selected_num += 1
        return seed_path, energy, case_exec_result

    def get_a_random_all_success_seed(self):
        all_success_seeds = _get_all_can_success_seeds(self.seedPath2SeedSelectInfo, self.seed_pool)
        assert len(all_success_seeds)
        return random.choice(all_success_seeds)

    def has_all_success_seed(self):
        for _, _info in self.seedPath2SeedSelectInfo.items():
            if _info.all_can_success:
                return True
        return False
    
    def _get_energy(self, seed_path, coverage_summary: CoverageAll):
        # TODO 
        seed_path = str(seed_path)
        assert seed_path in self.seedPath2SeedSelectInfo
        N = self.energy_base_N
        selected_time_factor = cal_selected_time_factor(self.seedPath2SeedSelectInfo, self.proper_max_selected_time, seed_path)
        N *= selected_time_factor
        assert N > 0
        return max(int(N), 1)
       
    def _select_a_seed(self, coverage_summary: CoverageAll):
        raise NotImplementedError

    def _select_seed_and_exec(self, exec_engine, collection, coverage_summary, *args, **kwds):
        while True:
            seed_idx, seed_path = self._select_a_seed(coverage_summary)
            case_exec_result = None
            if seed_path not in self.seedPath2SeedSelectInfo:
                case_exec_result = exec_engine.run_one_case_and_get_info(seed_path, need_coverage=True)
                self.seedPath2SeedSelectInfo.insert_info_from_case_exec_result(seed_path, case_exec_result)
                seed_info = SeedSelectInfo.from_caseExecResult(case_exec_result,  seed_path=seed_path)
                # collection.insert_one(get_can_be_seed_check_query(seed_path, can_be_seed=seed_info.case_can_be_seed, seed_len=len(self.seed_pool)))
            if self._case_can_be_seed(seed_path, coverage_summary):
                break
            # log something
            self.logger.debug(f'A seed in seed pool cannot be a seed: {seed_path}')
            seed_info = self.seedPath2SeedSelectInfo[seed_path]
            collection.insert_one(get_popped_seed_query(seed_path, seed_info.trigger_tester_exception, seed_info.has_timeout, seed_info.is_valid, seed_info.at_least_one_success))
            # remove something
            self._remove_a_seed(seed_path)
            # select another one
        return seed_path, case_exec_result
   
    def _case_can_be_seed(self, seed_path:str, coverage_summary:CoverageAll):
        assert seed_path in self.seedPath2SeedSelectInfo, print(list(self.seedPath2SeedSelectInfo.seed_paths()))
        seed_info = self.seedPath2SeedSelectInfo[seed_path]
        return seed_info.case_can_be_seed
    
    
def _get_all_can_success_seeds(seedPath2SeedSelectInfo, seeds:List[str]):
    considered_seeds = []
    for seed in seeds:
        if seed in seedPath2SeedSelectInfo:
            if seedPath2SeedSelectInfo[seed].all_can_success:
                considered_seeds.append(seed)
    return considered_seeds
