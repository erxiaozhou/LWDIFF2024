import traceback
from typing import List
from time import time
from .util import get_each_epoch_status_query, update_cov_after_exec_new_cases
from .fuzzer_tmp_common_part import act_mutation_and_get_case_exec_info
from .seed_scheduler.seed_select_info_util import Path2SeedSelectInfoClass
from .tester_util import testerExecInfo
from file_util import check_dir, cp_file
from file_util import get_time_string
from .TesterBase import TesterBase
class StructureTesterBase(TesterBase):
    def __init__(self, runtime_names:List[str], 
                 actions, 
                 tester_name_prefix, 
                 tester_exec_paths,
                 mutation_selector, 
                 seed_scheduler, 
                 seedPath2SeedSelectInfo:Path2SeedSelectInfoClass) -> None:
        self.SEED_MUTANT_MAX = 5
        super().__init__(runtime_names, actions, tester_name_prefix, tester_exec_paths, mutation_selector, seed_scheduler, seedPath2SeedSelectInfo)
        
    @property
    def tester_para_dir(self):
        return super().tester_para_dir
 
    def _init_tester_before_loop(self, *args, **kwds):
        super()._init_tester_before_loop(*args, **kwds)
    def run_testing(self, impls, testing_time, *args, **kwds):
        self._init_tester_before_loop(impls)

        seed_path, energy = self._select_seed_and_exec_ori_seed()
        self.cur_epoch = 0
        while self.seed_scheduler.has_seeds():
            print('self.seed_scheduler.has_seeds', len(self.seed_scheduler.seed_pool))
            self.cur_epoch += 1
            try:
                print('current energy:', energy)
                last_seed_exec_result = self.seedPath2SeedSelectInfo.get_by_path(seed_path)
                for _cur_idx in range(energy):
                    action, action_index = self.mutation_selector.choose_action()
                    case_exec_info_list, new_test_cases = act_mutation_and_get_case_exec_info(
                        self.mutation_engine, 
                        self.case_batch_size, 
                        self.exec_paths.new_tc_dir, 
                        self.exec_engine, 
                        self.tester_para_dir, 
                        self.collection, 
                        seed_path, action, time()-self.time0, None)

                    self.mutation_selector.update_inner_info(action_index, 
                                                             case_exec_info_list, 
                                                             last_seed_exec_result,
                                                             coverage_summary=self.coverage_summary)
                    self.seed_scheduler.update_seed_pool(
                            case_exec_info_list=case_exec_info_list, 
                            coverage_summary=self.coverage_summary, 
                            new_test_cases=new_test_cases, 
                            seed_path=seed_path)
                    update_cov_after_exec_new_cases(self.coverage_summary,self.all_success_cov , case_exec_info_list)
                    if int(time()-self.time0) > testing_time: break
                seed_path, energy = self._select_seed_and_exec_ori_seed()
                self.coverage_summary.update_common_guards()
                self.process_logger.info(f'{get_time_string()} cur common guards num: {len(self.coverage_summary.common_guards)}')
                if int(time()-self.time0) > testing_time: break
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
                self.process_logger.info(f'exec ori seed: {seed_path}')
        return seed_path, energy
