import random
import time
from pathlib import Path

from extract_block_mutator.fuzzer.Fuzzer import Fuzzer

from .byte_seq_nomask_mutator import mutate_without_mask
from .byte_seq_mask_mutator import mutate_with_mask
from .generate_wasm_tc_util import read_next_leb_num, write_wasm_from_dict
from .get_mask_util import get_byte_mask_range
import leb128
from util.prepare_template import prepare_template

        


class Func0ByteFuzzer(Fuzzer):
    def __init__(self, check_defined_cals) -> None:
        self.check_defined_cals = check_defined_cals
        super().__init__()
    
    def fuzz_one(self, ori_wasm, tgt_wasm_path, *args, **kwads):
        generate_tcs_by_mutate_bytes_one(ori_wasm, tgt_wasm_path, self.check_defined_cals)


def generate_tcs_by_mutate_bytes_one(ori_tc_path, new_path, check_defined_cals=True):
    sec_template = prepare_template(ori_tc_path)
    code_sec_bytes = sec_template['code']
    code_sec_info = _code_secion.from_code_sec_ba(code_sec_bytes)
    # code_part = code_sec_info.after_func1_length
    # masks = get_byte_mask_range(code_part, check_defined_cals)
    # sec_template['code'] = _generate_new_code_sec(code_sec_bytes, masks)
    sec_template['code'] = _generate_new_code_sec_without_mask(code_sec_bytes)
    write_wasm_from_dict(new_path, sec_template)


def _generate_new_code_sec(code_sec_bytes, masks):
    code_sec_info = _code_secion.from_code_sec_ba(code_sec_bytes)
    func1_body = _get_new_func1_body(code_sec_info.func1_body, masks)
    code_sec_info.func1_body = func1_body
    code_sec_info.func1_len = code_sec_info.get_random_func1_len
    bas = code_sec_info.get_bytes()
    return bas


def _generate_new_code_sec_without_mask(code_sec_bytes):
    code_sec_info = _code_secion.from_code_sec_ba(code_sec_bytes)
    func1_body = mutate_without_mask(bytearray(code_sec_info.func1_body))
    code_sec_info.func1_body = func1_body
    code_sec_info.func1_len = code_sec_info.get_random_func1_len
    bas = code_sec_info.get_bytes()
    return bas

class _code_secion():
    def __init__(self, before_func, func1_len, func1_body, content_after_func1):
        self.before_func = before_func
        self.func1_len = func1_len
        self.func1_body = func1_body
        self.content_after_func1 = content_after_func1
    
    @classmethod
    def from_code_sec_ba(cls, ori_code_sec):
        ori_code_sec = bytearray(ori_code_sec)
        func_num, offset = read_next_leb_num(ori_code_sec, offset=0)
        before_func = ori_code_sec[:offset]
        func1_len, offset = read_next_leb_num(ori_code_sec, offset=offset)
        func1_body = ori_code_sec[offset:func1_len + offset]
        content_after_func1 = ori_code_sec[func1_len + offset:]
        info = cls(before_func, func1_len, func1_body, content_after_func1)
        return info

    def get_bytes(self):
        base = bytearray()
        base.extend(self.before_func)
        base.extend(leb128.u.encode(self.func1_len))
        base.extend(self.func1_body)
        base.extend(self.content_after_func1)
        return base
    
    @property
    def after_func1_length(self):
        return self.func1_body + self.content_after_func1

    @property
    def get_random_func1_len(self):
        return _get_random_length(len(self.func1_body))


def _get_random_length(func1_length):
    return random.choices([-1, 0, 1], [0.01, 0.98, 0.01], k=1)[0] + func1_length
# =============================================================================


def generate_tcs_by_mutate_bytes(ori_tc_path, mutate_num, new_tc_dir):
    new_tc_dir = Path(new_tc_dir)
    sec_template = prepare_template(ori_tc_path)

    code_sec_bytes = sec_template['code']
    code_sec_info = _code_secion.from_code_sec_ba(code_sec_bytes)
    code_part = code_sec_info.after_func1_length
    masks = get_byte_mask_range(code_part)
    paths = _tc_name_generator(ori_tc_path, mutate_num, new_tc_dir)
    assert len(paths) == mutate_num
    for new_path in paths:
        sec_template['code'] = _generate_new_code_sec(code_sec_bytes, masks)
        write_wasm_from_dict(new_path, sec_template)
    return paths


def _get_new_func1_body(func1_body, masks):
    func1_body = bytearray(func1_body)
    func1_body = mutate_with_mask(func1_body, masks)
    return func1_body


def _tc_name_generator(ori_tc_path, num, new_tc_dir):
    new_tc_dir = Path(new_tc_dir)
    ori_name = Path(ori_tc_path).name
    assert ori_name.endswith('.wasm')
    stem = ori_name[:-5]
    if stem.count('_') < 2:
        ori_stem = stem
        start_idx = 0
    else:
        follow_underline = stem.split('_')[-2]
        before_underline = '_'.join(stem.split('_')[:-2])
        assert isinstance(follow_underline, str)
        if follow_underline.isdigit():
            start_idx = int(follow_underline) + 1
            ori_stem = before_underline
        else:
            ori_stem = stem
            start_idx = 0
    paths = []
    for i in range(num):
        idx = start_idx + i
        time_str = str(time.time()).replace('.', '')
        new_name = '{}_{}_{}.wasm'.format(ori_stem, idx, time_str)
        path = str(new_tc_dir/new_name)
        paths.append(path)
    return paths
