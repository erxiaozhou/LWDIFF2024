from pathlib import Path
from typing import Union
from file_util import check_dir, save_json
from smith_util import gen_a_tested_wasm
from smith_util.wasm_smith_util import gen_a_default_wasm, gen_a_non_can_ensure_term_wasm, gen_a_default_ensure_term_wasm
from smith_util.wasm_smith_util import a_default_bm_fmt, a_default_ensure_bm_term_fmt, generate_case_with_cmd_template
from smith_util.wasm_smith_util import a_default_simplest_fmt
from smith_util.wasm_smith_util import a_default_ensure_bm_may_invalid_term_fmt, simd_ensure_term_bm_fmt
import time
import sys
from tqdm import tqdm



mode_name2func = {
    'ensure_term': gen_a_non_can_ensure_term_wasm,
    # 'normal': gen_a_tested_wasm,
    # 'cdefault': gen_a_default_wasm,
    'default_ensure_term': gen_a_default_ensure_term_wasm,
    'default_bm': lambda size, path: generate_case_with_cmd_template(a_default_bm_fmt, size, path),
    'default_ensure_bm_term': lambda size, path: generate_case_with_cmd_template(a_default_ensure_bm_term_fmt, size, path),
    'default_ensure_bm_may_invalid_term': lambda size, path: generate_case_with_cmd_template(a_default_ensure_bm_may_invalid_term_fmt, size, path),
    'simd_ensure_term_bm': lambda size, path: generate_case_with_cmd_template(simd_ensure_term_bm_fmt, size, path),
    'a_default_simplest': lambda size, path: generate_case_with_cmd_template(a_default_simplest_fmt, size, path),
}

def generate_pre_seeds(mode, num, sub_dir_name, pre_seed_base_dir):
    # assert mode == 'non_can'
    from file_util import get_time_string
    def generate_seed_in_a_dir(case_dir, seed_num, prefix, size=20000):
        case_dir = check_dir(case_dir)
        cur_case_num = len(list(case_dir.iterdir()))
        func = mode_name2func[mode]
        seed_num = seed_num - cur_case_num
        assert case_dir.exists()
        for i in tqdm(range(seed_num), 'Generate Wasm-smith Case', total=seed_num):
            p = case_dir / f'{prefix}_{i}_{get_time_string()}.wasm'
            for i in range(5):
                success_run = True
                try:
                    func(size, p)
                except Exception as e:
                    print(e)
                    success_run = False
                if success_run:
                    break
    cur_time = time.time()
    cur_time = int(cur_time)
    prefix = f'{cur_time}_{mode}'
    case_dir = pre_seed_base_dir / sub_dir_name
    generate_seed_in_a_dir(case_dir, num, prefix)
    print(f'case_dir: {case_dir}')
    

# for i in range(1000):
#     pass
if __name__ == '__main__':
    argv = sys.argv
    assert len(argv) >= 4
    mode = argv[1]
    assert mode in ['ensure_term', 'normal', 'cdefault', 'default_ensure_term', 'default_bm', 'a_default_simplest', 'simd_ensure_term_bm', 'default_ensure_bm_term', 'simd_ensure_term_bm', 'default_ensure_bm_may_invalid_term']
    num = int(argv[2])
    sub_dir_name = argv[3].strip()
    if len(argv) > 4:
        pre_seed_base_dir = Path(argv[4])
    else:
        pre_seed_base_dir = check_dir('/media/hdd8T1/inv_wasm_smith/pre_seed')
    generate_pre_seeds(mode, num, sub_dir_name, pre_seed_base_dir)
    # change_random_val_to_modify_length_generate()
    # generate_to_investigat_cnan_smith()
    # generate_to_update_strategy()
    pass
