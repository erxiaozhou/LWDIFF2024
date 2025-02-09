import sys
from extract_block_mutator.WasmParser import WasmParser
from file_util import read_json, check_dir
from pathlib import Path
from extract_block_mutator.insert_post_process_nan_func import insert_post_process_nan_func_by_easy_sound_strategy
from tqdm import tqdm
from debug_util.debug_util import wasm2wat, validate_wasm
from extract_block_mutator.parser_to_file_util import parser2wasm


def post_process_one(p, target_path):
    parser = WasmParser.from_wasm_path(p)
    assert parser is not None
    parser.insert_post_process_nan_func_by_easy_sound_strategy()
    # target_path = check_dir(target_path)
    parser2wasm(parser, target_path)


def get_tc_paths(base_dir):
    base_dir = Path(base_dir)
    diff_tcs_dir = base_dir / 'diff_tcs'
    stack_category_base_dir = base_dir / 'stack_category_base'
    # name_p =
    stems = []
    for diff_log_p in stack_category_base_dir.iterdir():
        if not diff_log_p.stem.isdigit():
            continue
        d = read_json(diff_log_p)
        for sub_stems in d.values():
            stems.extend(sub_stems)
    paths = []
    for stem in stems:
        fname = f'{stem}.wasm'
        p = diff_tcs_dir / fname
        paths.append(p)
    return paths


def get_new_path(p, new_dir):
    return new_dir / p.name


if __name__ == '__main__':
    assert len(sys.argv) == 2
    result_base_dir = sys.argv[1]
    new_dir = Path(result_base_dir) / 'to_rerun_stack_diff_cases'
    new_dir = check_dir(new_dir)
    for p in tqdm(get_tc_paths(result_base_dir)):
        new_path = get_new_path(p, new_dir)
        # if new_path.exists():
        #     continue
        post_process_one(p, new_path)
        if validate_wasm(p):
            assert validate_wasm(new_path), print(p, new_path)
    
    
