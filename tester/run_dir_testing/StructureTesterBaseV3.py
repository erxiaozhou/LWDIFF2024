import traceback
from typing import List
from time import time
from extract_dump.retrieve_coverage import CoverageAll

from run_dir_testing.components.CIMABUCBTMutationSelector import CIMABUCBTMutationSelector, MutateSeqInfo
from .util import get_each_epoch_status_query, update_cov_after_exec_new_cases
from .util import init_case_info_in_db
from .fuzzer_tmp_common_part import act_mutation_and_get_case_exec_info
from .seed_scheduler.seed_select_info_util import Path2SeedSelectInfoClass
from .tester_util import testerExecInfo, testerExecPaths
from file_util import check_dir, cp_file, path_write, read_json
from .StructureTesterBase import StructureTesterBase



class StructureTesterBaseV3(StructureTesterBase):
    def __init__(self, runtime_names:List[str], 
                 actions, 
                 tester_name_prefix, 
                 tester_exec_paths,
                 mutation_selector:CIMABUCBTMutationSelector, 
                 seed_scheduler, 
                 seedPath2SeedSelectInfo:Path2SeedSelectInfoClass) -> None:
        super().__init__(runtime_names, actions, tester_name_prefix, tester_exec_paths, mutation_selector, seed_scheduler, seedPath2SeedSelectInfo)
        

    def run_testing(self, impls, testing_time, *args, **kwds):
        assert isinstance(self.mutation_selector, CIMABUCBTMutationSelector)
        self._init_tester_before_loop(impls)

        seed_path, energy = self._select_seed_and_exec_ori_seed()
        self.cur_epoch = 0
        while self.seed_scheduler.has_seeds():
            print('self.seed_scheduler.has_seeds', len(self.seed_scheduler.seed_pool))
            self.cur_epoch += 1
            try:
                last_seed_exec_result = self.seedPath2SeedSelectInfo.get_by_path(seed_path)
                next_path = seed_path
                # for mutation selector
                mutationseq_info = MutateSeqInfo(self.coverage_summary, self.all_success_cov)
                # 
                current_seed_mutation_num = 0
                while energy > 0:
                    action, action_index = self.mutation_selector.choose_action(mutationseq_info.iter_idx)
                    case_exec_info_list, new_test_cases = act_mutation_and_get_case_exec_info(
                        self.mutation_engine, 
                        self.case_batch_size, 
                        self.exec_paths.new_tc_dir, 
                        self.exec_engine, 
                        self.tester_para_dir, 
                        self.collection, 
                        next_path, action, time()-self.time0)

                    self.seed_scheduler.update_seed_pool(
                            case_exec_info_list=case_exec_info_list, 
                            coverage_summary=self.coverage_summary, 
                            all_success_cov_summary=self.all_success_cov, 
                            new_test_cases=new_test_cases, 
                            seed_path=seed_path)
                    update_cov_after_exec_new_cases(self.coverage_summary,self.all_success_cov , case_exec_info_list)
                    # determone the nect path
                    mutationseq_info.update_an_epoch(action_index, case_exec_info_list)
                    # action_idxs.append(action_index)
                    # case_exec_info_list_list.append(case_exec_info_list)
                    if len(new_test_cases) > 0 and len(case_exec_info_list) > 0 and case_exec_info_list[0].case_can_be_seed  and current_seed_mutation_num < self.SEED_MUTANT_MAX:
                        next_path = new_test_cases[0]
                        current_seed_mutation_num += 1
                    else:
                        self.mutation_selector.update_inner_info(mutationseq_info, last_seed_exec_result)
                        next_path = seed_path
                        mutationseq_info = MutateSeqInfo(self.coverage_summary, self.all_success_cov)
                        
                        energy -= 1  # ! energy seed mutation sequence， mutants
                        current_seed_mutation_num = 9
                    if int(time()-self.time0) > testing_time: break
                # 
                self.mutation_selector.update_inner_info(mutationseq_info, last_seed_exec_result)
                # 
                seed_path, energy = self._select_seed_and_exec_ori_seed()
                self.coverage_summary.update_common_guards()
                self.all_success_cov.update_common_guards()
                cur_time = int(time()-self.time0)
                if cur_time > testing_time:
                    break
            except Exception as e:
                # raise e
                RETRY_TIMES = 5
                # self.process_logger.warning(f'Exception in run_testing {e}')
                self.process_logger.warning(traceback.format_exc())
                for _ in range(RETRY_TIMES):
                    try:
                        if self.may_except_case_path is not None:
                            cp_file(self.may_except_case_path, self.exec_paths.except_dir)
                            self.may_except_case_path = None
                        action, action_index = self.mutation_selector.choose_action(0)
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
