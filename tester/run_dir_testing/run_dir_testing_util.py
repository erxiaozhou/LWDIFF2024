from pathlib import Path
from .mutation_testing import test_with_mutation
from file_util import check_dir, read_json, rm_dir
from log_content_util import log_content_categorize_by_one_reason_path
from tqdm import tqdm
from analyze_reslut_util import reasonSummary
from stack_val_analyze import category_stack
from .testing_paras_util import mutationParas
from .tester_util import testerExecPaths
from util import analyzeResultDirs
from extract_dump.data_comparer import diffResult


# import cProfile
def test_and_analyze(result_base_dir, paras, impls):
    test_with_mutation(paras)
    exec_paths = paras.tester_exec_paths
    # detect_canrun_cannotdump(exec_paths, result_base_dir, impls)
    # analyze(result_base_dir, exec_paths)

def analyze(result_base_dir, exec_paths):
    analyze_paths = analyzeResultDirs(result_base_dir)
    reason_summary = reasonSummary(analyze_paths.reason_summary_base_dir, exec_paths.reason_dir)
    log_content_categorize(reason_summary.only_exec_smry_path, analyze_paths.log_category_base_dir, exec_paths.dumped_data_base_dir, ['all', 'only_interesting'])
    category_stack(reason_summary.stack_smry_path, exec_paths.dumped_data_base_dir, analyze_paths.stack_category_base_dir)


def detect_canrun_cannotdump(exec_paths, result_base_dir, impls):
    assert isinstance(exec_paths, testerExecPaths)
    canrun_cannotdump_tc_names = []
    # init canrun_cannotdump_tc_names
    for reason_file in tqdm(exec_paths.reason_dir.iterdir(), desc='detect_canrun_cannotdump'):
        assert reason_file.suffix == '.json'
        diff_reason = diffResult.from_json(reason_file)
        if diff_reason.canrun_cannot_dump:
            tc_name = reason_file.stem
            canrun_cannotdump_tc_names.append(tc_name)
    # copy the tcs in canrun_cannotdump_tc_names to a tmp dir
    diff_tcs_base_dir = exec_paths.diff_tc_dir
    diff_tcs_base_dir = Path(diff_tcs_base_dir)
    new_dir = check_dir(diff_tcs_base_dir.parent / 'tmp_tcs')
    for tc_name in canrun_cannotdump_tc_names:
        assert not tc_name.endswith('.wasm')
        tc_path = diff_tcs_base_dir / f'{tc_name}.wasm'
        new_dir_tc_path = new_dir / f'{tc_name}.wasm'
        tc_path.rename(new_dir_tc_path)
    # remove existing results in each result dir
    for tc_name in canrun_cannotdump_tc_names:
        tc_dumped_data_dir = Path(exec_paths.dumped_data_base_dir) / tc_name
        if tc_dumped_data_dir.exists():
            rm_dir(tc_dumped_data_dir)
        tc_reason_path = Path(exec_paths.reason_dir) / f'{tc_name}.json'
        if tc_reason_path.exists():
            tc_reason_path.unlink()
    paras = mutationParas.get_no_mutation_paras(result_base_dir, new_dir, impls=impls,  tester_exec_paths=exec_paths)
    test_with_mutation(paras)


def log_content_categorize(reason_summary_path, log_category_base_dir, dumped_data_base_dir, modes):
    log_category_base_dir = check_dir(log_category_base_dir)
    for mode in modes:
        sub_log_category_dir = log_category_base_dir / f'{mode}_log_category'
        log_content_categorize_by_one_reason_path(reason_summary_path, dumped_data_base_dir, sub_log_category_dir, mode)
        print('a log_category_dir:', sub_log_category_dir)
