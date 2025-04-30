
from .SpecialContextConstVal.SpecialContextConstVal import SpecialContextOneDefSize, SpecialContextOneVal, SpecialContextConstVal, get_parent_size_val
from extract_block_mutator.Context import Context
from extract_block_mutator.InstUtil.Inst import Inst

from .ContextScopeVal import paramSpecialIdxsScope
from typing import List, Union
from .InstValRelationHelper import InstValRelationHelper

class NotApplicableError(Exception):
    """"""
    pass

def base_func_for_context_size_func(context: Context, insts: List[Inst], r_context_val:Union[SpecialContextConstVal, SpecialContextOneDefSize], l_const, relation):
    if not isinstance(r_context_val, (SpecialContextOneVal, SpecialContextOneDefSize)):
        raise Exception(f'r_context_val should be SpecialContextConstVal, but got {type(r_context_val)} , r_context_val is {r_context_val}')
    if r_context_val.idx_repr is not None and not r_context_val.idx_repr.isdigit():
        # raise ValueError(f'r_context_val.idx_repr should be a digit, but got {r_context_val.idx_repr}  r_context_val : {r_context_val}  l_const : {l_const}  relation : {relation}')
        assert isinstance(r_context_val, SpecialContextOneDefSize)
        concrete_parent_size = get_parent_size_val(r_context_val).get_size_concrete_val(context)
        for idx in range(concrete_parent_size):
            considered_val = SpecialContextOneDefSize(r_context_val.context_val_type, str(idx), r_context_val.val_attr)
            if InstValRelationHelper.compare(relation, l_const, considered_val.get_size_concrete_val(context)):
                return True
        return False
    else:
        r_context_cval = r_context_val.get_size_concrete_val(context)
        return InstValRelationHelper.compare(relation, l_const, r_context_cval)


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

