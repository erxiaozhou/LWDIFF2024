from itertools import product
from .funcType import funcType
from WasmInfoCfg import val_type_strs_list


def _init_base_func_tys():
    d={}
    _insert_func_ty([], [], d, True)
    _insert_func_ty([], [], d, False)
    repeat_times = [1, 2, 3]
    for repeat in repeat_times:
        _init_batch_types(repeat, val_type_strs_list, d, determined_return_ty=False)
        _init_batch_types(repeat, val_type_strs_list, d, determined_return_ty=True)
    _init_batch_types(4, val_type_strs_list,d, determined_return_ty=False)
    return d

def _init_batch_types(repeat, _types, d, determined_return_ty):
    types = list(product(_types, repeat=repeat))
    for split_pos in range(repeat+1):
        for _cur_types in types:
            params = _cur_types[:split_pos]
            results = _cur_types[split_pos:]
            _insert_func_ty(params, results, d, determined_return_ty)
        
def _insert_func_ty(params, results, d, determined_return_ty):
    params = tuple(params)
    results = tuple(results)
    new_func_ty = funcType(params, results, determined_return_ty=determined_return_ty)
    d[(params, results, determined_return_ty)] = new_func_ty


class funcTypeFactory:
    _generated_func_tys:dict = _init_base_func_tys()
    def __init__(self):
        pass

    @staticmethod
    def generate_one_func_type_default(param_type, result_type, determined_return_ty=False)->funcType:
        param_type = tuple(param_type)
        result_type = tuple(result_type)
        if (param_type, result_type, determined_return_ty) in funcTypeFactory._generated_func_tys:
            return funcTypeFactory._generated_func_tys[(param_type, result_type, determined_return_ty)]
        else:
            new_func_ty = funcType(param_type, result_type, determined_return_ty)
            return new_func_ty
        
    @staticmethod
    def func_type_adder(ty1:funcType, ty2:funcType)->funcType:
        return ty1+ty2
