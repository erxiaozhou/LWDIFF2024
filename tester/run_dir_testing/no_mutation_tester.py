from pathlib import Path
from extract_dump import at_least_one_can_instantiate
from run_dir_testing.components.exec_engine import ExecEngine
from .tester_util import test_one_tc_old
from .tester_util import post_process_arrording_to_diff_reason_update_exec_info
from .tester import Tester
from file_util import check_dir, cp_file, path_write, save_json
from file_util import get_logger
from .tester_util import testerExecInfo
from .tester_util import testerExecPaths
from tqdm import tqdm
import traceback
from extract_dump.retrieve_coverage import CoverageAll
from util.db_util import get_default_client
from time import time
from .util import get_each_epoch_status_query, update_cases_info
from file_util import get_time_string


class noMutationTester(Tester):
    def __init__(self):
        pass

    def run_testing(self, exec_paths, impls, tc_paths_iterator, testing_time, *args, **kwds):
        # TODO exec_paths，
        assert isinstance(exec_paths, testerExecPaths)
        para_paths = noMutationTestingPaths.from_testerExecPaths(exec_paths)
        time_str = get_time_string()
        base_dir_name = para_paths.base_dir.name
        smith_baseline_name = f'SWNM{base_dir_name}_{time_str}'
        path_write(exec_paths.tester_para_dir / 'start_time.txt', smith_baseline_name)
        collection = get_default_client()['Qlearning'][smith_baseline_name]
        exec_engine = ExecEngine(impls, exec_paths)
        exec_info = testing_without_mutation(para_paths, tc_paths_iterator, testing_time, collection, exec_engine)
        return exec_info
    
    def __repr__(self):
        return self._common_brief_info()


def testing_without_mutation(exec_paths:testerExecPaths, tc_paths_iterator,testing_time, collection, exec_engine:ExecEngine):
    # TODO tc_paths_iterator 
    # testing_without_mutation_and_collect_can_init_tc ， noMutationTester
    # ，
    coverage_summary = CoverageAll()
    case_name_logger = get_logger('case_name_logger', exec_paths.tester_para_dir / 'case_name_logger.log')
    exec_logger = get_logger('exec_logger', exec_paths.tester_para_dir / 'exec_logger.log')
    exec_info = testerExecInfo()
    start_time = time()
    guards_path = exec_paths.tester_para_dir / 'guards.json'
    test_idx = 0
    for tc_name, tc_path in tqdm(tc_paths_iterator):
        try:
            t0 = time()
            # 
            case_exec_info = exec_engine.run_one_case_and_get_info(tc_path, need_coverage=True)
            if case_exec_info.trigger_tester_exception:
                cp_file(tc_path, exec_paths.except_dir)
                continue
            # 
            assert case_exec_info.caseCoverage is not None
            coverage_summary.update_coverage_info(case_exec_info.caseCoverage)
            # 
            t1 = time()
            exec_time = t1 - t0
            case_name_logger.info(f'{tc_name} {exec_time}')
            test_idx += 1
            if test_idx % 1000 == 0:
                collection.insert_one(get_each_epoch_status_query('', coverage_summary.cov_rate, 0, int(time()-start_time)))
            if test_idx % 20000 == 0:
                save_json(guards_path, [str(x) for x in coverage_summary.visited_guards])
            if testing_time is not None and time() - start_time > testing_time:
                break
            # print('time() - start_time > testing_time:', time() - start_time , testing_time)
        except (RuntimeError, Exception) as e:
            print(f'Exception tc_path: {tc_path}')
            exec_logger.debug(f'Exception tc_path: {tc_path}')
            exec_logger.warning(traceback.format_exc())
            # raise e
            cp_file(tc_path, exec_paths.except_dir)
    collection.insert_one(get_each_epoch_status_query('', coverage_summary.cov_rate, 0, int(time()-start_time)))
    # sa
    
    # guards = 
    save_json(guards_path, [str(x) for x in coverage_summary.visited_guards])
    return exec_info


class noMutationTestingPaths:
    def __init__(self, dumped_data_base_dir, diff_tc_dir, reason_dir, except_dir, tester_para_dir):
        self.dumped_data_base_dir = dumped_data_base_dir
        self.diff_tc_dir = diff_tc_dir
        self.reason_dir = reason_dir
        self.except_dir = except_dir
        self.tester_para_dir = tester_para_dir
        self.base_dir = Path(dumped_data_base_dir).parent
        assert self.base_dir == Path(diff_tc_dir).parent == Path(reason_dir).parent == Path(except_dir).parent == Path(tester_para_dir).parent
    
    @classmethod
    def from_testerExecPaths(cls, tester_exec_paths):
        return cls(tester_exec_paths.dumped_data_base_dir, tester_exec_paths.diff_tc_dir, tester_exec_paths.reason_dir, tester_exec_paths.except_dir, tester_exec_paths.tester_para_dir)
