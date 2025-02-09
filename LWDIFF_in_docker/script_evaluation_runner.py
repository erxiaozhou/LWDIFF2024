import os
import subprocess
import sys
from pathlib import Path
import time

def get_time_string():
    return time.strftime('%m-%d-%H-%M-%S', time.localtime())

acceptable_tester_repr = ['WADIFF', 'WasmSmith', 'RM', 'RS', 'RP', 'Our']

def get_paras():
    usage_str = '''
        'Usage: python script_evaluation_runner.py <tester_repr> time result_id result_base_dir [add_random]
            <tester_repr> : 'WADIFF' / 'WasmSmith' / 'RM' / 'RS' / 'RP' / 'Our'
            time : int
            result_id : str, e.g., 01, 02
            result_base_dir : str, e.g., /media/xxx/baseline
            add_random : 'True' / 'False'  (Only for 'RM', 'RS', 'RP', 'Our')

        Execute the output the conduct the actual testing. The output will store the testing results at <result_base_dir>
    '''
    print(usage_str, '\n==========================================================')
    tester_repr = sys.argv[1]  # 'WADIFF' / 'WasmSmith' / 'RM' / 'RS' / 'RP' / 'Our'
    time = int(sys.argv[2])  # 86400
    result_id = sys.argv[3]  # 'CP910_try'
    result_base_dir = sys.argv[4]  
    if len(sys.argv) < 6:
        add_random = None
    else:
        add_random = sys.argv[5]  # 'True' / 'False'
        assert add_random in ['True', 'False']
        add_random = add_random == 'True'
    return tester_repr, time, result_id, result_base_dir, add_random


def get_cmd():
    tester_repr, time, result_id, result_base_dir, add_random = get_paras()
    cur_time_stem = get_time_string()
    result_id = f'{result_id}_{cur_time_stem}'
    assert tester_repr in acceptable_tester_repr
    time_str = f'{time}s'
    if tester_repr == 'WADIFF':
        final_result_repr = f'{tester_repr}_{result_id}_{time_str}'
        if (Path(result_base_dir) / final_result_repr).exists():
            raise Exception(f'{(Path(result_base_dir) / final_result_repr)} exists')
        seed_dir = '/home/anonymous/CP912/v19_tcs_from_cloud'
        print('The result will be stored at:\n    ', Path(result_base_dir) / final_result_repr)
        cmd = f'python script_byte_mutate_baseline.py {seed_dir} {result_base_dir} {final_result_repr} {time}'
        print('To conduct the testing, please execute the following command:\n    ', cmd)
    elif tester_repr == 'WasmSmith':
        final_result_repr = f'{tester_repr}_{result_id}_{time_str}'
        result_dir = Path(result_base_dir) / final_result_repr
        
        if (Path(result_base_dir) / final_result_repr).exists():
            raise Exception(f'{(Path(result_base_dir) / final_result_repr)} exists')
        # result base dir 
        case_dir = '<The directory storing the Wasm-Smith generated test cases>'  # To be replaced by the user!
        cmd = f'python run_dir_tester_main.py no_mutation_halfdump {case_dir} {result_dir} {time} ; python script_extract_smith_case_name_from_exec_log.py  {result_dir}   mv_tested_cases {case_dir}  /media/hdd8T1/inv_wasm_smith/pre_seed/a_default_simplest_rewrite_tested_cur'
        print('The result will be stored at:', result_dir)
        print('To conduct the testing, please execute the following command:')
        print(cmd)
    # elif tester
    else:
        assert add_random is not None
        pos_candi_config_path = 'tester_configs/PosCandis_v1.json'
        insert_wrap_config_path = 'tester_configs/InsertWraps_v4.json'
        seed_config_path = 'tester_configs/seed_updates/no_replace.json'
        mutator_config_path = 'tester_configs/ori_all_v9_debug.json'
        scheduler_name = 'MABUCB'
        if tester_repr == 'RM':
            mutator_config_path = 'tester_configs/only_byte.json'
        if tester_repr == 'RP':
            pos_candi_config_path = 'tester_configs/PosCandis_Random.json'
            insert_wrap_config_path = 'tester_configs/InsertWraps_None.json'
        if tester_repr == 'RS':
            scheduler_name = 'Random'
        final_result_repr = f'{tester_repr}_{result_id}'
        result_base_dir_with_suffix = Path(result_base_dir) / 'L'
        cmd = f'python script_generate_SOPS_mutation_testing_cmd.py  True False {time_str} ../only_nop  {result_base_dir_with_suffix} halfdump V3  {scheduler_name}  {final_result_repr}  False {mutator_config_path} {pos_candi_config_path} {insert_wrap_config_path}  {seed_config_path}  {add_random}'
        # os.system(cmd)
        # output = os.system(cmd, shell=True)
        full_command = subprocess.check_output(cmd, shell=True).decode('utf-8').strip('\n')
        output_path = full_command.split(' ')[4]
        # output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip('\n').split(' ')[-6]
        print('The result will be stored at:\n    ', output_path)
        print('To conduct the testing, please execute the following command:\n    ', full_command)


if __name__ == '__main__':
    get_cmd()
