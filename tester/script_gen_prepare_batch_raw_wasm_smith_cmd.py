import sys
from pathlib import Path

# python script_prepare_wasm_smith.py a_default_simplest  500000 "a_default_simplest_b1/a_default_simplest_g10"




def _get_cur_sub_dir_name(cur_batch_id, batch_size, sub_dir_base_name:str, mode):
    if sub_dir_base_name.endswith('/'):
        pass
    else:
        sub_dir_base_name = sub_dir_base_name + '_'
    return f'{mode}_{sub_dir_base_name}{mode}_{batch_size}_b{cur_batch_id}'


def _assert_sub_dir_not_exist(pre_seed_base_dir, sub_dir_name):
    assert not (pre_seed_base_dir / sub_dir_name).exists(), f'{sub_dir_name} exists !!!!'


if __name__ == '__main__':
    argv = sys.argv
    assert len(argv) >= 6
    mode = argv[1]
    sub_dir_base_name = argv[2]
    a_batch_size = int(argv[3])
    start_idx = int(argv[4])
    end_idx = int(argv[5])
    if len(argv) >6:
        pre_seed_base_dir = Path(argv[6])
    else:
        pre_seed_base_dir = Path('/media/hdd8T1/inv_wasm_smith/pre_seed')
    # process sub_dir_base_name
    if not sub_dir_base_name.endswith('/'):
        sub_dir_base_name = sub_dir_base_name + '/'
    
    cmds = []
    for i in range(start_idx, end_idx):
        actual_sub_name = _get_cur_sub_dir_name(i, a_batch_size, sub_dir_base_name, mode)
        _assert_sub_dir_not_exist(pre_seed_base_dir, actual_sub_name)
        cur_cmd = f'python script_prepare_wasm_smith.py {mode} {a_batch_size} "{_get_cur_sub_dir_name(i, a_batch_size, sub_dir_base_name, mode)}" {pre_seed_base_dir}'
        cmds.append(cur_cmd)
    output = '  ;  '.join(cmds) + ';'
    print(output)
    
#  a_default_simplest 20000 "default_ensure_bm_term_25b1/default_ensure_bm_term_p1_20000"