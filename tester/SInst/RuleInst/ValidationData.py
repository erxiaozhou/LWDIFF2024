from functools import partial
from typing import Callable, List, Optional, Tuple, Union

from ..InstModel.util import base_func_for_context_scope_exist_func
from .ValidationDataUtil import ContextCheckFuncFactory
from ..InstModel.SelectFuncConstraint import AndFuncChain, BoolFuncChain, OrFuncChain, SelectFuncConstraint, get_or_func

from ..InstModel.ValConstraint import ValConstraint
from ..InstModel.ImSolveInfo import ImSolveInfo
from ..InstModel.PHEnv import PHEnv
from ..RuleInst.RuleV2 import get_func_constraint, get_val_constraints
from ..InstModel.SelectFuncConstraint import always_true


class ValidationData:
    def __init__(self,
                 valid_ty_cs,
                 valid_im_cs,
                 ph_envs:Optional[list[PHEnv]] = None,
                 ):
        self.valid_ty_cs = valid_ty_cs
        self.valid_im_cs = valid_im_cs
        assert ph_envs is not None
        self.ph_envs = ph_envs
        self.all_valid_cs = valid_ty_cs + valid_im_cs
        self.im_solve_infos = self._init_im_solve_infos()
        self.func_constraint:Optional[SelectFuncConstraint] = None
        self.val_constraints:Optional[List[ValConstraint]] = None  # 
        # val_cs0 = get_val_constraints(self.im_solve_infos[0])

        self.context_can_apply_func:Callable = ContextCheckFuncFactory.wrap_as_context_check_func(self._init_context_can_apply_func())

    def _init_context_can_apply_func(self)->Callable:

        if len(self.ph_envs) == 1:
            
            can_apply_func = get_func_constraint(self.im_solve_infos[0]).can_apply_func
            
        else:
            all_funcs = [get_func_constraint(_solve_info).can_apply_func for _solve_info in self.im_solve_infos]
            can_apply_func = get_or_func(all_funcs)
        can_apply_func = _simplify_func_chains(can_apply_func)
        return can_apply_func

    def _init_im_solve_infos(self):
        rs = []
        for ph_env in self.ph_envs:
            rs.append(ImSolveInfo(ph_env, self.valid_im_cs, self.all_valid_cs, True))
        return rs
    
    '''
     ValidationData valid，
    1.  context, op,  imm
    2.  context, op,  imm
    3.  context, op,  imm
    ''' 




    def display(self):
        print('valid_ty_cs')
        for c in self.valid_ty_cs:
            print(c)
        print('---------------------------------')
        print('valid_im_cs')
        for c in self.valid_im_cs:
            print(c)
        print('---------------------------------')
        print('ph_env')
        for ph_env in self.ph_envs:
            print(ph_env)
        print('---------------------------------')
        if self.val_constraints is not None:
            print('val_constraints')
            for c in self.val_constraints:
                print(c)
        else:
            print('val_constraints is None')
        print('---------------------------------')
        print('self.can_apply_func')
        print(self.context_can_apply_func)
        print('---------------------------------')


def _simplify_func_chains(can_apply_func)->Callable:
    # not_fixed = True
    # while not_fixed:
    def inner_polish(can_apply_func)->tuple[Callable, bool]:
        if not isinstance(can_apply_func, (AndFuncChain, OrFuncChain)):
            return can_apply_func, False
        elif isinstance(can_apply_func, AndFuncChain):
            has_mutated = False
            new_funcs = []
            for _sub_func in can_apply_func.funcs:
                new_sub_func, _has_mutated = inner_polish(_sub_func)
                has_mutated = has_mutated or _has_mutated
                new_funcs.append(new_sub_func)
            new_can_apply_func = AndFuncChain(new_funcs)
            new_can_apply_func, _has_mutated = _remove_dup_wrap(new_can_apply_func)
            has_mutated = _has_mutated or has_mutated
            new_can_apply_func2 = _process_empty(new_can_apply_func)
            # if new_can_apply_func is new_can_apply_func2:
            #     _has_mutated = False
            _has_mutated = not (new_can_apply_func is new_can_apply_func2)
            has_mutated = _has_mutated or has_mutated
            return new_can_apply_func2, has_mutated
            raise NotImplementedError
        elif isinstance(can_apply_func, OrFuncChain):
            has_mutated = False
            new_funcs = []
            for _sub_func in can_apply_func.funcs:
                new_sub_func, _has_mutated = inner_polish(_sub_func)
                has_mutated = has_mutated or _has_mutated
                new_funcs.append(new_sub_func)
            # print(len(new_funcs), new_funcs)
            new_can_apply_func = get_or_func(new_funcs)
            if new_can_apply_func is always_true:
                has_mutated = True
            new_can_apply_func, _has_mutated = _remove_dup_wrap(new_can_apply_func)
            _has_mutated = _has_mutated or has_mutated
            new_can_apply_func2 = re_organize_or_func_chain(new_can_apply_func)
            new_can_apply_func2 = _simplify_for_just_context(new_can_apply_func2)
            
            _has_mutated = not (new_can_apply_func is new_can_apply_func2)
            # new_can_apply_func, _has_mutated = inner_polish(new_can_apply_func)
            has_mutated = has_mutated or _has_mutated
            return new_can_apply_func2, has_mutated
            raise NotImplementedError
        else:
            raise Exception
        can_apply_func = re_organize_or_func_chain(can_apply_func)
            
        can_apply_func = _process_empty(can_apply_func)
        can_apply_func = _simplify_for_just_context(can_apply_func)
    has_mutated = True
    # iter_times = 0
    while has_mutated:
        can_apply_func, has_mutated = inner_polish(can_apply_func)
        # iter_times += 1
        # print('iter_times', iter_times)
    
    return can_apply_func


# def wrap_funcs(funcs:List[Callable]):
#     assert len(funcs) >= 2
#     final_func = get_or_func(funcs)
#     final_func = re_organize_or_func_chain(final_func)
#     return final_func
    

def _simplify_for_just_context(func:Callable):
    if isinstance(func, OrFuncChain):
        if all([isinstance(_f, partial) for _f in func]):
            if all([_f.func == base_func_for_context_scope_exist_func for _f in func]):
                # assert 0
                # print('BGFSBGFBWEFWEFWESFSDFSDFSDFSDF')
                return always_true
    return func

# def _simplify_for_just_context_ori(func:Callable):
#     # base_func_for_context_scope_exist_func
#     if isinstance(func, AndFuncChain):
#         new_funcs = []
#         for _sub_func in func.funcs:
#             if isinstance(_sub_func, OrFuncChain):
#                 if all([isinstance(_f, partial) for _f in _sub_func]):
#                     if all([_f.func == base_func_for_context_scope_exist_func for _f in _sub_func]):
#                         continue
#             new_funcs.append(_sub_func)
#         func = AndFuncChain(new_funcs)
#     return func

def _remove_dup_wrap(func:Callable)->tuple[Callable, bool]:
    if isinstance(func, AndFuncChain) and len(func) == 1:
        return func.funcs[0], True
    if isinstance(func, OrFuncChain) and len(func) == 1:
        return func.funcs[0], True
    return func, False
        
    


def _process_empty(func:Callable):
    if isinstance(func, AndFuncChain) and len(func) == 0:
        return always_true
    return func


def re_organize_or_func_chain(func: Callable)->Callable:
    if not isinstance(func, OrFuncChain):
        return func
    if any([not isinstance(f, AndFuncChain) for f in func.funcs]):
        return func
    if len(func.funcs) == 1:
        return func
    assert len(func.funcs) != 0
    funcs = func.funcs

    func_lists = [f.funcs for f in funcs]
    func_list0 = func_lists[0]
    func_list1 = func_lists[1]
    common_funcs = _detect_the_same_ones(func_list0, func_list1)
    if len(common_funcs) == 0:
        return func
    or_unique_ones = []
    for func_list in func_lists:
        unique_ones = list(set(func_list) - common_funcs)
        if len(unique_ones) == 0:
            continue
        elif len(unique_ones) == 1:
            or_unique_ones.append(unique_ones[0])
            continue
        elif len(unique_ones) > 1:
            unique_func = AndFuncChain(unique_ones)
            or_unique_ones.append(unique_func)
            continue
    # * 2. group the funcs
    or_func = get_or_func(or_unique_ones)
    return AndFuncChain([*list(common_funcs), or_func])
    

def _detect_the_same_ones(func_list0, func_list1)->set[Callable]:
    func_set0 = set(func_list0)
    func_set1 = set(func_list1)
    common_funcs = func_set0 & func_set1
    return common_funcs
