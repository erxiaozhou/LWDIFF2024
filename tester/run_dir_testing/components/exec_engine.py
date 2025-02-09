from pathlib import Path
from ..util import caseExecResult
from .exec_engine_util import TestedCasesPaths
from ..tester_util import testerExecPaths
from ..tester_util import test_one_tc_new
from ..tester_util import post_process
from file_util import check_dir, cp_file
from .CaseNameGenerator import get_new_case_path


_tested_case_paths = TestedCasesPaths()

class ExecEngine:
    def __init__(self, impls: list, exec_paths: testerExecPaths):
        self.impls = impls
        self.exec_paths = exec_paths

    def run_one_case_and_get_info(self, tc_path, func_name='to_test', need_coverage=False, re_exec_check=True) -> caseExecResult:
        # print(f'func_name: {func_name}')
        # ! * check whether the path existes, just for debug
        if re_exec_check:
            if tc_path in _tested_case_paths:
                raise Exception(f'Case has been executed! {tc_path}; len(_tested_case_paths): {len(_tested_case_paths)}')
            _tested_case_paths.add(tc_path)
        #
        tc_name = Path(tc_path).stem
        tc_dumped_data_dir = check_dir(self.exec_paths.dumped_data_base_dir / tc_name)
        try:
            exec_raw_result, difference_reason = test_one_tc_new(
                tc_dumped_data_dir, self.impls, tc_path, need_validate_info=True, need_coverage=need_coverage, func_name=func_name)
            is_valid = exec_raw_result.is_valid
            post_process(
                self.exec_paths, tc_dumped_data_dir, tc_path, tc_name, difference_reason)
            result = caseExecResult(False, difference_reason=difference_reason, dumped_results=exec_raw_result.dumped_results, is_valid=is_valid, caseCoverage=exec_raw_result.coverage_data)
            
        except (RuntimeError, Exception) as e:
            print('Case case exception!', tc_path)
            raise e
            # ! TODO 
            self.may_except_case_path = Path(tc_path)
            cp_file(tc_path, self.exec_paths.except_dir)
            exec_raw_result, _ = test_one_tc_new(tc_dumped_data_dir, self.impls, "not_exist path", need_validate_info=True, need_coverage=need_coverage, func_name=func_name)
            result = caseExecResult(True)
        return result
    def get_cov(self, tc_path, func_name='to_test'):
        pass