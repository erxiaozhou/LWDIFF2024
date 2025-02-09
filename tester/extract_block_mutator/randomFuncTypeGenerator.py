from WasmInfoCfg import base_ty_strs
from random import randint, choice
from .funcTypeFactory import funcTypeFactory


class randomFuncTypeGenerator:
    def __init__(self, max_param_num=None, max_result_num=None, ty_str_candidates=None):
        self.max_param_num = max_param_num
        self.max_result_num = max_result_num
        self.ty_str_candidates = ty_str_candidates
        
    def generate_one(self):
        
        if self.max_param_num is None:
            param_num = None
        else:
            param_num = randint(0, self.max_param_num)
        if self.max_result_num is None:
            result_num = None
        else:
            result_num = randint(0, self.max_result_num)
        # print(self.max_param_num, self.max_result_num)
        return generate_random_funcType(param_num, result_num, self.ty_str_candidates)


def generate_random_funcType(param_num=None, result_num=None, ty_str_candidates=None):
    if param_num is None:
        param_num = randint(0, 2)
    if result_num is None:
        result_num = randint(0, 2)
    if ty_str_candidates is None:
        ty_str_candidates = base_ty_strs
    param_types = [choice(ty_str_candidates) for _ in range(param_num)]
    result_types = [choice(ty_str_candidates) for _ in range(result_num)]
    return funcTypeFactory.generate_one_func_type_default(param_types, result_types)
