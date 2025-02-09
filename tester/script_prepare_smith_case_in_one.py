from pathlib import Path
import sys



def _get_cur_sub_dir_name(cur_batch_id, batch_size, sub_dir_base_name:str, mode):
    if sub_dir_base_name.endswith('/'):
        pass
    else:
        sub_dir_base_name = sub_dir_base_name + '_'
    return f'{mode}_{sub_dir_base_name}{mode}_{batch_size}_b{cur_batch_id}'

def _determine_result_dir(
    pre_seed_base_dir: Path, 
    sub_dir_base_name: str,
    mode: str,
    a_batch_size: int,
    cur_batch_id: int
):
    actual_sub_name = _get_cur_sub_dir_name(cur_batch_id, a_batch_size, sub_dir_base_name, mode)
    return pre_seed_base_dir / actual_sub_name
    


def _identify_start_idx(
    pre_seed_base_dir: Path, 
    sub_dir_base_name: str,
    mode: str,
    a_batch_size: int,
    start_batch_id: int,
    to_gen_dirs:list[Path]
)->int:
    to_check_result_dir = _determine_result_dir(pre_seed_base_dir, sub_dir_base_name, mode, a_batch_size, start_batch_id)
    while to_check_result_dir.exists() or to_check_result_dir in to_gen_dirs:
        start_batch_id += 1
        to_check_result_dir = _determine_result_dir(pre_seed_base_dir, sub_dir_base_name, mode, a_batch_size, start_batch_id)
    return start_batch_id

def determine_cmd_and_result_dir(
    pre_seed_base_dir: Path, 
    sub_dir_base_name: str,
    mode: str,
    a_batch_size: int,
    start_batch_id: int,
    to_gen_dirs:list[Path]
):
    start_batch_id = _identify_start_idx(
        pre_seed_base_dir, 
        sub_dir_base_name, 
        mode, a_batch_size, 
        start_batch_id, 
        to_gen_dirs
    )
    sub_dir_name = _get_cur_sub_dir_name(
        start_batch_id, 
        a_batch_size, 
        sub_dir_base_name, 
        mode
    )
    generated_dir_path = _determine_result_dir(
        pre_seed_base_dir, 
        sub_dir_base_name, 
        mode, 
        a_batch_size, 
        start_batch_id
    )
    new_cmd = determine_cmd(
        mode, 
        a_batch_size, 
        pre_seed_base_dir, 
        sub_dir_name
    )
    
    return new_cmd, generated_dir_path, start_batch_id


def determine_cmd(
    mode:str,
    a_batch_size:int,
    base_dir:Path,
    sub_dir_name:str
)->str:
    return f'python script_prepare_wasm_smith.py {mode} {a_batch_size} "{sub_dir_name}" {base_dir}'



# def 


def gen_raw_ones(mode, sub_dir_base_name, raw_case_num, pre_seed_base_dir, a_batch_size):
    cmds = []
    to_gen_dirs = []
    initialized_start_idx = 0
    to_generated_num = raw_case_num
    # 
    cur_start_idx = initialized_start_idx
    while to_generated_num > 0:
        # determine current batch size
        cur_batch_size = min(a_batch_size, to_generated_num)
        # determine current start idx
        new_cmd, cur_dir, last_start_idx = determine_cmd_and_result_dir(pre_seed_base_dir, sub_dir_base_name, mode, cur_batch_size, cur_start_idx, to_gen_dirs)
        # 
        cur_start_idx = last_start_idx + 1
        to_generated_num -= cur_batch_size
        to_gen_dirs.append(cur_dir)
        cmds.append(new_cmd)
    # 
    final_cmd = '  ;  '.join(cmds) + ';'
    return final_cmd, to_gen_dirs


def _get_actual_rewrite_case_dir(
    pre_seed_base_dir,
    mode_name,
    rewrited_case_sub_dir_id
)->Path:
    return pre_seed_base_dir / f'{mode_name}_{rewrited_case_sub_dir_id}'

def _get_actual_exception_case_dir(
    pre_seed_base_dir,
    mode_name,
    exception_case_sub_dir_id
)->Path:
    return pre_seed_base_dir / f'{mode_name}_{exception_case_sub_dir_id}'


def gen_rewrite_cmds(
    rewrite_result_dir,
    exception_result_dir,
    input_dirs:list[Path],
):
    cmds = []
    for input_dir in input_dirs:
        cur_cmd = f'python script_rewrite_wasm_smith.py {input_dir} {rewrite_result_dir} {exception_result_dir} n'
        cmds.append(cur_cmd)
    return cmds

def main():
    cli_paras = get_cli_paras()
    if cli_paras is None:
        print(get_usage())
        return
    else:
        mode, raw_case_sub_dir_id, raw_case_num, pre_seed_base_dir, rewrited_case_sub_dir_id, exception_case_sub_dir_id = cli_paras

    a_batch_size = 200000
    # 
    final_cmd, to_gen_dirs = gen_raw_ones( 
        mode, 
        raw_case_sub_dir_id, 
        raw_case_num, 
        pre_seed_base_dir, 
        a_batch_size
    )
    # 
    to_gen_dirs_repr = '\n'.join([f'\t{p}' for p in to_gen_dirs])
    
    print('========= Generate Raw Cases =========')
    print(
        f'Execute the command \n\n\t{final_cmd}\n\nIt will generate {raw_case_num} cases in the paths:\n{to_gen_dirs_repr}'
    )
    #
    print('========= Rewrite =========')
    # print('\n')
    rewrite_case_dir = _get_actual_rewrite_case_dir(pre_seed_base_dir, mode, rewrited_case_sub_dir_id)
    exception_case_dir = _get_actual_exception_case_dir(pre_seed_base_dir, mode, exception_case_sub_dir_id)
    rewrite_cmds = gen_rewrite_cmds(rewrite_case_dir, exception_case_dir, to_gen_dirs)
    print('Execute the following commands to rewrite the generated cases:\n\n')
    print('\t', '  ;  '.join(rewrite_cmds))
    print('\n\n The result is stored in the following path:')
    print(f'\t{rewrite_case_dir}')


def get_usage()->str:
    s = '''
Usage: 
# Input: The script requires 6 arguments
python script_gen_prepare_batch_raw_wasm_smith_cmd.py <mode> <raw_case_sub_dir_id> <raw_case_num> <pre_seed_base_dir> <rewrited_case_sub_dir_id> <exception_case_sub_dir_id>
    - <mode>: Each mode corresponds to a specific way to generate the raw cases. They are defined in the `mode_name2func` dictionary in the script `script_prepare_wasm_smith.py`.
    - <raw_case_sub_dir_id>: The identifier of the sub directory to store the raw cases. The raw cases will be stored in the path: `<pre_seed_base_dir>/<mode>_<raw_case_sub_dir_id>`.
    - <raw_case_num>: The number of raw cases to generate.
    - <pre_seed_base_dir>: The base directory to store the generated cases.
    - <rewrited_case_sub_dir_id>: The identifier of the sub directory to store the rewritten cases. The rewritten cases will be stored in the path: `<pre_seed_base_dir>/<mode>_<rewrited_case_sub_dir_id>`.
    - <exception_case_sub_dir_id>: The identifier of the sub directory to store the exception cases. The exception cases will be stored in the path: `<pre_seed_base_dir>/<mode>_<exception_case_sub_dir_id>`.


# Output: The output is the text 
    - contains two python commands for generate the raw cases and rewrite the generated cases. 
    - Describes the paths of the generated cases and the rewritten cases.

# Example usage:
    python script_prepare_smith_case_in_one.py simd_ensure_term_bm raw_batch1 500000 /media/hdd8T1/inv_wasm_smith/pre_seed  rewrite exception
    '''
    return s


def get_cli_paras():
    argv = sys.argv
    if len(argv) == 7:
        
        mode = argv[1]
        
        raw_case_sub_dir_id = argv[2]
        if not raw_case_sub_dir_id.endswith('/'):
            raw_case_sub_dir_id = raw_case_sub_dir_id + '/'
        
        raw_case_num = int(argv[3])
        pre_seed_base_dir = Path(argv[4])
        
        rewrited_case_sub_dir_id = argv[5]
        exception_case_sub_dir_id = argv[6]
        return mode,raw_case_sub_dir_id,raw_case_num,pre_seed_base_dir,rewrited_case_sub_dir_id,exception_case_sub_dir_id
    else:
        return None


if __name__ == '__main__':
    main()
    