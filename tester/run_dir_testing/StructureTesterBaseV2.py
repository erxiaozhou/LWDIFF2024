from pathlib import Path
from random import random
import traceback
from typing import List
from time import time

from .util import get_each_epoch_status_query, update_cov_after_exec_new_cases
from .fuzzer_tmp_common_part import act_mutation_and_get_case_exec_info
from .seed_scheduler.seed_select_info_util import SeedSelectInfo, Path2SeedSelectInfoClass
from .tester_util import testerExecInfo, testerExecPaths
from file_util import check_dir, cp_file
from file_util import get_logger
from file_util import get_time_string
from .StructureTesterBase import StructureTesterBase
from memory_profiler import profile
import io


class StructureTesterBaseV2(StructureTesterBase):
    def __init__(self, runtime_names:List[str], 
                 actions, 
                 tester_name_prefix, 
                 tester_exec_paths,
                 mutation_selector, 
                 seed_scheduler, 
                 seedPath2SeedSelectInfo:Path2SeedSelectInfoClass) -> None:
        super().__init__(runtime_names, actions, tester_name_prefix, tester_exec_paths, mutation_selector, seed_scheduler, seedPath2SeedSelectInfo)

    # @profile(stream=io.open('tt/debug_memoty.txt', 'w+'))
    def run_testing(self, impls, testing_time, *args, **kwds):
        self._init_tester_before_loop(impls)
        self.mutation_effectiveness_logger = get_logger('mutation_effectiveness', self.tester_para_dir/'mutation_effectiveness.log')

        seed_path, energy = self._select_seed_and_exec_ori_seed()
        self.cur_epoch = 0
        while self.seed_scheduler.has_seeds():
            print('self.seed_scheduler.has_seeds', len(self.seed_scheduler.seed_pool))
            self.cur_epoch += 1
            
            try:
                # print('current energy:', energy)
                last_seed_exec_result = self.seedPath2SeedSelectInfo.get_by_path(seed_path)
                last_case_exec_result = last_seed_exec_result
                next_path = seed_path
                current_seed_mutation_num =0
                total_mutation_num_for_the_seed = 0
                total_mutant_idx = 0
                while energy > 0:
                    total_mutation_num_for_the_seed+=1
                    r_ = random()
                    if last_seed_exec_result.all_can_success and r_<0.95:
                        action = 'special_op_mutate'
                        action_index = 0
                    else:
                        action, action_index = self.mutation_selector.choose_action()
                    print(f'Current action: {action}')
                    debug_t1 = time()
                    _debug_ori_case = next_path
                    # self.process_logger.info(f'Init parser log 1: {last_case_exec_result._init_parser_num}')
                    case_exec_info_list, new_test_cases = act_mutation_and_get_case_exec_info(
                        self.mutation_engine, 
                        self.case_batch_size, 
                        self.exec_paths.new_tc_dir, 
                        self.exec_engine, 
                        self.tester_para_dir, 
                        self.collection, 
                        next_path, 
                        action, 
                        time()-self.time0,
                        parser=last_case_exec_result.parser
                        )
                    # self.process_logger.info(f'Init parser log 2: {last_case_exec_result._init_parser_num}')

                    self.mutation_selector.update_inner_info(action_index, 
                                                             case_exec_info_list, 
                                                             last_case_exec_result,
                                                             coverage_summary=self.coverage_summary)

                    self.seed_scheduler.update_seed_pool(
                            case_exec_info_list=case_exec_info_list, 
                            coverage_summary=self.coverage_summary, 
                            all_success_cov_summary=self.all_success_cov, 
                            new_test_cases=new_test_cases, 
                            seed_path=seed_path)
                    # log mutation
                    debug_before_analyze_log = time()
                    log_content = ''
              
                    debug_after_analyze_log = time()
                    # 
                    update_cov_after_exec_new_cases(self.coverage_summary,self.all_success_cov , case_exec_info_list)
                    # determone the nect path
                    if len(new_test_cases) > 0 and len(case_exec_info_list) > 0 and case_exec_info_list[0].case_can_be_seed  and current_seed_mutation_num < self.SEED_MUTANT_MAX:
                        possible_seed_exec_info = case_exec_info_list[0]
                        possible_next_path = new_test_cases[0]
                        next_path = possible_next_path
                        last_case_exec_result = SeedSelectInfo.from_caseExecResult(possible_seed_exec_info, seed_path=next_path)
                        current_seed_mutation_num += 1
                        total_mutant_idx += 1
                    else:
                    # if len(new_test_cases) == 0 or len(case_exec_info_list) == 0:
                        next_path = seed_path
                        last_case_exec_result = last_seed_exec_result
                        energy -= 1  # ! energy seed mutation sequence， mutants
                        current_seed_mutation_num = 0
                        total_mutant_idx += 1
                    debug_end_epoch = time()
                    self.process_logger.info(f'[{get_time_string()}]  {Path(_debug_ori_case).name},  cur_seed_mn: {current_seed_mutation_num}, energy: {energy}, time: {debug_end_epoch-debug_t1}, time of analyze log: {debug_after_analyze_log-debug_before_analyze_log}, {action}')
                    if int(time()-self.time0) > testing_time: break
                self.coverage_summary.update_common_guards()
                self.all_success_cov.update_common_guards()
                self.process_logger.info(f"[{get_time_string()}] {Path(seed_path).name}s' total_mutation_num_for_the_seed: {total_mutation_num_for_the_seed}")
                seed_path, energy = self._select_seed_and_exec_ori_seed()
                total_mutation_num_for_the_seed = 0
                cur_time = int(time()-self.time0)
                if cur_time > testing_time:
                    break
            except Exception as e:
                # raise e
                RETRY_TIMES = 5
                self.process_logger.warning(f'Exception in run_testing {e}')
                self.process_logger.warning(traceback.format_exc())
                for _ in range(RETRY_TIMES):
                    try:
                        if self.may_except_case_path is not None:
                            cp_file(self.may_except_case_path, self.exec_paths.except_dir)
                            self.may_except_case_path = None
                        action, action_index = self.mutation_selector.choose_action()
                        seed_path, energy = self._select_seed_and_exec_ori_seed()
                        break
                    except Exception as e:
                        self.process_logger.warning(f'Exception IN RETRUN {_}:  {e}')
                        self.process_logger.warning(traceback.format_exc())
            # log something --------------------------------------
            self.mutation_selector.dump_inner_info(self.cur_epoch, self.tester_para_dir)

            self.collection.insert_one(get_each_epoch_status_query(action, self.coverage_summary.cov_rate, 0, int(time()-self.time0)))
            # if self.cur_epoch % 2000 == 0:
            #     update_guards_in_collection(self.collection, self.coverage_summary.visited_guards, self.coverage_summary.total_guard_num)
        return testerExecInfo()  # ， ，
