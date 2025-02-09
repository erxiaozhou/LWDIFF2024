import sys
from analyze_reslut_util import reasonSummary
from run_dir_testing.tester_util import testerExecPaths
from util import analyzeResultDirs
from run_dir_testing.run_dir_testing_util import log_content_categorize
from stack_val_analyze import category_stack


def analyze_in_base_dir(result_base_dir):
    exec_paths = testerExecPaths.from_result_base_dir(result_base_dir, False)
    analyze_paths = analyzeResultDirs(result_base_dir)
    reason_summary = reasonSummary(analyze_paths.reason_summary_base_dir, exec_paths.reason_dir)

    log_content_categorize(reason_summary.only_exec_smry_path, analyze_paths.log_category_base_dir, exec_paths.dumped_data_base_dir, ['all', 'only_interesting'])
    category_stack(reason_summary.stack_smry_path, exec_paths.dumped_data_base_dir, analyze_paths.stack_category_base_dir)

def analyze_in_base_dir_only_interesting(result_base_dir):
    exec_paths = testerExecPaths.from_result_base_dir(result_base_dir, False)
    analyze_paths = analyzeResultDirs(result_base_dir)
    reason_summary = reasonSummary(analyze_paths.reason_summary_base_dir, exec_paths.reason_dir)

    log_content_categorize(reason_summary.only_exec_smry_path, analyze_paths.log_category_base_dir, exec_paths.dumped_data_base_dir, ['only_interesting'])




def analyze_in_base_dir_only_value_stack(result_base_dir):
    exec_paths = testerExecPaths.from_result_base_dir(result_base_dir, False)
    analyze_paths = analyzeResultDirs(result_base_dir)
    reason_summary = reasonSummary(analyze_paths.reason_summary_base_dir, exec_paths.reason_dir, exec=False)

    category_stack(reason_summary.stack_smry_path, exec_paths.dumped_data_base_dir, analyze_paths.stack_category_base_dir)

if __name__ == '__main__':
    assert len(sys.argv) in [2, 3]
    result_base_dir = sys.argv[1]
    if len(sys.argv) == 2:
        analyze_in_base_dir(result_base_dir)
    else:
        
        analyze_in_base_dir_only_interesting(result_base_dir)

