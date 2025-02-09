from typing import List
from time import time
from pymongo import MongoClient
from extract_dump.retrieve_coverage import CoverageAll
from .tester_util import testerExecPaths
from .util import init_case_info_in_db
from .seed_scheduler.seed_select_info_util import Path2SeedSelectInfoClass
from .seed_scheduler.SeedSchedulerBase import SeedSchedulerBase
from .tester import Tester
from config import MONGO_HOST, MONGO_PORT
from .components import MutationEngine
from .components import ExecEngine
from .components.mutation_engine import GeneratedMutators
from file_util import check_dir, cp_file, path_write, read_json
from file_util import get_logger
from file_util import path_write
from file_util import get_time_string
from .components.mutation_selector import MutationSelector


class TesterBase(Tester):
    def __init__(self, runtime_names:List[str], 
                 actions, 
                 tester_name_prefix, 
                 tester_exec_paths,
                 mutation_selector, 
                 seed_scheduler, 
                 seedPath2SeedSelectInfo:Path2SeedSelectInfoClass) -> None:
        self.runtime_names = runtime_names
        self.actions = actions
        self.exec_paths:testerExecPaths = tester_exec_paths
        # 
        self.seedPath2SeedSelectInfo = seedPath2SeedSelectInfo
        # 
        self.seed_scheduler:SeedSchedulerBase = seed_scheduler
        self.mutation_selector:MutationSelector = mutation_selector
        # 
        enabled_action2mutators = GeneratedMutators.generate_enabled_action2mutators(self.actions)
        self.mutation_engine = MutationEngine(enabled_action2mutators, self.exec_paths.tester_para_dir)
        # 
        self.case_batch_size = 1
        self.coverage_summary = CoverageAll()
        self.all_success_cov = CoverageAll()
        # * 
        self.may_except_case_path = None
        self.tested_seeds = set()
        #  collection
        self.cur_tester_name = f'{tester_name_prefix}_{get_time_string()}'
        path_write(self.tester_para_dir / 'start_time.txt', self.cur_tester_name)
        db = MongoClient(MONGO_HOST, MONGO_PORT)['Qlearning']
        self.collection = db[self.cur_tester_name]
        # checher the attrs atr the same in the tester and it components
        assert seed_scheduler.seedPath2SeedSelectInfo is self.seedPath2SeedSelectInfo

    @property
    def tester_para_dir(self):
        return self.exec_paths.tester_para_dir

    def _init_tester_before_loop(self, impls):
        self.exec_engine = ExecEngine(impls, self.exec_paths)
        self.process_logger = get_logger('process_logger', f'{self.tester_para_dir}/process_logger.log')
        self.time0 = int(time())
        init_case_info_in_db(self.collection, self.actions)

    def _select_seed_and_exec_ori_seed(self):
        # * select seed and get information related to the seed
        seed_path, energy, case_exec_result = self.seed_scheduler.select_seed_and_energy(
            self.exec_engine, self.collection, self.coverage_summary)
        seed_path = str(seed_path)
        if self.seed_scheduler.is_ori_seed(seed_path):
            if case_exec_result is not None:  #  exec a case
                assert seed_path not in self.tested_seeds
                self.coverage_summary.update_coverage_info(case_exec_result.caseCoverage)
                self.tested_seeds.add(seed_path)
        return seed_path, energy
