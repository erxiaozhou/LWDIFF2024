from functools import lru_cache
from typing import Callable, Optional
from SInst.RuleInst.GptInst2GRule import GptInstKM
from ..Context import Context


def _get_context_vfunc2ops(gpt_data:GptInstKM)->dict[Callable, list[str]]:
    vfunc2ops:dict[Callable, list[str]] = {}
    for inst_name, vfunc in gpt_data.raw_inst_name2valid_context_func.items():
        if vfunc not in vfunc2ops:
            vfunc2ops[vfunc] = []
        vfunc2ops[vfunc].append(inst_name)
    return vfunc2ops


def _get_not_func2ops(func2ops:dict[Callable, list[str]])->dict[Callable, list[str]]:
    not_func2ops:dict[Callable, list[str]] = {}
    for func, ops in func2ops.items():
        new_func = get_not_func(func)
        not_func2ops[new_func] = ops
    return not_func2ops

def get_not_func(func:Callable)->Callable:
    def new_func(context:Optional[Context]):
        # print(f'|| func: {func} ;; func(context)', func(context))
        return not func(context)
    return new_func

    
class ToSkipOpDetectorbyContext:
    _func2ops = _get_context_vfunc2ops(GptInstKM(just_valid_part=True))
    _not_func2ops = _get_not_func2ops(_func2ops)
    @staticmethod
    def get_skip_ops_by_Context(context:Optional[Context]):
        to_skip_ops = set()
        for func, ops in ToSkipOpDetectorbyContext._not_func2ops.items():
            if func(context):
                to_skip_ops.update(ops)
        return to_skip_ops


def get_skip_ops_by_Context(context:Optional[Context]):
    return ToSkipOpDetectorbyContext.get_skip_ops_by_Context(context)
