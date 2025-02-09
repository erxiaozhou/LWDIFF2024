import cProfile
from pathlib import Path
import re
from get_impls_util.get_impls_util import get_always_new_uninst_impls, get_lastest_uninst_impls
from run_dir_testing.run_dir_testing_util import test_and_analyze
from run_dir_testing.testing_paras_util import mutationParas
from get_impls_util import get_lastest_halfdump_impls
import sys
from util.db_util import get_default_client

from debug_util.debug_util import validate_wasm
from file_util import check_dir
from file_util import read_json
from tqdm import tqdm
from get_impls_util.get_impls_util import get_lastest_halfdump_impls
from run_dir_testing.run_dir_testing_util import test_and_analyze
from run_dir_testing.testing_paras_util import mutationParas
from memory_profiler import profile
from script_post_process_nan_in_stack_diff_ccases import post_process_one
from file_util import get_time_string
from run_dir_testing.tester_factory import seed_scheduler_names
from run_dir_testing.tester_factory import all_mutation_selector_names
from run_dir_testing.tester_factory import name2strcuture

def get_argv_log_query(argv_repr, time_str):
    return {
        'argv_repr': argv_repr,
        'time_str': time_str,
    }




def no_mutation_testing(tested_dir, result_base_dir):
    impls = get_lastest_halfdump_impls()
    paras = mutationParas.get_no_mutation_paras(result_base_dir, tested_dir, impls=impls)
    test_and_analyze(result_base_dir, paras, impls=impls)

def no_mutation_testing_uninst(tested_dir, result_base_dir):
    impls = get_lastest_uninst_impls()
    paras = mutationParas.get_no_mutation_paras(result_base_dir, tested_dir, impls=impls)
    test_and_analyze(result_base_dir, paras, impls=impls)





def post_process_nan_in_and_rerun_and_analyze(base_dir):
    def get_paths(base_dir):
        stack_reason_summary_path = base_dir / 'reason_summarys' / 'stack_summary.json'
        stems = []
        for key, _stems in read_json(stack_reason_summary_path).items():
            if 'variable_diff=None' in key:
                continue
            stems.extend(_stems)
        diff_tcs_dir = base_dir / 'diff_tcs'
        paths = []
        for stem in stems:
            fname = f'{stem}.wasm'
            p = diff_tcs_dir / fname
            paths.append(p)
        return paths
    base_dir = Path(base_dir)
    paths = get_paths(base_dir)
    new_case_dir = check_dir(Path(base_dir) / 'to_rerun_stack_diff_cases')
    for p in tqdm(paths):
        new_path = new_case_dir / p.name
        post_process_one(p, new_path)
        if validate_wasm(p):
            assert validate_wasm(new_path), print(p, new_path)
    impls = get_lastest_halfdump_impls()
    result_base_dir = new_case_dir.parent / (new_case_dir.name + '_result')
    tested_dir = new_case_dir
    paras = mutationParas.get_no_mutation_paras(
        result_base_dir, tested_dir, impls=impls)
    test_and_analyze(result_base_dir, paras, impls=impls)




def get_paras_from_cli():
    no_mutation_task_names = [
        
        'no_mutation_halfdump',
        'no_mutation_uninst',
        'no_mutation_uninst_always_new'
    ]
    support_task_names = [
        'post_process_nan_in_and_rerun_and_analyze',

        'mutation_testing'
    ]
    support_task_names = no_mutation_task_names + support_task_names
    tasks_name_string = ', '.join(support_task_names)
    usage_info = f'''
    Usage: python run_dir_tester_main.py <task_name> <tested_dir> <result_base_dir> <action_config_file_path(optional) tester_name_prefix>
        task_name: {tasks_name_string}
        tested_dir: An existing dir
        result_base_dir: An unexisting dir
        
    '''
    argv = sys.argv
    argv_repr = ' '.join(argv)
    collection = _get_argv_log_collection()
    collection.insert_one(get_argv_log_query(argv_repr, get_time_string()))

    task_name = argv[1]
    if task_name == 'post_process_nan_in_and_rerun_and_analyze':
        assert len(argv) == 3, usage_info
        tester_base_dir = argv[2]
        post_process_nan_in_and_rerun_and_analyze(tester_base_dir)
    elif task_name in no_mutation_task_names:
        assert len(argv) in  [4, 5], usage_info
        tested_dir = argv[2]
        result_base_dir = argv[3]
        if len(argv) == 5:
            seconds = int(argv[4])
        else:
            seconds = None
        if task_name == 'no_mutation_halfdump':
            impls = get_lastest_halfdump_impls()
        elif task_name == 'no_mutation_uninst':
            impls = get_lastest_uninst_impls()
        elif task_name == 'no_mutation_uninst_always_new':
            impls = get_always_new_uninst_impls()
        paras = mutationParas.get_no_mutation_paras(result_base_dir, tested_dir, impls=impls, testing_time=seconds)
        test_and_analyze(result_base_dir, paras, impls=impls)
    elif task_name == 'mutation_testing_SOSP':
        assert len(argv) == 14, usage_info + f'len(argv): {len(argv)}\n'

        tested_dir = argv[2]
        result_base_dir = argv[3]
        config_file_path = argv[4]
        seed_scheduler_name = argv[5]
        assert seed_scheduler_name in seed_scheduler_names
        phase_scheduler_name = argv[6]

        impl_mode = argv[7]
        tester_name_prefix = argv[8]
        assert impl_mode in ['halfdump', 'uninst']
        if impl_mode == 'halfdump':
            impls = get_lastest_halfdump_impls()
        else:
            impls = get_lastest_uninst_impls()
        time_str = argv[9]

        assert re.match(r'\d+s$', time_str)
        testing_time = int(time_str[:-1])
        runtime_names = [im.name for im in impls]
        pos_candis_json = argv[10]
        wraps_json = argv[11]
        seed_updater_json = argv[12]
        assert argv[13] in ['True', 'False']
        add_random_phase = argv[13] == 'True'
        paras = mutationParas.get_testing_SOSP_paras(
            tested_dir, 
            result_base_dir, 
            runtime_names=runtime_names, 
            impls=impls, 
            config_file_path=config_file_path,
            seed_scheduler_name=seed_scheduler_name,
            phase_scheduler_name=phase_scheduler_name, 
            tester_name_prefix=tester_name_prefix,
            testing_time = testing_time,
            pos_candis_json=pos_candis_json,
            wraps_json=wraps_json,
            seed_updater_json=seed_updater_json,
            add_random_phase=add_random_phase
            )

        test_and_analyze(result_base_dir, paras, impls)
    else:
        assert task_name == 'mutation_testing'
        assert len(argv) == 11, usage_info

        tested_dir = argv[2]
        result_base_dir = argv[3]
        config_file_path = argv[4]
        seed_scheduler_name = argv[5]
        assert seed_scheduler_name in seed_scheduler_names
        mutation_selector_name = argv[6]
        assert mutation_selector_name in all_mutation_selector_names
        impl_mode = argv[7]
        tester_name_prefix = argv[8]
        assert impl_mode in ['halfdump', 'uninst']
        if impl_mode == 'halfdump':
            impls = get_lastest_halfdump_impls()
        else:
            impls = get_lastest_uninst_impls()
        structure_name = argv[9]
        assert structure_name in name2strcuture
        time_str = argv[10]

        assert re.match(r'\d+s$', time_str)
        testing_time = int(time_str[:-1])
            
        
        runtime_names = [im.name for im in impls]
        paras = mutationParas.get_testing_paras(
            tested_dir, 
            result_base_dir, 
            runtime_names=runtime_names, 
            impls=impls, 
            config_file_path=config_file_path,
            seed_scheduler_name=seed_scheduler_name,
            mutation_selector_name=mutation_selector_name, 
            tester_name_prefix=tester_name_prefix,
            structure_name=structure_name,
            testing_time = testing_time
            )
        test_and_analyze(result_base_dir, paras, impls)
        
def _get_argv_log_collection():
    return get_default_client()['Qlearning']['script_command_log']

if __name__ == '__main__':
    get_paras_from_cli()

