import traceback
from extract_dump import load_results_from_one_dumped_data_dir
from extract_dump import dumpData
from file_util import check_dir, read_json, save_json
from log_content_util import get_reason_key2dumped_data_dirs_from_reason_json
from pathlib import Path
from functools import lru_cache
from tqdm import tqdm
import re
import numpy as np

from util import is_anan, is_cnan, is_illegal_anan, is_nan

from file_util import get_logger

logger = get_logger(__name__, f'tt/{__name__}.log')

def category_stack(reason_json_path, dumped_data_base_dir, result_dir, ignore_all_nan=True):
    reason2tc_result_dirs = get_reason_key2dumped_data_dirs_from_reason_json(
        reason_json_path, dumped_data_base_dir)
    assert isinstance(reason2tc_result_dirs, dict)
    result_dir = check_dir(result_dir)
    reason_log_pair2path = {}
    path2reason_log_pair = {}
    cur_file_idx = 1
    for reason_key in reason2tc_result_dirs:
        if  not reason_key:
            continue
        tc_result_dirs = reason2tc_result_dirs[reason_key]
        stack_key2tc_names = group_tc_names_by_stack_key(tc_result_dirs, ignore_all_nan)
        if len(stack_key2tc_names) == 0:
            continue
        stack_key2tc_names_path = str(result_dir / '{}.json'.format(cur_file_idx))
        save_json(stack_key2tc_names_path, stack_key2tc_names)

        for log_key in tqdm(stack_key2tc_names.keys()):
            cleaned_reason_key = str(reason_key)
            reason_content_pair = (cleaned_reason_key, '===', log_key)
            reason_content_pair = repr(reason_content_pair)
            reason_log_pair2path[reason_content_pair] = stack_key2tc_names_path
            inv_key = '<-->'.join((stack_key2tc_names_path,
                                  cleaned_reason_key))
            if inv_key not in path2reason_log_pair:
                path2reason_log_pair[inv_key] = []
            path2reason_log_pair[inv_key].append(log_key)
        cur_file_idx += 1

    reason_content_pair_log_path = result_dir / '0_reason_content_pair_log.json'
    save_json(reason_content_pair_log_path, reason_log_pair2path)
    reason_content_pair_log_inv_path = result_dir / '0_reason_content_pair_inv_log.json'
    save_json(reason_content_pair_log_inv_path, path2reason_log_pair)
    print('The result of stack clustering is located at', result_dir)


def group_tc_names_by_stack_key(tc_result_dirs, ignore_all_nan, ignore_stack_type=True):
    stack_key2tc_names = {}
    for tc_result_dir in tc_result_dirs:
        
        try:
            dumped_results = load_results_from_one_dumped_data_dir(tc_result_dir)
        except Exception as e:
            logger.debug(f'Error in {tc_result_dir}')
            continue
        stack_vals = cleanedStackVals.from_dumped_results(dumped_results)
        if ignore_all_nan and stack_vals.all_nan:
            continue
        try:
            key = stack_vals.key
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            print('tc_result_dir', tc_result_dir)
            print('stack_vals', stack_vals.stack_val_dict_)
            raise e
        if ignore_stack_type and 'unknown' in key:
            continue
        name = Path(tc_result_dir).name
        stack_key2tc_names.setdefault(key, []).append(name)
    return stack_key2tc_names


def get_diff_stack_idxs(stacks: list['cleanedStackVal']):
    diff_idxs = set()
    assert len(stacks) >= 2
    for stack_idx in range(1, len(stacks)):
        diff_idxs |= get_different_stack_val_idxs(stacks[0], stacks[stack_idx])
    return diff_idxs


class cleanedStackVals:
    def __init__(self, dict_:dict[str, 'cleanedStackVal']) -> None:
        self.stack_val_dict_ = dict_
        for v in dict_.values():
            assert isinstance(v, cleanedStackVal)

    @property
    def key(self):
        sorted_list = []
        val_lists = list(self.stack_val_dict_.values())
        diff_idxs = get_diff_stack_idxs(val_lists)
        considered_keys = get_most_diff_keys(self.stack_val_dict_)
        for k, v in self.stack_val_dict_.items():
            assert isinstance(v, cleanedStackVal)
            if k in considered_keys:
                impl_repr = (k, v.key(diff_idxs))
                sorted_list.append(impl_repr)
        sorted_list = sorted(sorted_list, key=lambda x: x[0])
        key = repr(tuple(sorted_list))
        return key
    
    @property
    def all_nan(self):
        for v in self.stack_val_dict_.values():
            if not v.is_nan:
                return False
        if len(self.stack_val_dict_) == 0:
            return False
        return True

    @classmethod
    def from_dumped_results(cls, dumped_results):
        r = cls(get_stack_val_from_dumped_results(dumped_results))
        return r


def get_stack_val_from_dumped_results(dumped_results):
    stack_val_dict = {}
    for r in dumped_results:
        assert isinstance(r, dumpData)
        if not r.failed_exec:
            stack_val_dict[r.name] = cleanedStackVal.from_dump_data(r)
    return stack_val_dict


class one_val_describer:
    def __init__(self, val_ty, val_bytes, stack_infered_val) -> None:
        ty_is_nan = False
        val_is_inf = False
        val_is_ninf = False
        if val_ty in ['f32', 'f64']:
            ty_is_nan = is_nan(val_bytes)
        if val_ty == 'v128':
            if any([
                is_nan(val_bytes[:8]), 
                is_nan(val_bytes[8:]),
                is_nan(val_bytes[:4]), 
                is_nan(val_bytes[4:8]), 
                is_nan(val_bytes[8:12]), 
                is_nan(val_bytes[12:]), 
                ]):
                ty_is_nan = True
        if stack_infered_val == np.inf:
            val_is_inf = True
        if stack_infered_val == -np.inf:
            val_is_ninf = True
        self.is_nan = ty_is_nan
        self.is_inf = val_is_inf
        self.is_ninf = val_is_ninf
        self.val_ty = val_ty
        self.val_bytes = val_bytes
        self.stack_infered_val = stack_infered_val

    @property
    def key(self):
        s = f'{self.val_ty}'
        if self.is_nan:
            s += '_nan'
        if self.is_inf:
            s += '_inf'
        if self.is_ninf:
            s += '_ninf'
        return s

    def __eq__(self, __value: 'one_val_describer') -> bool:
        return self.val_ty == __value.val_ty and \
            self.val_bytes == __value.val_bytes 

    def __hash__(self) -> int:
        return hash((self.val_ty, bytes(self.val_bytes)))


def get_different_stack_val_idxs(stack_val1: 'cleanedStackVal', stack_val2: 'cleanedStackVal'):
    assert isinstance(stack_val1, cleanedStackVal)
    assert isinstance(stack_val2, cleanedStackVal)
    different_idxs = set()
    max_length = max(stack_val1.stack_num, stack_val2.stack_num)
    if stack_val1.stack_types is None or stack_val2.stack_types is None:
        return set()
        return set(range(max_length))
    if stack_val1.stack_bytes_process_nan is None or stack_val2.stack_bytes_process_nan is None:
        return set()
        return set(range(max_length))
    if stack_val1.stack_infered_vals is None or stack_val2.stack_infered_vals is None:
        return set()
        return set(range(max_length))
    for idx, (stack_ty1, stack_ty2) in enumerate(zip(stack_val1.stack_types, stack_val2.stack_types)):
        if stack_ty1 != stack_ty2:
            different_idxs.add(idx)
    for idx, (stack_bytes1, stack_bytes2) in enumerate(zip(stack_val1.stack_bytes_process_nan, stack_val2.stack_bytes_process_nan)):
        if stack_bytes1 != stack_bytes2:
            different_idxs.add(idx)
    return different_idxs

def get_most_diff_keys(name2stack_val: dict[str, 'cleanedStackVal']):
    runtime_num = len(name2stack_val)
    half_th = runtime_num / 2
    under_th_keys = set()
    stack_num = list(name2stack_val.values())[0].stack_num
    for idx in range(stack_num):
        hash_val2names = {}
        for name, stack_val in name2stack_val.items():
            cur_val = stack_val.val_describors[idx]
            hash_val = hash(cur_val)
            hash_val2names.setdefault(hash_val, []).append(name)
        for hash_val, names in hash_val2names.items():
            if len(names) <= half_th:
                under_th_keys.update(names)
    return under_th_keys

class cleanedStackVal:
    def __init__(self, stack_num=-1, stack_types=None, stack_bytes=None, stack_infered_vals=None, stack_bytes_process_nan=None) -> None:
        self.stack_types = stack_types
        self.stack_bytes = stack_bytes
        self.stack_bytes_process_nan = stack_bytes_process_nan
        self.stack_infered_vals = stack_infered_vals
        self.stack_num = stack_num
        self.nan_ty =None
        self.is_nan = None
        self.val_describors = []
        for i in range(stack_num):
            self.val_describors.append(one_val_describer(
                stack_types[i], 
                stack_bytes_process_nan[i], 
                stack_infered_vals[i]
                )
            )

    

    def key(self, diff_idxs):
        assert self.stack_num != -1, print('Except', self.stack_num, self.stack_types, self.stack_bytes)
        strs = []
        for idx, val in enumerate(self.val_describors):
            if idx not in diff_idxs:
                pass
            else:
                strs.append(val.key)
        key = '-'.join(strs)
        return key

    @classmethod
    def from_dump_data(cls, dump_data_obj):
        assert isinstance(dump_data_obj, dumpData)
        assert not dump_data_obj.failed_exec
        paras = {
            'stack_num': dump_data_obj.stack_num,
            'stack_types': dump_data_obj.stack_types,
            'stack_bytes': dump_data_obj.stack_bytes,
            'stack_infered_vals': dump_data_obj.stack_infered_vals,
            'stack_bytes_process_nan': dump_data_obj.stack_bytes_process_nan
        }
        return cls(**paras)

    @classmethod
    def from_dict(cls, dict_):
        assert isinstance(dict_, dict)
        return cls(**dict_)


