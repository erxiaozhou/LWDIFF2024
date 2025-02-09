from random import choice, randint
from typing import Callable, Optional
from WasmInfoCfg import base_ty_strs
from WasmInfoCfg import ContextValAttr, DataSegAttr, ElemSecAttr, globalValMut
from extract_block_mutator.ModuleFuzzerUtil.data_memory_related import generate_a_data_seg
from extract_block_mutator.ModuleFuzzerUtil.table_and_elem_related import generate_elem_seg
from extract_block_mutator.Context import Context
from extract_block_mutator.get_data_shell import has_func_idx
from .InstValRelation import InstValRelation
from extract_block_mutator.ModuleFuzzerUtil.DefGenerator import memDescGenerator, oneTableDescGenerator
from extract_block_mutator.ModuleFuzzerUtil.global_related import generate_global_def
from extract_block_mutator.WasmParser import WasmParser
from .ContextScopeVal import paramSpecialIdxsScope, specialIdxsType

from .util import base_func_for_context_scope_exist_func, base_func_for_context_size_func
from .specialContextConstVal import specialContextConstVal
from .SelectFuncConstraint import AndFuncChain,  PreFuncChain, SelectFuncConstraint, always_true
from functools import partial

def _all_partial_And_pattern(func:Callable)->bool:
    # assert 
    if isinstance(func, AndFuncChain):
        assert not any([f==always_true for f in func.raw_funcs])
        if all(map(lambda x: isinstance(x, partial), func.raw_funcs)):
            return True
    return False

def get_a_mock_parser(context:Context) -> WasmParser:
    return WasmParser(
        types=context.types,
        imports=[],
        defined_func_ty_ids=context.func_type_ids,
        defined_table_datas=context.defined_table_datas,
        defined_memory_datas=context.defined_memory_datas,
        defined_globals=context.defined_globals,
        exports=[],
        elem_sec_datas=context.elem_sec_datas,
        data_sec_datas=context.data_sec_datas,
        defined_funcs=[None]*context.func_num
        
        
    )

def transfer_func_constraint(func_constraint: SelectFuncConstraint) -> SelectFuncConstraint:
    new_can_apply_funcs = AndFuncChain([])
    new_pre_funcs = PreFuncChain([])
    # 
    assert len(new_pre_funcs) == 0
    if _all_partial_And_pattern(func_constraint.can_apply_func):
        # assert 0
        for can_apply_func in func_constraint.can_apply_func:
            possible_pre_func = get_pre_func(can_apply_func)
            if possible_pre_func is None:
                new_can_apply_funcs.append(can_apply_func)
            else:
                # print('possible_pre_func', possible_pre_func)
                new_pre_funcs.append(possible_pre_func)
        new_func_constraint = SelectFuncConstraint(
            can_apply_func=new_can_apply_funcs,
            pre_func=new_pre_funcs
        )
        # print('new_func_constraint', new_func_constraint)
        # 
        return new_func_constraint
    all_can_apply_raw_funcs = func_constraint.can_apply_func.all_raw_funcs
    finished = True
    for f in all_can_apply_raw_funcs:
        _pre_func = get_pre_func(f)
        if _pre_func is not None:
            new_pre_funcs.append(_pre_func)
        else:
            # assert 0, print(f)
            if not no_process_func(f):
                raise NotImplementedError(f'f: {f}')
            finished = False
            # new_can_apply_funcs.append(f)
    if finished:
        # assert 0
        return SelectFuncConstraint(
            can_apply_func = new_can_apply_funcs,
            pre_func = new_pre_funcs
        )
    return func_constraint


def no_process_func(can_apply_func:Callable)->bool:
    if isinstance(can_apply_func, partial):
        func = can_apply_func.func
        if func == base_func_for_context_size_func:
            keywards = can_apply_func.keywords
            # r_context_val:specialContextConstVal = keywards['r_context_val']
            # required_const = int(keywards['l_const'])
            relation = keywards['relation']
            if relation == InstValRelation.GE:
                return True
    assert 0
    return False
    


def get_pre_func(can_apply_func)->Optional[Callable]:
    # assert isinstance(can_apply_func, partial)
    if isinstance(can_apply_func, partial):
        func = can_apply_func.func
        # if not isinstance(func, FuncChain):
        #     raise ValueError(f'Not FuncChain :: func: {func}')
        # assert isinstance(func, FuncChain)
        assert len(can_apply_func.args) == 0
        keywards = can_apply_func.keywords
        # 
        if func == base_func_for_context_scope_exist_func:
            context_scope:paramSpecialIdxsScope = keywards['context_scope']
            param_dict = context_scope.param
            special_idxs_type: specialIdxsType = context_scope.special_idxs_type
            if special_idxs_type == specialIdxsType.LocalWithAttr:
                to_insert_local_types = param_dict['local_types']
                return lambda context, insts: context.local_types.extend(list(to_insert_local_types))
            if special_idxs_type == specialIdxsType.TableWithAttr:
                to_insert_table_types:set = param_dict['table_types']
                to_insert_table_types = to_insert_table_types.intersection({'funcref', 'externref'})
                target_type = choice(list(to_insert_table_types))
                
                return lambda context, insts: context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one(target_type))
            if special_idxs_type == specialIdxsType.GlobalWithMut:
                to_append_globals = []
                for mut_ in param_dict['global_muts']:
                    for ty in base_ty_strs:
                        global_val = generate_global_def(mut_, ty)
                        to_append_globals.append(global_val)
                return lambda context, insts: context.defined_globals.extend(to_append_globals)
            if special_idxs_type == specialIdxsType.GlobalWithType:
                target_val_types = param_dict['global_types']
                muts = list(globalValMut)
                to_append_globals = []
                for mut_ in muts:
                    for ty in target_val_types:
                        global_val = generate_global_def(mut_, ty)
                        to_append_globals.append(global_val)
                return lambda context, insts: context.defined_globals.extend(to_append_globals)
                    # context.
            if special_idxs_type == specialIdxsType.OneTableSize:
                target_len = param_dict['min_length']
                return lambda context, insts: context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one(min_limit=target_len))
            if special_idxs_type == specialIdxsType.ElemWithRefType:
                ref_types = param_dict['elem_seg_ref_type']
                ref_types = ref_types.intersection({'funcref', 'externref'})
                attrs = list(ElemSecAttr)
                # assert 0
                def _func6(context:Context, insts):
                    mock_parser = get_a_mock_parser(context)
                    for ref_type in ref_types:
                        for attr in attrs:
                            if attr == ElemSecAttr.active:
                                context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one(ref_type))
                            new_def = generate_elem_seg(mock_parser, elem_seg_attr=attr, ref_type=ref_type)
                            context.elem_sec_datas.append(new_def)
                return _func6
            if special_idxs_type == specialIdxsType.DataWithAttr:
                data_attrs = param_dict['data_active']
                def _func8(context:Context, insts):
                    mock_parser = get_a_mock_parser(context)
                    for data_attr in data_attrs:
                        if data_attr == DataSegAttr.active:
                            if context.defined_memory_num == 0:
                                context.defined_memory_datas.append(memDescGenerator.generate_valid_one())
                        new_def = generate_a_data_seg(mock_parser, data_attr)
                        context.data_sec_datas.append(new_def)
            if special_idxs_type == specialIdxsType.ElemWithAttr:
                ref_type = choice(['funcref', 'externref'])
                attrs = param_dict['elem_attrs']
                def _func9(context, insts):
                    mock_parser = get_a_mock_parser(context)
                    
                    for attr in attrs:
                        if attr == ElemSecAttr.active:
                            context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one(ref_type))
                        new_def = generate_elem_seg(mock_parser, elem_seg_attr=attr, ref_type=ref_type)
                        context.elem_sec_datas.append(new_def)
            if special_idxs_type == specialIdxsType.RefedFuncIdx:
                def _func7(context:Context, insts):
                    attr = choice(list(ElemSecAttr))
                    if attr == ElemSecAttr.active:
                        if len(context.defined_table_datas) == 0:
                            context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one())
                    new_elem_seg = generate_elem_seg(get_a_mock_parser(context),ref_type='funcref', elem_seg_attr=attr)
                    for i in range(20):
                        if has_func_idx(new_elem_seg):
                            break
                    attr = choice(list(ElemSecAttr))
                    if attr == ElemSecAttr.active:
                        if len(context.defined_table_datas) == 0:
                            context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one())
                        new_elem_seg = generate_elem_seg(get_a_mock_parser(context),ref_type='funcref', elem_seg_attr=attr)
                    context.elem_sec_datas.append(new_elem_seg)
                return _func7
                
        if func == base_func_for_context_size_func:
            # return None
            r_context_val:specialContextConstVal = keywards['r_context_val']
            required_const = int(keywards['l_const'])
            relation = keywards['relation']
            if r_context_val.context_val_type == ContextValAttr.Locals:
                if relation in {InstValRelation.LT, InstValRelation.LE}:
                    def _func1(context:Context, insts):
                        concrete_context_cval = r_context_val.get_concrete_value(context=context)
                        to_append_num = required_const - concrete_context_cval
                        if relation == InstValRelation.LT:
                            to_append_num += 1
                        to_append_num = randint(1, 3)
                        to_insert_local_types = []
                        for _ in range(to_append_num):
                            to_insert_local_types.append(choice(base_ty_strs))
                        context.local_types.extend(list(to_insert_local_types))
                    return _func1
            if r_context_val.context_val_type == ContextValAttr.MemSec:
                if relation in {InstValRelation.LT, InstValRelation.LE}:
                    def _func2(context:Context, insts):
                        concrete_context_cval = r_context_val.get_concrete_value(context=context)
                        to_append_num = required_const - concrete_context_cval
                        if relation == InstValRelation.LT:
                            to_append_num += 1
                        for _ in range(to_append_num):
                            context.defined_memory_datas.append(memDescGenerator.generate_valid_one())
                    return _func2
            if r_context_val.context_val_type == ContextValAttr.TableSec:
                if relation in {InstValRelation.LT, InstValRelation.LE}:
                    def _func3(context:Context, insts):
                        concrete_context_cval = r_context_val.get_concrete_value(context=context)
                        to_append_num = required_const - concrete_context_cval
                        if relation == InstValRelation.LT:
                            to_append_num += 1
                        to_append_num = randint(1, 3)
                        for _ in range(to_append_num):
                            context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one())
                    return _func3
            if r_context_val.context_val_type == ContextValAttr.DataSec:
                if relation in {InstValRelation.LT, InstValRelation.LE}:
                    def _func4(context:Context, insts):
                        concrete_context_cval = r_context_val.get_concrete_value(context=context)
                        to_append_num = required_const - concrete_context_cval
                        mock_parser = get_a_mock_parser(context)
                        if relation == InstValRelation.LT:
                            to_append_num += 1
                        to_append_num = randint(1, 3)
                        to_insert_attrs = [choice([DataSegAttr.active, DataSegAttr.passive]) for _ in range(to_append_num)]
                        # need insert table
                        if DataSegAttr.active in to_insert_attrs:
                            if context.defined_memory_num == 0:
                                context.defined_memory_datas.append(memDescGenerator.generate_valid_one())
                        for attr in to_insert_attrs:
                        # for _ in range(to_append_num):
                            new_def = generate_a_data_seg(mock_parser,attr=attr)
                            context.data_sec_datas.append(new_def)
                    return _func4
            if r_context_val.context_val_type == ContextValAttr.ElemSec:
                if relation in {InstValRelation.LT, InstValRelation.LE}:
                    def _func10(context:Context, insts):
                        concrete_context_cval = r_context_val.get_concrete_value(context=context)
                        to_append_num = required_const - concrete_context_cval
                        mock_parser = get_a_mock_parser(context)
                        if relation == InstValRelation.LT:
                            to_append_num += 1
                        to_append_num = randint(1, 3)
                        to_insert_elem_attrs = [choice(list(ElemSecAttr)) for _ in range(to_append_num)]
                        # whether need insert table
                        if ElemSecAttr.active in to_insert_elem_attrs:
                            if len(context.defined_table_datas) == 0:
                                context.defined_table_datas.append(oneTableDescGenerator.generate_valid_one())
                        for attr in to_insert_elem_attrs:
                            new_def = generate_elem_seg(mock_parser, elem_seg_attr=attr)
                            context.elem_sec_datas.append(new_def)
                    return _func10
            if r_context_val.context_val_type == ContextValAttr.Globals:
                if relation in {InstValRelation.LT, InstValRelation.LE}:
                    def _func11(context:Context, insts):
                        concrete_context_cval = r_context_val.get_concrete_value(context=context)
                        to_append_num = required_const - concrete_context_cval
                        if relation == InstValRelation.LT:
                            to_append_num += 1
                        to_append_num = randint(1, 3)
                        for _ in range(to_append_num):
                            context.defined_globals.append(generate_global_def())
                    return _func11
            # if r_context_val.context_val_type == ContextValAttr.Types:
            #     if relation in {InstValRelation.LS, InstValRelation.LE}:
            #         def
            
            
    else:
        return None
    return None
    raise NotImplementedError
    


