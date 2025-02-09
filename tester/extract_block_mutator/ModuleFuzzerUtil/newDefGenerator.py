from random import choice
from typing import Optional

from extract_block_mutator.get_data_shell import get_table_attr

from ..DefShell import gen_active_data_seg0, gen_active_data_seg1, gen_exprs_repr_ref_insts, gen_limit, gen_mem_from_limit, gen_passive_data_seg, gen_table_type, get_offset_inst_from_int
from ..DefShell import gen_elem_seg1, gen_elem_seg5, gen_elem_seg2, gen_elem_seg3, gen_elem_seg4, gen_elem_seg0, gen_elem_seg6, gen_elem_seg7


from .util import gen_random_bytes, generate_common_name

from ..WasmParser import WasmParser
from .ValueField import alwaysValidOneFieldListField, alwaysValidStringField, oneGenFuncValueField, funcDeterminedRangeIntValueField
from .ValueField import FieldFunc
from .ValueField import alwaysValidDiscreteValueField
from ..specialConst import SpecialDefConst, SpecialModuleConst
from ..funcTypeFactory import funcTypeFactory
from ..encode.NGDataPayload import DataPayloadwithName
# memory ==========================================================
def _determine_min_memory_page_num_by_cur_num(cur_mem_page_num):
    return max(0, cur_mem_page_num)

# def _


class memLimitGenerator:
    # ! 
    valid_min_field = funcDeterminedRangeIntValueField(FieldFunc(_determine_min_memory_page_num_by_cur_num), SpecialDefConst.MaxMinMemPages.get_concrete_value(),False, False)
    valid_max_field = funcDeterminedRangeIntValueField(FieldFunc(_determine_min_memory_page_num_by_cur_num), SpecialDefConst.CommonMaxMemPages.get_concrete_value(),False, False)
    valid_max_field.insert_a_special_task_generation_prob(None, 0.5)

    @staticmethod
    def generate_valid_one(cur_mem_page_num:int)->DataPayloadwithName:
        min_v = memLimitGenerator.valid_min_field.random_valid_cvalue(cur_mem_page_num=cur_mem_page_num)
        max_v = memLimitGenerator.valid_max_field.random_valid_cvalue(cur_mem_page_num=cur_mem_page_num)

        if max_v is not None and min_v > max_v:
            min_v, max_v = max_v, min_v
        return gen_limit(min_v, max_v)

class memDescGenerator:
    @staticmethod
    def generate_valid_one(cur_mem_page_num:Optional[int]=None)->DataPayloadwithName:
        if cur_mem_page_num is None:
            cur_mem_page_num = 0
        limit = memLimitGenerator.generate_valid_one(cur_mem_page_num=cur_mem_page_num)
        return gen_mem_from_limit(limit)


# table ==========================================================
class tableLimitGenerator:
    valid_min_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.MaxMinTableLen.get_concrete_value(),False, False)
    valid_max_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.CommonMaxTableLen.get_concrete_value(),False, False)
    valid_max_field.insert_a_special_task_generation_prob(None, 0.5)

    @staticmethod
    def generate_valid_one()->DataPayloadwithName:
        min_v = tableLimitGenerator.valid_min_field.random_valid_cvalue()
        max_v = tableLimitGenerator.valid_max_field.random_valid_cvalue()
        if max_v is not None and min_v > max_v:
            min_v, max_v = max_v, min_v
        return gen_limit(min_v, max_v)
    
unconstrain_ref_type_field = alwaysValidDiscreteValueField(['funcref', 'externref'], [0.7, 0.3])

class oneTableDescGenerator:
    
    @staticmethod
    def generate_valid_one(target_type:Optional[str]=None)->DataPayloadwithName:
        limit: DataPayloadwithName = tableLimitGenerator.generate_valid_one()
        if target_type is None:
            table_type = unconstrain_ref_type_field.random_valid_cvalue()
        else:
            table_type = target_type
        return gen_table_type(table_type, limit)

    @staticmethod
    def generate_min_limit_valid_one(target_type:Optional[str]=None, min_limit:int=0)->DataPayloadwithName:
        limit: DataPayloadwithName = gen_limit(min_limit, None)
        if target_type is None:
            table_type = unconstrain_ref_type_field.random_valid_cvalue()
        else:
            table_type = target_type
        return gen_table_type(table_type, limit)


# start ======================================================

def _valid_start_func_candis_candis(wat_parser:WasmParser, skip_idxs=None) -> int:
    if skip_idxs is None:
        skip_idxs = []
    enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
    defined_func_idxs = [idx for idx, func in enumerate(wat_parser.defined_funcs) if (func.func_ty == enpry_ty) and (idx not in skip_idxs)]
    # assert len(defined_func_idxs) > 0
    if len(defined_func_idxs) == 0:
        raise ValueError(f'no valid start func: skip_idxs:{skip_idxs}; func_num: {wat_parser.func_num} {startSecGenerator.can_generate_valid_one(wat_parser)}')
    return choice(defined_func_idxs)

def _invalid_start_func_candis(wat_parser) -> int:
    enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
    defined_func_idxs = [idx for idx, func in enumerate(wat_parser.defined_funcs) if func.func_ty != enpry_ty]
    assert len(defined_func_idxs) > 0
    return choice(defined_func_idxs)


class startSecGenerator:
    idx_field = oneGenFuncValueField(FieldFunc(_valid_start_func_candis_candis), FieldFunc(_invalid_start_func_candis))

    @staticmethod
    def can_generate_valid_one(wat_parser:WasmParser):
        enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
        for func in wat_parser.defined_funcs:
            if func.func_ty== enpry_ty:
                return True
        return False

    @staticmethod
    def can_generate_multi_valid(wat_parser:WasmParser):
        enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
        defined_func_idxs = [idx for idx, func in enumerate(wat_parser.defined_funcs) if func.func_ty == enpry_ty]
        return len(defined_func_idxs) > 1


    @staticmethod
    def generate_valid_one(wat_parser: WasmParser, skip_idxs=None):
        idx = startSecGenerator.idx_field.random_valid_cvalue(wat_parser=wat_parser, skip_idxs=skip_idxs)
        return idx

    @staticmethod
    def generate_invalid_one(wat_parser: WasmParser):
        idx = startSecGenerator.idx_field.random_invalid_cvalue(wat_parser=wat_parser)
        return idx

# data ======================================================
def _get_max_length_of_mem(memory_idx, wat_parser:WasmParser):
    mem_length = SpecialModuleConst.CurMemLen.get_concrete_value(wat_parser, memory_idx=memory_idx)
    return mem_length


def _get_length_for_active_data_sec(determined_offset, wat_parser:WasmParser, memory_idx=0):
    mem_length = _get_max_length_of_mem(memory_idx, wat_parser)
    rest_length = mem_length - determined_offset
    max_length = min(rest_length, SpecialDefConst.CommonMaxDataLen.get_concrete_value())
    return max_length

data_field = alwaysValidStringField(FieldFunc(gen_random_bytes))

class activeDataSegmentGenerator:
    def_type_idx_field =  alwaysValidDiscreteValueField([0, 1], [0.5, 0.5])
    mem_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurDefMemNum.get_concrete_value),False, True)
    offset_fileld = funcDeterminedRangeIntValueField(0, FieldFunc(func=_get_max_length_of_mem), False, False)  #
    actual_length_field = funcDeterminedRangeIntValueField(0, FieldFunc(_get_length_for_active_data_sec), False, False)
    
    @staticmethod
    def can_insert(wat_parser:WasmParser):
        return len(wat_parser.defined_memory_datas) > 0
    @staticmethod
    def generate_valid_one(wat_parser:WasmParser):
        def_idx = activeDataSegmentGenerator.def_type_idx_field.random_valid_cvalue()
        if def_idx == 0:
            memory_idx = 0
        else:
            memory_idx = activeDataSegmentGenerator.mem_idx_field.random_valid_cvalue(wat_parser=wat_parser)
        offset = activeDataSegmentGenerator.offset_fileld.random_valid_cvalue(memory_idx=memory_idx, wat_parser=wat_parser)
        actual_length = activeDataSegmentGenerator.actual_length_field.random_valid_cvalue(
            determined_offset=offset,
            wat_parser=wat_parser,
            memory_idx=memory_idx
        )
        data = data_field.random_valid_cvalue(length=actual_length)
        if def_idx == 0:
            def_ = gen_active_data_seg0(data, offset)
        else:
            def_ = gen_active_data_seg1(data, offset, memory_idx)
        return def_
        


class passiveDataSegmentGenerator:
    actual_length_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.CommonMaxDataLen.get_concrete_value(), False, False)
    
    @staticmethod
    def can_insert(*args, **kwds):
        return True
    
    @staticmethod
    def generate_valid_one():
        actual_length = passiveDataSegmentGenerator.actual_length_field.random_valid_cvalue()
        data = data_field.random_valid_cvalue(length=actual_length)
        return gen_passive_data_seg(data)
    

# elem ===================================================================================
# 1.  all func idx
# 2.  all none 
# 3. 

_one_externref_field = alwaysValidDiscreteValueField([None])
_one_funcref_field_with_null = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurFuncNum.get_concrete_value), False, True)
_one_funcref_field_with_null.insert_a_special_task_generation_prob(None, 0.2)

_funcref_field_all_null = alwaysValidOneFieldListField(alwaysValidDiscreteValueField([None]))
_one_funcref_field_without_null= alwaysValidOneFieldListField(funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurFuncNum.get_concrete_value), False, True))


_externrefs_fields = alwaysValidOneFieldListField(_one_externref_field)
_funcrefs_fields = alwaysValidOneFieldListField(_one_funcref_field_with_null)
ref_type2fields = {
    'funcref': _funcrefs_fields,
    'externref': _externrefs_fields
}
unconstrain_elem_list_length_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.MaxOneElemLen.get_concrete_value(), False, False)


class passiveElemSegmentGenerator:
    def_type_idx_field =  alwaysValidDiscreteValueField([1, 5], [0.5, 0.5])
    @staticmethod
    def can_insert(*args, **kwds):
        return True

    @staticmethod
    def generate_valid_one(wat_parser:WasmParser, ref_type:Optional[str]=None):
        if ref_type is None:
            ref_type = unconstrain_ref_type_field.random_valid_cvalue()
        if ref_type != 'funcref':
            def_idx = 5
        # determine def id
        func_num = wat_parser.func_num
        if func_num == 0:
            def_idx = 5
        else:
            def_idx = passiveElemSegmentGenerator.def_type_idx_field.random_valid_cvalue()

        actual_length = unconstrain_elem_list_length_field.random_valid_cvalue(wat_parser=wat_parser)
        assert isinstance(ref_type, str)
        if func_num == 0 and ref_type == 'funcref':
            elems = _funcref_field_all_null.random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            exprs = gen_exprs_repr_ref_insts(elems, ref_type)
            return gen_elem_seg5(exprs, ref_type)
        elif def_idx == 1:
            elems = _one_funcref_field_without_null.random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            return gen_elem_seg1(elems)
        else:
            elems = ref_type2fields[ref_type].random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            exprs = gen_exprs_repr_ref_insts(elems, ref_type)
            return gen_elem_seg5(exprs, ref_type)


class declarativeElemSegmentGenerator:
    def_type_idx_field =  alwaysValidDiscreteValueField([3, 7], [0.5, 0.5])

    @staticmethod
    def can_insert(*args, **kwds):
        return True

    @staticmethod
    def generate_valid_one(wat_parser:WasmParser, ref_type:Optional[str]=None):
        if ref_type is None:
            ref_type = unconstrain_ref_type_field.random_valid_cvalue()
        if ref_type != 'funcref':
            def_idx = 7
        # determine def id
        func_num = wat_parser.func_num
        if func_num == 0:
            def_idx =   7
        else:
            def_idx = declarativeElemSegmentGenerator.def_type_idx_field.random_valid_cvalue()

        actual_length = unconstrain_elem_list_length_field.random_valid_cvalue(wat_parser=wat_parser)
        assert isinstance(ref_type, str)
        if func_num == 0 and ref_type == 'funcref':
            elems = _funcref_field_all_null.random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            exprs = gen_exprs_repr_ref_insts(elems, ref_type)
            return gen_elem_seg7(exprs, ref_type)

        elif def_idx == 3:
            elems = _one_funcref_field_without_null.random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            return gen_elem_seg3(elems)
        else:
            elems = ref_type2fields[ref_type].random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            exprs = gen_exprs_repr_ref_insts(elems, ref_type)
            return gen_elem_seg7(exprs, ref_type)


def _get_max_length_of_table(table_idx, wat_parser:WasmParser):
    table_length = SpecialModuleConst.CurTableLength.get_concrete_value(wat_parser, table_idx=table_idx)
    return table_length


def _get_length_for_active_elem_sec(determined_offset, wat_parser:WasmParser, table_idx=0):
    mem_length = _get_max_length_of_table(table_idx, wat_parser)
    rest_length = mem_length - determined_offset
    max_length = min(rest_length, SpecialDefConst.MaxOneElemLen.get_concrete_value())
    return max_length


def _determine_ref_type_field_for_table(wat_parser:WasmParser, table_idx:int):
    table = wat_parser.defined_table_datas[table_idx]
    return get_table_attr(table, 'val_type')


def _determine_invalid_ref_type_field_for_table(wat_parser:WasmParser, table_idx:int):
    table = wat_parser.defined_table_datas[table_idx]
    table_type = get_table_attr(table, 'val_type')
    if table_type == 'funcref':
        return 'externref'
    else:
        return 'funcref'


class activeElemSegmentGenerator:
    def_type_idx_field =  alwaysValidDiscreteValueField([0,2,4, 6], [0.25, 0.25, 0.25, 0.25])
    ref_type_field = oneGenFuncValueField(FieldFunc(_determine_ref_type_field_for_table),FieldFunc(_determine_invalid_ref_type_field_for_table))
    table_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurDefTableNum.get_concrete_value), False, True)
    offset_field = funcDeterminedRangeIntValueField(0, FieldFunc(func=_get_max_length_of_table), False, False)
    elem_list_length_field = funcDeterminedRangeIntValueField(0, FieldFunc(_get_length_for_active_elem_sec), False, False)
    
    @staticmethod
    def can_insert(wat_parser:WasmParser):
        return len(wat_parser.defined_table_datas) > 0
    
    @staticmethod
    def generate_valid_one(wat_parser:WasmParser, *args, **kwds):
        def_idx = activeElemSegmentGenerator.def_type_idx_field.random_valid_cvalue()
        
        if def_idx == 0:
            paraname2type = {'funcidxs':'funcidxs', 'offset':'offset_expr'}
            # required_filed_names = {'funcidxs', 'offset'}
        elif def_idx == 2:
            paraname2type = {'offset':'offset_expr', 'funcidxs':'funcidxs', 'table_idx':'tableidx'}
            
        elif def_idx == 4:
            paraname2type = { 'offset':'offset_expr', 'exprs':'exprs'}
        else:
            paraname2type = { 'offset':'offset_expr', 'exprs':'exprs', 'table_idx':'tableidx', 'valtype': 'valtype'}
        required_filed_names = list(paraname2type.values())
        type_repr2fields = {v:k for k, v in paraname2type.items()}
        paras = {}
        
        # for para_name, para_type in paraname2type.items():
        if 'tableidx' in required_filed_names:
            table_idx = activeElemSegmentGenerator.table_idx_field.random_valid_cvalue(wat_parser=wat_parser)
            paras[type_repr2fields['tableidx']] = table_idx
        else:
            table_idx = 0
        if 'offset_expr' in required_filed_names:
            offset = activeElemSegmentGenerator.offset_field.random_valid_cvalue(table_idx=table_idx, wat_parser=wat_parser)
            assert isinstance(offset, int), print('offset:', offset)
            paras[type_repr2fields['offset_expr']] = offset
        else:
            offset = 0
        if 'valtype' in required_filed_names:
            ref_type = activeElemSegmentGenerator.ref_type_field.random_valid_cvalue(table_idx=table_idx, wat_parser=wat_parser)
            paras[type_repr2fields['valtype']] = ref_type
        else:
            ref_type = 'funcref'
        if 'funcidxs' in required_filed_names:
            actual_length = activeElemSegmentGenerator.elem_list_length_field.random_valid_cvalue(
                determined_offset=offset, 
                wat_parser=wat_parser, 
                table_idx=table_idx)
            elems = _one_funcref_field_without_null.random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            paras[type_repr2fields['funcidxs']] = elems
        if 'exprs' in required_filed_names:
            actual_length = activeElemSegmentGenerator.elem_list_length_field.random_valid_cvalue(
                determined_offset=offset, 
                wat_parser=wat_parser, 
                table_idx=table_idx)
            elems = ref_type2fields[ref_type].random_valid_cvalue(length=actual_length, wat_parser=wat_parser)
            paras[type_repr2fields['exprs']] = gen_exprs_repr_ref_insts(elems, ref_type)
        if def_idx == 0:
            return gen_elem_seg0(**paras)
        elif def_idx == 2:
            return gen_elem_seg2(**paras)
        elif def_idx == 4:
            return gen_elem_seg4(**paras)
        else:
            return gen_elem_seg6(**paras)