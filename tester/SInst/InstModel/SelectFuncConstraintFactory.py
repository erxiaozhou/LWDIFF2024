from functools import partial
from .SelectFuncConstraint import SelectFuncConstraint, always_true, do_nothing
from .InstValRelation import InstValRelation
from typing import List, Tuple
from .specialContextConstVal import specialContextConstVal
from .ContextScopeVal import paramSpecialIdxsScope
from .util import base_func_for_context_size_func
from .util import base_func_for_context_scope_exist_func


class SelectFuncConstraintFactory:
    _generated_funcs:dict[Tuple, SelectFuncConstraint] = {}
    @staticmethod
    def compared_with_context_size_func(
            l_const:int,
            r_context_val_attr:specialContextConstVal, 
                                       relation:InstValRelation):
        paras = (r_context_val_attr, l_const, relation)
        if paras not in SelectFuncConstraintFactory._generated_funcs:
            _func = partial(base_func_for_context_size_func, r_context_val=r_context_val_attr, l_const=l_const, relation=relation)
            SelectFuncConstraintFactory._generated_funcs[paras] = SelectFuncConstraint.from_one_func(can_apply_func=_func,  pre_func=do_nothing)
        return SelectFuncConstraintFactory._generated_funcs[paras]
    
    @staticmethod
    def context_scope_exist_func( context_scope:paramSpecialIdxsScope)->SelectFuncConstraint:
        paras = ('exist', context_scope)
        if paras not in SelectFuncConstraintFactory._generated_funcs:
            _func = partial(base_func_for_context_scope_exist_func, context_scope=context_scope)
            SelectFuncConstraintFactory._generated_funcs[paras] = SelectFuncConstraint.from_one_func(can_apply_func=_func,  pre_func=do_nothing)
        return SelectFuncConstraintFactory._generated_funcs[paras]

    @staticmethod
    def get_default_func_constraint()->SelectFuncConstraint:
        paras = ('default',)
        if paras not in SelectFuncConstraintFactory._generated_funcs:
            _func = SelectFuncConstraint.from_one_func(can_apply_func=always_true,  pre_func=do_nothing)
            SelectFuncConstraintFactory._generated_funcs[paras] = _func
        return SelectFuncConstraintFactory._generated_funcs[paras] 
