from functools import partial
from typing import Callable, Optional

from ..InstModel.SelectFuncConstraint import AndFuncChain, always_true

from extract_block_mutator.Context import Context


def _detect_contexty_is_not_None(context:Optional[Context], *args, **kwds)->bool:
    return context is not None

class ContextCheckFuncFactory:
    _rawfunc2wrapped_func = {}
    @staticmethod
    def wrap_as_context_check_func(base_func:Callable):
        if base_func in ContextCheckFuncFactory._rawfunc2wrapped_func:
            return ContextCheckFuncFactory._rawfunc2wrapped_func[base_func]
        # def wrapped_func(context:Context):
        #     return base_func(context=context, insts=[])
        # 
        if base_func is always_true:
            wrapped_func = base_func
        else:
            wrapped_func = AndFuncChain([_detect_contexty_is_not_None, base_func])
        # 
        # assert 0
        final_func = partial(wrapped_func, insts=[])
        # wrapped_func = _wrap_not_always_true(wrapped_func)
        ContextCheckFuncFactory._rawfunc2wrapped_func[base_func] = final_func
        return final_func
