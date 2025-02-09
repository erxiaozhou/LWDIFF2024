import os
import sys
from pathlib import Path
import time

def get_time_string():
    return time.strftime('%m-%d-%H-%M-%S', time.localtime())

acceptable_tester_repr = ['WADIFF', 'WasmSmith', 'RM', 'RS', 'RP', 'Our']


def get_usage_str():
    usage_str = '''
        'Usage: python script_evaluation_runner.py <tester_repr> <test_time> <result_id> <result_base_dir> [<additional_parameter>] 
            <tester_repr> : 'WADIFF' / 'WasmSmith' / 'RM' / 'RS' / 'RP' / 'Our'
            <test_time> : int
            <result_id> : str, e.g., 01, 02
            <result_base_dir> : str, e.g., /media/hdd8T1/baseline
            <additional_parameter> (it represents different meanings for different tester) :
                - For WasmSmith:
                    input_dir : str, e,g., /media/hdd8T1/WasmSmithCases
                - For WADIFF:
                    input_dir : str, e,g., /home/anonymous/CP912/v19_tcs_from_cloud
                - For RM / RS / RP / Our:
                    add_random : 'True' / 'False'
                    seed_dir : str, e.g., ./only_nop

                add_random (for 'RM' / 'RS' / 'RP' / 'Our') : 'True' / 'False'.
                input_dir (for 'WADIFF') : str, e,g., /home/anonymous/CP912/v19_tcs_from_cloud
                input_dir (for 'WasmSmith') : str, e,g., /media/hdd8T1/WasmSmithCases
                
    '''
    return usage_str

def get_paras():
    print(get_usage_str(), '\n==========================================================')
    try:
        tester_repr = sys.argv[1]  # 'WADIFF' / 'WasmSmith' / 'RM' / 'RS' / 'RP' / 'Our'
        raw_time_repr = sys.argv[2]  # '86400'
        if raw_time_repr.endswith('s'):
            raw_time_repr = raw_time_repr[:-1]
        testing_time = int(raw_time_repr)  # 86400
        result_id = sys.argv[3]  # 'CP910_try'
        result_base_dir = sys.argv[4]  # '/media/hdd8T1/baseline'
        if tester_repr == 'WADIFF':
            additional_para = Path(sys.argv[5])
        elif tester_repr == 'WasmSmith':
            additional_para = Path(sys.argv[5])
        else:
            add_random = sys.argv[5]  # 'True' / 'False'
            assert add_random in ['True', 'False']
            add_random = add_random == 'True'
            seed_dir = Path(sys.argv[6])  # e.g., './only_nop'
            seed_dir = Path(seed_dir)
            additional_para = (add_random, seed_dir)
        return tester_repr, testing_time, result_id, result_base_dir, additional_para
    except Exception as e:
        print(e)
        print(get_usage_str())
        sys.exit(1)


def get_cmd():
    tester_repr, time, result_id, result_base_dir, additional_para = get_paras()
    cur_time_stem = get_time_string()
    result_id = f'{result_id}_{cur_time_stem}'
    assert tester_repr in acceptable_tester_repr
    time_str = f'{time}s'
    if tester_repr == 'WADIFF':
        final_result_repr = f'{tester_repr}_{result_id}_{time_str}'
        if (Path(result_base_dir) / final_result_repr).exists():
            raise Exception(f'{(Path(result_base_dir) / final_result_repr)} exists')

        input_dir = additional_para
        assert isinstance(input_dir, Path)
        cmd = f'python script_byte_mutate_baseline.py {input_dir} {result_base_dir} {final_result_repr} {time}'
        print(cmd)
    elif tester_repr == 'WasmSmith':

        final_result_repr = f'{tester_repr}_{result_id}_{time_str}'
        result_dir = Path(result_base_dir) / final_result_repr
        
        if (Path(result_base_dir) / final_result_repr).exists():
            raise Exception(f'{(Path(result_base_dir) / final_result_repr)} exists')

        case_dir = additional_para
        assert isinstance(case_dir, Path)
        cmd = f'python run_dir_tester_main.py no_mutation_halfdump {case_dir} {result_dir} {time} ; python script_extract_smith_case_name_from_exec_log.py  {result_dir}   mv_tested_cases {case_dir}  /media/hdd8T1/inv_wasm_smith/pre_seed/a_default_simplest_rewrite_tested_cur'
        print(cmd)

    else:
        assert additional_para is not None and isinstance(additional_para, tuple)
        assert len(additional_para) == 2
        add_random, seed_dir = additional_para
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
        cmd = f'python script_generate_SOPS_mutation_testing_cmd.py  True False {time_str} {seed_dir}  {result_base_dir_with_suffix} halfdump V3  {scheduler_name}  {final_result_repr}  False {mutator_config_path} {pos_candi_config_path} {insert_wrap_config_path}  {seed_config_path}  {add_random}'
        os.system(cmd)


if __name__ == '__main__':
    get_cmd()
