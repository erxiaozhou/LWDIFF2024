
from ..InstUtil.OneInstReqUtil import InstTypeReqF
from config_inst_info import all_inst_names


def _type_has_v128(d):
    for ty in d.param_types:
        if ty == 'v128':
            return True
    for ty in d.result_types:
        if ty == 'v128':
            return True
    return False


_v128_determined_inst_names = []
for inst_name, types in InstTypeReqF().naive_inst_name2func_types.items():
    for type_ in types:
        if _type_has_v128(d=type_):
            _v128_determined_inst_names.append(inst_name)
            continue

_non_v128_all_names = [
    d for d in all_inst_names if d not in _v128_determined_inst_names]

_cannot_insert_insts = {'loop', 'if', 'block', 'else', 'end'}
all_names_can_insert = set(
    [x for x in all_inst_names if x not in _cannot_insert_insts])
non_v128_all_names_can_insert = set(
    [x for x in _non_v128_all_names if x not in _cannot_insert_insts])
