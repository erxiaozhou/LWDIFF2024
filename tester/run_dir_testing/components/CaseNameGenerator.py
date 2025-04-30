from functools import lru_cache
from time import time
from pathlib import Path
import re


_inner_count = 0
mutator_seq_p = re.compile(r'[A-Z]*$')

def get_new_case_path(ori_case_path, new_case_dir, app_case_name=''):
    ori_case_stem = _remove_tail_nums(Path(ori_case_path).stem)
    stem, mutation_seq = get_stem_and_mutation_seq(ori_case_stem)
    global _inner_count
    if _inner_count > 1000:
        _inner_count = 0
    else:
        _inner_count += 1
    inner_value = _inner_count
    time_str = str(time()).replace('.', '')
    new_path = Path(new_case_dir) / \
        f'{stem}{mutation_seq}{app_case_name}_{inner_value}_{time_str}.wasm'
    return new_path

def get_stem_and_mutation_seq(ori_stem:str):
    r = mutator_seq_p.findall(ori_stem)
    r = r[0]
    stem_len = len(ori_stem) - len(r)
    stem = ori_stem[:stem_len]
    if len(r) > 100:
        r = r.lstrip('R')
        mutation_seq = 'R' + r[-100:]
    else:
        mutation_seq = r 
    return stem, mutation_seq

@lru_cache(maxsize=1024)
def _remove_tail_nums(stem):
    return_stem = stem
    while True:
        splited_stem = stem.split('_')
        if len(splited_stem) < 3:
            break
        if not splited_stem[-1].isdigit():
            break
        if not splited_stem[-2].isdigit():
            break
        return_stem = '_'.join(splited_stem[:-2])
        break
    return return_stem