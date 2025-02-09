from typing import List, Optional

from extract_block_mutator.WasmParser import WasmParser
from .util import caseExecResult
from .util import save_cannot_init_cases
from .util import update_cases_info


def act_mutation_and_get_case_exec_info(mutation_engine, case_batch_size, new_tc_dir, exec_engine, custom_log_dir, collection, seed_path, action, cut_time, parser:Optional[WasmParser]=None):

    # TODO ，，
    # * necessary for all testers
    case_exec_info_list: List[caseExecResult] = []
    non_tester_exception_case_paths = []
    new_cases = mutation_engine.act_mutation(
        seed_path, action, case_batch_size, new_tc_dir, parser)
    for tc_path in new_cases:
        case_exec_info = exec_engine.run_one_case_and_get_info(tc_path, need_coverage=True)
        if case_exec_info.trigger_tester_exception:
            continue
        non_tester_exception_case_paths.append(tc_path)
        case_exec_info_list.append(case_exec_info)
    # just for log ; not necessary
    # collect some cases for debugigng
    save_cannot_init_cases(custom_log_dir, seed_path, action,
                           case_exec_info_list, non_tester_exception_case_paths)
    #
    update_cases_info(collection, action,
                      non_tester_exception_case_paths, case_exec_info_list, cut_time)

    if len(case_exec_info_list) == 0:
        raise Exception(f'len(case_exec_info_list) == 0, action: {action}; seed_path: {seed_path} new_cases:{new_cases}')
    return case_exec_info_list, non_tester_exception_case_paths
