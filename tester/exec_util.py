from typing import List, Optional
from concurrent import futures
from pathlib import Path
from extract_dump import dumpData
from util import cmnImplResultPathGroup
from debug_util import validate_wasm
from extract_dump.retrieve_coverage import exec_to_dump_coverage
from extract_dump.retrieve_coverage import get_coverage_from_default_path
from time import time


class execRawResult:
    def __init__(self, dumped_results: List[dumpData], is_valid: Optional[bool] = None, coverage_data=None) -> None:
        self.dumped_results = dumped_results
        self._is_valid = is_valid
        self.coverage_data = coverage_data

    @property
    def is_valid(self):
        if self._is_valid is None:
            raise ValueError('is_valid is not set')
        return self._is_valid


def exec_one_tc(impls, tc_path, tc_tgt_dump_dir, func_name='to_test'):
    dumped_results = []
    for impl in impls:
        result:dumpData = _exec_one_runtime(impl,  tc_path, func_name)
        dumped_results.append(result)
        dumped_path = _get_default_dumped_path(tc_tgt_dump_dir, result.name)
        result.dump(dumped_path)
    return dumped_results


def exec_one_tc_mth(impls, tc_path, tc_tgt_dump_dir, need_validate_info=False, get_coverage=False, func_name='to_test') -> execRawResult:

    dumped_results = []
    to_do = []
    with futures.ThreadPoolExecutor(max_workers=len(impls)+2) as executor:

        if get_coverage:
            finish_collect_coverage = executor.submit(
                exec_to_dump_coverage, tc_path, func_name)
        if need_validate_info:
            is_valid_future = executor.submit(validate_wasm, tc_path)


        for impl in impls:
            future = executor.submit(_exec_one_runtime, impl,
                                     tc_path, func_name)
            to_do.append(future)


        t1 = time()

        for future in to_do:

            result:dumpData = future.result()
            dumped_results.append(result)

            dumped_path = _get_default_dumped_path(
                tc_tgt_dump_dir, result.name)
            result.dump(dumped_path)



        if get_coverage:
            finish_collect_coverage.result()
            coverage_data = get_coverage_from_default_path()
        else:
            coverage_data = None
        if need_validate_info:
            is_valid = is_valid_future.result() if need_validate_info else None
        else:
            is_valid = None

    raw_result = execRawResult(
        dumped_results, is_valid, coverage_data=coverage_data)
    return raw_result


def _exec_one_runtime(impl, tc_path, func_name='to_test'):

    result = impl.execute_and_collect(tc_path=tc_path, func_name=func_name)
    return result


def _get_default_dumped_path(save_data_dir, impl_name):
    return Path(save_data_dir) / f'{impl_name}=dumped.pkl'
