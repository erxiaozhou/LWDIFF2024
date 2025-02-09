from file_util import save_json
from run_dir_testing.random_byte_mutation_tester import randomByteMutationTester
from run_dir_testing.tester_util import testerExecInfo, testerExecPaths
from run_dir_testing.testing_paras_util import _get_tcs_name_and_path
from get_impls_util import get_lastest_halfdump_impls
from pathlib import Path
import sys

assert len(sys.argv) == 5

se_case_dir = Path(sys.argv[1])
result_base_dir = Path(sys.argv[2])
id_name = sys.argv[3]
testing_time = int(sys.argv[4])

actual_result_base_dir = result_base_dir / id_name

tester = randomByteMutationTester(one_tc_limit=79, mutate_num=15)  

exec_paths = testerExecPaths.from_result_base_dir(actual_result_base_dir)
impls = get_lastest_halfdump_impls()

tc_paths_iterator = _get_tcs_name_and_path(se_case_dir)
exec_info: testerExecInfo = tester.run_testing(
    exec_paths, 
    impls, 
    tc_paths_iterator, 
    testing_time,
    id_name
)
exec_info_dict = exec_info.to_dict
save_json(actual_result_base_dir / 'exec_info.json', exec_info_dict)
