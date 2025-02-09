from itertools import product
from .funcType import funcType
from WasmInfoCfg import val_type_strs_list


def _init_base_func_tys():
    d={}
    # if len(funcTypeFactory._generated_func_tys) == 0:
        # len == 0
    _insert_func_ty([], [], d, True)
    _insert_func_ty([], [], d, False)
    # len == 1, 2, 3
    repeat_times = [1, 2, 3]
    for repeat in repeat_times:
        _init_batch_types(repeat, val_type_strs_list, d, determined_return_ty=False)
        _init_batch_types(repeat, val_type_strs_list, d, determined_return_ty=True)
    # 4
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
        # return funcType(param_types, result_types, determined_return_ty)
        param_type = tuple(param_type)
        result_type = tuple(result_type)
        if (param_type, result_type, determined_return_ty) in funcTypeFactory._generated_func_tys:
            return funcTypeFactory._generated_func_tys[(param_type, result_type, determined_return_ty)]
        else:
            new_func_ty = funcType(param_type, result_type, determined_return_ty)
            # param_len = len(params)
            # result_len = len(results)
            # if param_len + result_len < 4:
            #     funcTypeFactory._generated_func_tys[(params, results)] = new_func_ty
            return new_func_ty
    # @staticmethod
    # def generate_one_func_type_default(param_types, result_types)->funcType:
    #     return funcType(param_types, result_types)
        
    @staticmethod
    # @lru_cache(maxsize=8192)
    def func_type_adder(ty1:funcType, ty2:funcType)->funcType:
        return ty1+ty2
