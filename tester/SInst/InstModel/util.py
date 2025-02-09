
from extract_block_mutator.Context import Context
from extract_block_mutator.InstUtil.Inst import Inst
from .specialContextConstVal import specialContextConstVal
from .ContextScopeVal import paramSpecialIdxsScope
from typing import List


def base_func_for_context_size_func(context: Context, insts: List[Inst], r_context_val:specialContextConstVal, l_const, relation):
    r_context_cval = r_context_val.get_concrete_value(context=context)
    return relation.compare(l_const, r_context_cval)


def base_func_for_context_scope_exist_func(context: Context, insts: List[Inst], context_scope:paramSpecialIdxsScope):
    return len(context_scope.get_concrete_valset_from_context(context)) > 0


def base_func_for_multiple_context_scope_exist_func(context: Context, insts: List[Inst], context_scopes:List[paramSpecialIdxsScope]):
    if len(context_scopes) == 0:
        raise ValueError('context_scopes should not be empty')
    cur_scope = context_scopes[0].get_concrete_valset_from_context(context)
    for scope in context_scopes[1:]:
        cur_scope = cur_scope.intersection(scope.get_concrete_valset_from_context(context))
        if len(cur_scope) == 0:
            return False
    return len(cur_scope) > 0

