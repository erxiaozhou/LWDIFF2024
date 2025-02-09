from ..InstUtil.OneInstReqUtil import InstTypeReqF
from ..funcType import check_result_can_support_para_wc_len
from functools import lru_cache
from config_inst_info import  all_inst_names


new_param2inst_names = {}
for inst_name, func_types in InstTypeReqF().naive_inst_name2func_types.items():
    for func_type in func_types:
        _key = tuple(func_type.param_types)
        new_param2inst_names.setdefault(_key, []).append(inst_name)

non_determined_inst_names = all_inst_names - set(new_param2inst_names.keys())


@lru_cache(maxsize=8192)
def get_determined_possible_ops_core_with_prefix(cur_stack:tuple[str]):
    possible_inst_names = set()
    for param_types, inst_names in new_param2inst_names.items():
        if check_result_can_support_para_wc_len(cur_stack, param_types):
            possible_inst_names.update(inst_names)
    return possible_inst_names
