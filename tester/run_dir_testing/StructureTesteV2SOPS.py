from pathlib import Path
from random import choice, random
import traceback
from typing import List, Optional
from time import time
from extract_block_mutator.SpecialInstInputUtil.InsertWrap import InsertWraps
from extract_block_mutator.inst_pose_selector import PosCandis


from .EAScheduler import EASolution, EvaPeformance, PhaseSchedulerBase, determine_the_best_performance_idx, PhaseSchedulerBase
from .util import get_each_epoch_status_query, update_cov_after_exec_new_cases
from .fuzzer_tmp_common_part import act_mutation_and_get_case_exec_info
from .seed_scheduler.seed_select_info_util import SeedSelectInfo, Path2SeedSelectInfoClass
from .tester_util import testerExecInfo, testerExecPaths
from file_util import check_dir, cp_file, path_write, read_json, save_json
from file_util import get_logger
from .StructureTesterBase import StructureTesterBase

class PhaseExecStat:
    def __init__(self, case_num, time) -> None:
        self.case_num = case_num
        self.time = time

def repr_PhaseExecStat_list(phase_exec_stat_list:List[PhaseExecStat]):
    case_nums = [x.case_num for x in phase_exec_stat_list]
    times = [x.time for x in phase_exec_stat_list]
    return f'case_nums: {case_nums}; times: {times}'


class StructureTesteV2SOPS(StructureTesterBase):
    def __init__(self, runtime_names:List[str], 
                    actions, 
                    tester_name_prefix, 
                    tester_exec_paths,
                    seed_scheduler, 
                    seedPath2SeedSelectInfo:Path2SeedSelectInfoClass,
                    mutation_scheduler:PhaseSchedulerBase,
                    pos_candi_json_path,
                    insert_wrap_json_path 
                 ) -> None:
        super().__init__(runtime_names, actions, tester_name_prefix, tester_exec_paths, None, seed_scheduler, seedPath2SeedSelectInfo)
        self.phase = None
        self.action2action_idx = {action:idx for idx, action in enumerate(actions)}
        self.phase_names = actions.copy()
        self.mutation_scheduler = mutation_scheduler

        pos_candis = PosCandis.from_json(pos_candi_json_path)
        insert_wraps = InsertWraps.from_json(insert_wrap_json_path)
        self.mutation_engine.reset_sop_mutator_by_poss_wraps(None, pos_candis, insert_wraps)  
    
    def run_testing(self, impls, testing_time, *args, **kwds):
        self._init_tester_before_loop(impls)
        self.ea_logger = get_logger('ea_logger', self.tester_para_dir/'ea_logger.log')

        self.cur_epoch = 0
        while self.seed_scheduler.has_seeds():
            self.cur_epoch += 1
            if len(self.actions) == 1:
                phase_name = self.actions[0]
                self.exec_one_phase_(testing_time, phase_name, phase_time)
            else:
                if self.cur_epoch <= 1:
                    phase_name = 'random'
                    phase_time = 30
                    self.exec_one_phase_(testing_time, phase_name, phase_time)
                    continue
                if  self.cur_epoch <= 1:
                    for phase_name in self.mutation_scheduler.phase_names:
                        self.exec_one_phase_(testing_time, phase_name, 30)
                else:
                    # ori_solution_idx = 0
                    soluiton, extra_info = self.mutation_scheduler.get_a_solution()
                    self.ea_logger.info(f'Solution Epoch: {self.cur_epoch}; soluiton: {soluiton}')
                    
                    performance = self.exec_a_solution(testing_time, soluiton)
                    self.mutation_scheduler.update_by_performance(performance, self.ea_logger)
                    if extra_info is None:
                        extra_info = {}
                    self.ea_logger.info(f'===> Solution performance: {performance.as_data()}; extra_info: {extra_info}')
                    self.ea_logger.info(f'Solution: {self.mutation_scheduler._soluitons}')
            
            cur_time = int(time()-self.time0)
            if cur_time > testing_time:
                cov_json_path = self.tester_para_dir / 'cov.json'
                all_success_path = self.tester_para_dir / 'all_success_cov.json'
                save_json(cov_json_path, list(self.coverage_summary.visited_guards))
                save_json(all_success_path, list(self.all_success_cov.visited_guards))
                break
        return testerExecInfo() 

    def get_performance_obj_by_cur_stat(self):
        total_guards_num = self.coverage_summary.total_guard_num
        # assert total_guards_num is not None
        if total_guards_num is None:
            total_guards_num = -1
        performance = EvaPeformance(self.coverage_summary.visited_guards,
                                    self.all_success_cov.visited_guards,
                                    total_guards_num=total_guards_num)
        return performance

    def exec_a_solution(self, testing_time, soluiton)->EvaPeformance:
        performance = self.get_performance_obj_by_cur_stat()
        for phase_name, phase_time in soluiton.as_iter():
            phase_performance = self.exec_one_phase_(testing_time, phase_name, phase_time)
            performance.update_by_other_performance(phase_performance)
            self.ea_logger.info(f'Phase Epoch: {phase_name}; time:{phase_time} performance: {phase_performance.as_data()};')
        return performance

    def exec_one_phase_(self, testing_time, phase_name, phase_time):
        performance = self.get_performance_obj_by_cur_stat()
        print('self.seed_scheduler.has_seeds', len(self.seed_scheduler.seed_pool))
        one_case_test_time = 5
        # seed_num = phase_time // one_case_test_time
        time_slotes = [one_case_test_time] * (int(phase_time) // one_case_test_time) + [phase_time - one_case_test_time * (phase_time // one_case_test_time)]
        time_slotes = [x for x in time_slotes if x > 0.05]
        time_slotes = [x if x > 0.5 else 0.5 for x in time_slotes]
        phase_exec_stats = []
        for one_case_test_time in time_slotes:
            try:
                pass
                phase_exec_stat = self.exec_one_phase_core(testing_time, phase_name, one_case_test_time, performance)
                phase_exec_stats.append(phase_exec_stat)
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
                        break
                    except Exception as e:
                        self.process_logger.warning(f'Exception IN RETRUN {_}:  {e}')
                        self.process_logger.warning(traceback.format_exc())
                # log something --------------------------------------

            self.collection.insert_one(get_each_epoch_status_query(phase_name, self.coverage_summary.cov_rate, 0, int(time()-self.time0)))
        self.process_logger.info(f'Phase: {phase_name}; time: {phase_time}; {repr_PhaseExecStat_list(phase_exec_stats)}')
        return performance

    # def 

    def exec_one_phase_core(self, testing_time, phase_name, one_case_test_time, performance:Optional[EvaPeformance]=None) -> PhaseExecStat:
        if phase_name in ['special_op_mutate', 'special_op_mutate_debug']:
            seed_path, energy = self._select_seed_and_exec_ori_seed(all_sucess=True)
                    # energy = 100
            return self.sop_phase(one_case_test_time, 1, seed_path, testing_time, performance)
        elif phase_name == 'random':
            seed_path, energy = self._select_seed_and_exec_ori_seed()
            return self.rdm_phase_phase(one_case_test_time, 3, seed_path, testing_time, performance)
        else:
            seed_path, energy = self._select_seed_and_exec_ori_seed()
            return self.single_diverse_phase(one_case_test_time, phase_name, 2, seed_path, testing_time,performance) # ， ，



    def sop_phase(self, energy_time:float, max_seq_time:int, seed_path:str, testing_time, performance:Optional[EvaPeformance]=None)->PhaseExecStat: 
        t0 = time()
        testing_start_time = time()
        last_seed_exec_info = self.seedPath2SeedSelectInfo.get_by_path(seed_path)
        last_case_exec_info = last_seed_exec_info
        next_path: str = seed_path
        action = 'special_op_mutate'
        # 
        if action not in self.actions and 'special_op_mutate_debug' in self.actions:
            action = 'special_op_mutate_debug'
            
        # 
        assert last_seed_exec_info.all_can_success
        cur_seq_times = 0
        phase_test_num = 0
        while True:
            if time() - testing_start_time > energy_time:
                break
            last_case_exec_info.parser.func0_block
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
                parser=last_case_exec_info.parser
                )
            
            
            self.seed_scheduler.update_seed_pool(
                    case_exec_info_list=case_exec_info_list, 
                    coverage_summary=self.coverage_summary, 
                    all_success_cov_summary=self.all_success_cov, 
                    new_test_cases=new_test_cases, 
                    seed_path=seed_path)
            update_cov_after_exec_new_cases(self.coverage_summary,self.all_success_cov , case_exec_info_list)
            # performance
            if performance is not None:
                for c_result in case_exec_info_list:
                    performance.update_coverage(c_result, c_result.all_can_success)
            if len(new_test_cases) > 0 and \
                len(case_exec_info_list) > 0 and \
                case_exec_info_list[0].difference_reason.no_diff and \
                case_exec_info_list[0].case_can_be_seed  and \
                case_exec_info_list[0].all_can_success and cur_seq_times < max_seq_time :
                    
                next_path = new_test_cases[0]
                last_case_exec_info = SeedSelectInfo.from_caseExecResult(case_exec_info_list[0], seed_path=next_path)
                cur_seq_times += 1
            else:
                next_path = seed_path
                last_case_exec_info = last_seed_exec_info
                cur_seq_times = 0
            
            cur_time = int(time()-self.time0)
            if cur_time > testing_time:
                break
            phase_test_num += 1
        t1 = time()
        # self.process_logger.info(f'In SOP phase; Teste times: {phase_test_num}; time consuming: {t1-t0}')
        return PhaseExecStat(phase_test_num, t1-t0)

    def single_diverse_phase(self, energy_time, action, max_seq_time:int, seed_path:str, testing_time, performance:Optional[EvaPeformance]=None)->PhaseExecStat:
        t0 = time()
        last_seed_exec_info = self.seedPath2SeedSelectInfo.get_by_path(seed_path)
        last_case_exec_info = last_seed_exec_info
        next_path: str = seed_path
        cur_seq_times = 0
        phase_test_num = 0
        while True:
            if time() - t0 > energy_time:
                break
            if 'deep_block_mutate' in action:
                last_case_exec_info.parser.func0_block
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
                parser=last_case_exec_info.parser
                )
            
            self.seed_scheduler.update_seed_pool(
                    case_exec_info_list=case_exec_info_list, 
                    coverage_summary=self.coverage_summary, 
                    all_success_cov_summary=self.all_success_cov, 
                    new_test_cases=new_test_cases, 
                    seed_path=seed_path)
            update_cov_after_exec_new_cases(self.coverage_summary,self.all_success_cov , case_exec_info_list)
            if performance is not None:
                for c_result in case_exec_info_list:
                    performance.update_coverage(c_result, c_result.all_can_success)
            if len(new_test_cases) > 0 and \
                len(case_exec_info_list) > 0 and \
                case_exec_info_list[0].case_can_be_seed and cur_seq_times < max_seq_time :
                    
                next_path = new_test_cases[0]
                last_case_exec_info = SeedSelectInfo.from_caseExecResult(case_exec_info_list[0], seed_path=next_path)
                cur_seq_times += 1
            else:
                next_path = seed_path
                last_case_exec_info = last_seed_exec_info
                cur_seq_times = 0
            
            cur_time = int(time()-self.time0)
            if cur_time > testing_time:
                break
            phase_test_num += 1
        t1 = time()
        # self.process_logger.info(f'In {action}; Teste times: {phase_test_num}; time consuming: {t1-t0}')
        return PhaseExecStat(phase_test_num, t1-t0)


    def rdm_phase_phase(self, energy_time:float, max_seq_time:int, seed_path:str, testing_time, performance:Optional[EvaPeformance]=None)->PhaseExecStat: 
        t0 = time()
        testing_start_time = time()
        last_seed_exec_info = self.seedPath2SeedSelectInfo.get_by_path(seed_path)
        last_case_exec_info = last_seed_exec_info
        next_path: str = seed_path
        action = choice([x for x in self.actions if 'special_op_mutate' not in x])
            
        # 
        # assert last_seed_exec_info.all_can_success
        cur_seq_times = 0
        phase_test_num = 0
        while True:
            if time() - testing_start_time > energy_time:
                break
            # last_case_exec_info.parser.func0_block
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
                parser=last_case_exec_info.parser
                )
            
            
            self.seed_scheduler.update_seed_pool(
                    case_exec_info_list=case_exec_info_list, 
                    coverage_summary=self.coverage_summary, 
                    all_success_cov_summary=self.all_success_cov, 
                    new_test_cases=new_test_cases, 
                    seed_path=seed_path)
            update_cov_after_exec_new_cases(self.coverage_summary,self.all_success_cov , case_exec_info_list)
            # performance
            if performance is not None:
                for c_result in case_exec_info_list:
                    performance.update_coverage(c_result, c_result.all_can_success)
            if len(new_test_cases) > 0 and \
                len(case_exec_info_list) > 0 and \
                case_exec_info_list[0].case_can_be_seed  and \
                cur_seq_times < max_seq_time :
                    
                next_path = new_test_cases[0]
                last_case_exec_info = SeedSelectInfo.from_caseExecResult(case_exec_info_list[0], seed_path=next_path)
                cur_seq_times += 1
                action_candis = self.actions.copy()
                if (not case_exec_info_list[0].difference_reason.no_diff) or \
                    (not case_exec_info_list[0].all_can_success):
                        if 'special_op_mutate' in action_candis:
                            action_candis.remove('special_op_mutate')
                        if 'special_op_mutate_debug' in action_candis:
                            action_candis.remove('special_op_mutate_debug')
            else:
                next_path = seed_path
                last_case_exec_info = last_seed_exec_info
                cur_seq_times = 0
                action_candis = self.actions.copy()
            action = choice(action_candis)
            cur_time = int(time()-self.time0)
            if cur_time > testing_time:
                break
            phase_test_num += 1
        t1 = time()
        # self.process_logger.info(f'In Random phase; Teste times: {phase_test_num}; time consuming: {t1-t0}')
        return PhaseExecStat(phase_test_num, t1-t0)


    def _select_seed_and_exec_ori_seed(self, all_sucess=False):
        # * select seed and get information related to the seed
        seed_path, energy, case_exec_result = self.seed_scheduler.select_seed_and_energy(
            self.exec_engine, self.collection, self.coverage_summary, all_sucess)
            
        seed_path = str(seed_path)
        if self.seed_scheduler.is_ori_seed(seed_path):
            if case_exec_result is not None:  #  exec a case
                assert seed_path not in self.tested_seeds
                self.coverage_summary.update_coverage_info(case_exec_result.caseCoverage)
                self.tested_seeds.add(seed_path)
                # self.process_logger.info(f'exec ori seed: {seed_path}')
        return seed_path, energy
    