from util.encoding_util import read_next_leb_num
import re
from typing import List, Sequence
import leb128
from WasmInfoCfg import val_type_strs_list


byte_val2type_str = {
    0x7F: 'i32',
    0x7E: 'i64',
    0x7D: 'f32',
    0x7C: 'f64',
    0x7B: 'v128',
    0x70: 'funcref',
    0x6F: 'externref'
}
type_str2byte_val = {
    'i32': 0x7F,
    'i64': 0x7E,
    'f32': 0x7D,
    'f64': 0x7C,
    'v128': 0x7B,
    'funcref': 0x70,
    'externref':0x6F
}


class FuncTypeCatException(Exception):
    pass


func_type_pattern = re.compile(r'^(?:\(param\s*([^\)]*?)\))?\s*(?:\(result\s*([^\)]*?)\))?$')


def check_result_can_support_para_wc_len(cur_ops:Sequence[str], req_ops:Sequence[str]) -> bool:
    # ! ，
    to_consider_len = min(len(cur_ops), len(req_ops))
    for i in range(to_consider_len):
        cur_op = cur_ops[-i-1]
        req_op = req_ops[-i-1]
        if cur_op != req_op and req_op != 'any':
            return False
    return True


def check_result_can_support_param(cur_ops:List[str], req_ops:List[str]) -> bool:
    # cur ops : the operands on the stack
    # req ops : the operands required by the instruction / something else
    can_support = True
    if len(cur_ops) < len(req_ops):
        can_support = False
    else:
        to_compare_num = len(req_ops)
        for i in range(to_compare_num):
            to_comare_idx = - i - 1
            cur_op = cur_ops[to_comare_idx]
            req_op = req_ops[to_comare_idx]
        # while len(cur_ops) and len(req_ops):
            # cur_op = cur_ops.pop()
            # req_op = req_ops.pop()
            if cur_op != req_op and req_op != 'any':
                can_support = False
                break
    return can_support

class funcType:
    def __init__(self, param_types, result_types, determined_return_ty:bool=False) -> None:
        # assert
        if not isinstance(param_types, list):
            param_types = list(param_types)
        if not isinstance(result_types, list):
            result_types = list(result_types)

        for ty in param_types:
            if ty not in val_type_strs_list:
                raise Exception(f'{ty} not in {val_type_strs_list}')
            # assert ty in val_type_strs_list, f'{ty} not in {val_type_strs_list}'
        for ty in result_types:
            if ty not in val_type_strs_list:
                raise Exception(f'{ty} not in {val_type_strs_list}')
        self._param_types = param_types
        self._result_types = result_types

        self.determined_return_ty = determined_return_ty
    @classmethod
    def from_strs(cls, param_types, result_types):
        # param_types
        return cls(param_types, result_types)

    @property
    def param_types(self):
        return self._param_types
    @property
    def result_types(self):
        return self._result_types

    @param_types.setter
    def param_types(self, value):
        raise Exception('param_types is read only')

    @result_types.setter
    def result_types(self, value):
        raise Exception('param_types is read only')
    
    def __add__(self, __value):
        return _add_core1(self, __value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.param_types}, {self.result_types})'

    def __eq__(self, __value: object) -> bool:
        if self is __value:
            return True
        assert isinstance(__value, funcType)
        return self.param_types == __value.param_types and self.result_types == __value.result_types and self.determined_return_ty == __value.determined_return_ty

    def __hash__(self) -> int:
        return hash((tuple(self.param_types), tuple(self.result_types), self.determined_return_ty))

    def copy(self):
        return funcType(self.param_types, self.result_types, self.determined_return_ty)

    @property
    def as_bytes(self):
        r = bytearray([0x60])
        param_byte_vals = [type_str2byte_val[ty] for ty in self.param_types]
        raw_param_ba = bytearray(param_byte_vals)
        param_ba = leb128.u.encode(len(raw_param_ba)) + raw_param_ba
        result_byte_vals = [type_str2byte_val[ty] for ty in self.result_types]
        raw_result_ba = bytearray(result_byte_vals)
        result_ba = leb128.u.encode(len(raw_result_ba)) + raw_result_ba
        r.extend(param_ba)
        r.extend(result_ba)
        return r
    @classmethod
    def from_dict(cls, d):
        return cls(d['param'], d['result'])

    @classmethod
    def from_str(cls, s:str):
        s = str(s)
        s = s.split(';;')[0]
        s = s.strip()
        r = func_type_pattern.findall(s)
        if len(r) == 0:
            raise Exception(f'cannot parse funcType from {s}')
        param_types, result_types = r[0]
        param_types = [_ for _ in param_types.split(' ') if _ != '']
        result_types = [_ for _ in result_types.split(' ') if _ != '']
        return cls(param_types, result_types)


def match_func_type(fty1: funcType, fty2: funcType):
    if fty1.result_types != fty2.result_types:
        return False
    if len(fty1.param_types) != len(fty2.param_types):
        return False
    param_match = True
    for p1, p2 in zip(fty1.param_types, fty2.param_types):
        if p1 != p2 and ('any' not in [p1, p2]):
            param_match = False
            break
    return param_match


# @lru_cache(maxsize=8192)
def _add_core1(val1, val2):
    # param1 = self.param_types.copy()
    param2 = val2.param_types#.copy()
    result1 = val1.result_types#.copy()
    # result2 = __value.result_types.copy()
    param2_len = len(param2)
    result1_len = len(result1)
    exchange_num = 0
    min_len = min(param2_len, result1_len)
    while min_len > exchange_num:
        if param2[param2_len-1-exchange_num] == result1[result1_len-1-exchange_num] or param2[param2_len-1-exchange_num] == 'any':
            # param2.pop()
            # result1.pop()
            exchange_num += 1
        else:
            raise FuncTypeCatException('param2 does not match result1')
    
    final_param = param2[:param2_len-exchange_num] + val1.param_types
    assert len( param2[:param2_len-exchange_num]) == 0 or len(result1[:result1_len-exchange_num]) == 0
    if val2.determined_return_ty:
        final_result = val2.result_types
    else:
        final_result = result1[:result1_len-exchange_num] + val2.result_types
    return funcType(final_param, final_result)


def get_func_type_from_ba(ba:bytearray):
    param_type_num, offset = read_next_leb_num(ba, 0)
    # param_val_num = result_type_num
    param_part_ba = ba[offset:param_type_num+offset]
    result_type_num, offset = read_next_leb_num(ba, param_type_num+offset)
    result_part_ba = ba[offset:result_type_num+offset]
    # if read_next_leb_num == 0:
    #     return []
    params = [byte_val2type_str[v] for v in bytearray(param_part_ba)]
    results = [byte_val2type_str[v] for v in bytearray(result_part_ba)]
    return funcType(param_types=params, result_types=results)
        
    
   