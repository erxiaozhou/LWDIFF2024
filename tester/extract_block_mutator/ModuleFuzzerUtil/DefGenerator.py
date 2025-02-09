from random import choice, randint
from typing import Any, Optional
from WasmInfoCfg import globalValMut, val_type_strs_list 
from extract_block_mutator.get_data_shell import get_table_attr

from ..DefShell import gen_active_data_seg0, gen_active_data_seg1, gen_export_desc, gen_exprs_repr_ref_insts, gen_global_type, gen_limit, gen_limit1, gen_limit2, gen_mem_from_limit, gen_passive_data_seg, gen_table_type, get_offset_inst_from_int
from ..DefShell import gen_export_funcidx_part
from ..DefShell import gen_export_tableidx_part
from ..DefShell import gen_export_memidx_part
from ..DefShell import gen_export_global_idx_part
from ..DefShell import gen_elem_passive0, gen_elem_passive1, gen_elem_seg2, gen_elem_decl0, gen_elem_seg4, gen_elem_seg0, gen_elem_seg6, gen_elem_decl1


from .util import gen_random_bytes, generate_random_utf8_str

from ..WasmParser import WasmParser
from .ValueField import ComibedField, OneFuncValueField, ValueField, ListedField, discreteValueField, funcDeterminedRangeIntValueField, keyConditionField
from .ValueField import FieldFunc
from ..specialConst import SpecialDefConst, SpecialModuleConst, specialContextConst
from ..funcTypeFactory import funcTypeFactory
from ..encode.NGDataPayload import DataPayloadwithName
# memory ==========================================================
def _cur_num_or_0(cur_num:int=0):
    return max(0, cur_num)

# def _

class Limit1Gen(ValueField):
    def __init__(self, min_field:ValueField):
        self.min_gen = min_field

    def random_valid_cvalue(self, *args, **kwds):
        min_ = self.min_gen.random_valid_cvalue(*args, **kwds)
        return gen_limit1(min_)

class Limit2Gen(ValueField):
    def __init__(self, min_field:ValueField, max_field:ValueField):
        self.min_gen = min_field
        self.max_gen = max_field

    def random_valid_cvalue(self, *args, **kwds):
        min_ = self.min_gen.random_valid_cvalue(*args, **kwds)
        max_ = self.max_gen.random_valid_cvalue(*args, **kwds)
        if min_ > max_:
            max_ = min_
        return gen_limit2(min_, max_)


class LimitGen:
    def __init__(self, min_gen:ValueField, max_gen:ValueField):
        # self.limit1_gen = limit1_gen
        # self.limit2_gen = limit2_gen
        limit1_gen = Limit1Gen(min_gen)
        limit2_gen = Limit2Gen(min_gen, max_gen)
        self.gen = ComibedField([limit1_gen, limit2_gen], [0.5, 0.5])
        
    def random_valid_cvalue(self, *args, **kwds):
        return self.gen.random_valid_cvalue(*args, **kwds)


valid_mem_min_field = funcDeterminedRangeIntValueField(FieldFunc(_cur_num_or_0), SpecialDefConst.MaxMinMemPages.get_concrete_value(),False, False)
valid_mem_max_field = funcDeterminedRangeIntValueField(FieldFunc(_cur_num_or_0), SpecialDefConst.CommonMaxMemPages.get_concrete_value(),False, False)
valid_mem_limit_gen = LimitGen(valid_mem_min_field, valid_mem_max_field)


class memDescGenerator:
    @staticmethod
    def generate_valid_one(cur_num:Optional[int]=None)->DataPayloadwithName:
        return valid_mem_limit_gen.random_valid_cvalue(cur_num=cur_num)





# table ==========================================================
class tableLimitGenerator:
    valid_min_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.MaxMinTableLen.get_concrete_value(),False, False)
    valid_max_field = ComibedField(
        [
            funcDeterminedRangeIntValueField(0, SpecialDefConst.CommonMaxTableLen.get_concrete_value(),False, False),
            discreteValueField([None])
        ],
        [0.5, 0.5]
    )

    @staticmethod
    def generate_valid_one()->DataPayloadwithName:
        min_v = tableLimitGenerator.valid_min_field.random_valid_cvalue()
        max_v = tableLimitGenerator.valid_max_field.random_valid_cvalue()
        if max_v is not None and min_v > max_v:
            min_v, max_v = max_v, min_v
        return gen_limit(min_v, max_v)




valid_table_min_field = funcDeterminedRangeIntValueField(FieldFunc(_cur_num_or_0), SpecialDefConst.MaxMinTableLen.get_concrete_value(),False, False)
valid_table_max_field = funcDeterminedRangeIntValueField(FieldFunc(_cur_num_or_0), SpecialDefConst.CommonMaxTableLen.get_concrete_value(),False, False)
valid_table_limit_gen = LimitGen(valid_table_min_field, valid_table_max_field)
unconstrain_ref_type_field = discreteValueField(['funcref', 'externref'], [0.7, 0.3])



class oneTableDescGenerator:
    
    @staticmethod
    def generate_valid_one(target_type:Optional[str]=None,  min_limit:int=0)->DataPayloadwithName:
        limit: DataPayloadwithName = valid_table_limit_gen.random_valid_cvalue(cur_num=min_limit)
        table_type = unconstrain_ref_type_field.random_valid_cvalue(required=target_type)
        return gen_table_type(table_type, limit)


# start ======================================================

def _valid_start_func_candis_candis(wasm_parzer:WasmParser, skip_idxs=None) -> int:
    if skip_idxs is None:
        skip_idxs = []
    enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
    defined_func_idxs = [idx for idx, func in enumerate(wasm_parzer.defined_funcs) if (func.func_ty == enpry_ty) and (idx not in skip_idxs)]
    # assert len(defined_func_idxs) > 0
    if len(defined_func_idxs) == 0:
        raise ValueError(f'no valid start func: skip_idxs:{skip_idxs}; func_num: {wasm_parzer.func_num} {startSecGenerator.can_generate_valid_one(wasm_parzer)}')
    return choice(defined_func_idxs)



class startSecGenerator:
    idx_field = OneFuncValueField(FieldFunc(_valid_start_func_candis_candis))

    @staticmethod
    def can_generate_valid_one(wasm_parzer:WasmParser):
        enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
        for func in wasm_parzer.defined_funcs:
            if func.func_ty== enpry_ty:
                return True
        return False


    @staticmethod
    def generate_valid_one(wasm_parzer: WasmParser, skip_idxs=None):
        idx = startSecGenerator.idx_field.random_valid_cvalue(wasm_parzer=wasm_parzer, skip_idxs=skip_idxs)
        return idx

# data count
data_count_field = OneFuncValueField(FieldFunc(SpecialModuleConst.CurDataSegNum.get_concrete_value))

# data ======================================================


def _get_length_for_active_data_sec(determined_offset, wasm_parzer:WasmParser, memory_idx=0):
    mem_length = SpecialModuleConst.CurMemLen.get_concrete_value(memory_idx=memory_idx, wasm_parzer=wasm_parzer)
    rest_length = mem_length - determined_offset
    max_length = min(rest_length, SpecialDefConst.CommonMaxDataLen.get_concrete_value())
    return max_length

data_field = OneFuncValueField(FieldFunc(gen_random_bytes))
active_data_offset_field = funcDeterminedRangeIntValueField(0, FieldFunc(func=SpecialModuleConst.CurMemLen.get_concrete_value), False, False)
actual_length_field = funcDeterminedRangeIntValueField(0, FieldFunc(_get_length_for_active_data_sec), False, False)
mem_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurDefMemNum.get_concrete_value),False, True)


class activeDataDef0Gen(ValueField):
    def __init__(self):
        pass
    
    def random_valid_cvalue(self, wasm_parzer:WasmParser) -> Any:
        offset = active_data_offset_field.random_valid_cvalue(memory_idx=0, wasm_parzer=wasm_parzer)
        actual_length = activeDataSegmentGenerator.actual_length_field.random_valid_cvalue(
            determined_offset=offset,
            wasm_parzer=wasm_parzer,
            memory_idx=0
        )
        data = data_field.random_valid_cvalue(length=actual_length)
        return gen_active_data_seg0(data, init=offset)

class activeDataDef1Gen(ValueField):
    def __init__(self):
        pass
        
    def random_valid_cvalue(self, wasm_parzer:WasmParser) -> Any:
        memory_idx = mem_idx_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
        offset = active_data_offset_field.random_valid_cvalue(memory_idx=memory_idx, wasm_parzer=wasm_parzer)
        actual_length = activeDataSegmentGenerator.actual_length_field.random_valid_cvalue(
            determined_offset=offset,
            wasm_parzer=wasm_parzer,
            memory_idx=memory_idx
        )
        data = data_field.random_valid_cvalue(length=actual_length)
        return gen_active_data_seg1(data, offset, memory_idx)
        

class activeDataSegmentGenerator:
    def_type_idx_field =  discreteValueField([0, 1], [0.5, 0.5])
    mem_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurDefMemNum.get_concrete_value),False, True)
    offset_fileld = funcDeterminedRangeIntValueField(0, FieldFunc(func=SpecialModuleConst.CurMemLen.get_concrete_value), False, False)  #
    actual_length_field = funcDeterminedRangeIntValueField(0, FieldFunc(_get_length_for_active_data_sec), False, False)
    gen_main = ComibedField(
        [
            activeDataDef0Gen(),
            activeDataDef1Gen()
        ],
        [0.5, 0.5]
    )
    
    @staticmethod
    def can_insert(wasm_parzer:WasmParser):
        return len(wasm_parzer.defined_memory_datas) > 0
    
    @staticmethod
    def generate_valid_one(wasm_parzer:WasmParser):
    # @staticmethod
    # def generate_valid_one(wasm_parzer:WasmParser):
        def_ = activeDataSegmentGenerator.gen_main.random_valid_cvalue(wasm_parzer=wasm_parzer)
        return def_
        

actual_passive_data_length_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.CommonMaxDataLen.get_concrete_value(), False, False)



class passiveDataDef0Gen(ValueField):
    def __init__(self):
        pass
    
    def random_valid_cvalue(self, *args, **kwds) -> Any:
        actual_length = actual_passive_data_length_field.random_valid_cvalue()
        data = data_field.random_valid_cvalue(length=actual_length)
        return gen_passive_data_seg(data)

class passiveDataSegmentGenerator:
    gen_main = passiveDataDef0Gen()
    # ! ，
    
    @staticmethod
    def can_insert(*args, **kwds):
        return True
    
    @staticmethod
    def generate_valid_one():
        return passiveDataSegmentGenerator.gen_main.random_valid_cvalue()
    

# elem ===================================================================================
# 1.  all func idx
# 2.  all none 
# 3. 

_one_externref_field = discreteValueField([None])

_one_funcref_field_with_null = ComibedField(
    [
        funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurFuncNum.get_concrete_value), False, True),
        discreteValueField([None])
    ],
    [0.8, 0.2]
)



funcidx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurFuncNum.get_concrete_value), False, True)
funcidxs_field= ListedField(funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurFuncNum.get_concrete_value), False, True))


elem_exprs_field = keyConditionField({
    'funcref': ListedField(_one_funcref_field_with_null),
    'externref': ListedField(_one_externref_field)
})

unconstrain_elem_list_length_field = funcDeterminedRangeIntValueField(0, SpecialDefConst.MaxOneElemLen.get_concrete_value(), False, False)



class passiveElemDef0Gen(ValueField):
    def __init__(self):
        pass
    def random_valid_cvalue(self, *args, **kwds):
        actual_length = unconstrain_elem_list_length_field.random_valid_cvalue()
        elems = funcidxs_field.random_valid_cvalue(length=actual_length, wasm_parzer=kwds.get('wasm_parzer'))
        return gen_elem_passive0(elems)

class passiveElemDef1Gen(ValueField):
    def __init__(self):
        pass
    def random_valid_cvalue(self, *args, **kwds):
        ref_type = unconstrain_ref_type_field.random_valid_cvalue(required=kwds.get('ref_type'))
        actual_length = unconstrain_elem_list_length_field.random_valid_cvalue()
        elems = elem_exprs_field.random_valid_cvalue(length=actual_length, key=ref_type, wasm_parzer=kwds.get('wasm_parzer'))
        exprs = gen_exprs_repr_ref_insts(elems, ref_type)
        return gen_elem_passive1(exprs, ref_type)


passive_elem_gen0 = passiveElemDef0Gen()
passive_elem_gen1 = passiveElemDef1Gen()

passive_elem_gen = ComibedField(
    [
        passive_elem_gen0,
        passive_elem_gen1
    ],
    [0.5, 0.5]
)

class passiveElemSegmentGenerator:
    def_type_idx_field =  discreteValueField([1, 5], [0.5, 0.5])
    @staticmethod
    def can_insert(*args, **kwds):
        return True

    @staticmethod
    def generate_valid_one(wasm_parzer:WasmParser, ref_type:Optional[str]=None):
        if ref_type == 'externref':
            result =  passive_elem_gen1.random_valid_cvalue(wasm_parzer=wasm_parzer, ref_type=ref_type)
        else:
            result = passive_elem_gen.random_valid_cvalue(wasm_parzer=wasm_parzer)
        # print(' PPPP result:', result)
        return result


class declElemDef0Gen(ValueField):
    def __init__(self):
        pass
    def random_valid_cvalue(self, *args, **kwds):
        actual_length = unconstrain_elem_list_length_field.random_valid_cvalue()
        elems = funcidxs_field.random_valid_cvalue(length=actual_length, wasm_parzer=kwds.get('wasm_parzer'))
        return gen_elem_decl0(elems)

class declElemDef1Gen(ValueField):
    def __init__(self):
        pass
    def random_valid_cvalue(self, *args, **kwds):
        ref_type = unconstrain_ref_type_field.random_valid_cvalue(required=kwds.get('ref_type'))
        actual_length = unconstrain_elem_list_length_field.random_valid_cvalue()
        elems = elem_exprs_field.random_valid_cvalue(length=actual_length, key=ref_type, wasm_parzer=kwds.get('wasm_parzer'))
        exprs = gen_exprs_repr_ref_insts(elems, ref_type)
        return gen_elem_decl1(exprs, ref_type)


decl_elem_gen0 = declElemDef0Gen()
decl_elem_gen1 = declElemDef1Gen()
decl_elem_gen = ComibedField(
    [
        decl_elem_gen0,
        decl_elem_gen1
    ],
    [0.5, 0.5]
)



class declarativeElemSegmentGenerator:
    def_type_idx_field =  discreteValueField([1, 5], [0.5, 0.5])
    @staticmethod
    def can_insert(*args, **kwds):
        return True

    @staticmethod
    def generate_valid_one(wasm_parzer:WasmParser, ref_type:Optional[str]=None):
        if ref_type == 'externref':
            return decl_elem_gen1.random_valid_cvalue(wasm_parzer=wasm_parzer, ref_type=ref_type)
        return decl_elem_gen.random_valid_cvalue(wasm_parzer=wasm_parzer)


def _get_length_for_active_elem_sec(determined_offset, wasm_parzer:WasmParser, table_idx=0):
    mem_length = SpecialModuleConst.CurTableLength.get_concrete_value(table_idx=table_idx, wasm_parzer=wasm_parzer)
    rest_length = mem_length - determined_offset
    max_length = min(rest_length, SpecialDefConst.MaxOneElemLen.get_concrete_value())
    return max_length


def _determine_ref_type_field_for_table(wasm_parzer:WasmParser, table_idx:int):
    table = wasm_parzer.defined_table_datas[table_idx]
    return get_table_attr(table, 'val_type')


table_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(func=SpecialModuleConst.CurDefTableNum.get_concrete_value), False, True)

class activeElemSegmentGenerator:
    def_type_idx_field =  discreteValueField([0,2,4, 6], [0.25, 0.25, 0.25, 0.25])
    ref_type_field = OneFuncValueField(FieldFunc(_determine_ref_type_field_for_table))
    offset_field = funcDeterminedRangeIntValueField(0, FieldFunc(func=SpecialModuleConst.CurTableLength.get_concrete_value), False, False)
    elem_list_length_field = funcDeterminedRangeIntValueField(0, FieldFunc(_get_length_for_active_elem_sec), False, False)
    
    @staticmethod
    def can_insert(wasm_parzer:WasmParser):
        return len(wasm_parzer.defined_table_datas) > 0
    
    @staticmethod
    def generate_valid_one(wasm_parzer:WasmParser, *args, **kwds):
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
            table_idx = table_idx_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
            paras[type_repr2fields['tableidx']] = table_idx
        else:
            table_idx = 0
        if 'offset_expr' in required_filed_names:
            offset = activeElemSegmentGenerator.offset_field.random_valid_cvalue(table_idx=table_idx, wasm_parzer=wasm_parzer)
            assert isinstance(offset, int), print('offset:', offset)
            paras[type_repr2fields['offset_expr']] = offset
        else:
            offset = 0
        if 'valtype' in required_filed_names:
            ref_type = activeElemSegmentGenerator.ref_type_field.random_valid_cvalue(table_idx=table_idx, wasm_parzer=wasm_parzer)
            paras[type_repr2fields['valtype']] = ref_type
        else:
            ref_type = 'funcref'
        if 'funcidxs' in required_filed_names:
            actual_length = activeElemSegmentGenerator.elem_list_length_field.random_valid_cvalue(
                determined_offset=offset, 
                wasm_parzer=wasm_parzer, 
                table_idx=table_idx)
            elems = funcidxs_field.random_valid_cvalue(length=actual_length, wasm_parzer=wasm_parzer)
            paras[type_repr2fields['funcidxs']] = elems
        if 'exprs' in required_filed_names:
            actual_length = activeElemSegmentGenerator.elem_list_length_field.random_valid_cvalue(
                determined_offset=offset, 
                wasm_parzer=wasm_parzer, 
                table_idx=table_idx)
            elems = elem_exprs_field.random_valid_cvalue(length=actual_length, key=ref_type, wasm_parzer=wasm_parzer)
            paras[type_repr2fields['exprs']] = gen_exprs_repr_ref_insts(elems, ref_type)
        # print('VVVVVVVVVVVV paras:', paras, ';;;; def_idx:', def_idx)
        if def_idx == 0:
            return gen_elem_seg0(**paras)
        elif def_idx == 2:
            return gen_elem_seg2(**paras)
        elif def_idx == 4:
            return gen_elem_seg4(**paras)
        else:
            return gen_elem_seg6(**paras)


class Utf8Field(ValueField):
    def __init__(self, min_length:int, max_length:int):
        self.min_length = min_length
        self.max_length = max_length
    
    def random_valid_cvalue(self, *args, **kwds):
        length = randint(self.min_length, self.max_length)
        return generate_random_utf8_str(length)

common_utf8_field = Utf8Field(0, 60)



class bytesField(ValueField):
    def __init__(self, min_length:int, max_length:int):
        self.min_length = min_length
        self.max_length = max_length
    
    def random_valid_cvalue(self, *args, **kwds):
        length = randint(self.min_length, self.max_length)
        return gen_random_bytes(length)
common_bytes_field = bytesField(0, 256)



val_type_field = discreteValueField(val_type_strs_list)
global_mut_field = discreteValueField([globalValMut.Mut, globalValMut.Const], [0.5, 0.5])


class GlobalTypeField:
    def __init__(self):
        pass
    def random_valid_cvalue(self, *args, val_type=None, mut=None, **kwds):
        if val_type is None:
            val_type = val_type_field.random_valid_cvalue()
        if mut is None:
            mut = global_mut_field.random_valid_cvalue()
        # assert isinstance(mut, globalValMut), print('mut:', mut)
        # assert isinstance(val_type, str), print('val_type:', val_type)
        return gen_global_type(val_type, mut)

globaltype_field = GlobalTypeField()



def gen_a_random_globaltype(val_type=None, mut=None) -> DataPayloadwithName:
    return globaltype_field.random_valid_cvalue(val_type=val_type, mut=mut)

# export ==========================================================

global_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurGlobalNum.get_concrete_value), False, True)
table_idx_field = funcDeterminedRangeIntValueField(0, FieldFunc(SpecialModuleConst.CurDefTableNum.get_concrete_value), False, True)


class ExportFunidxGen:
    def __init__(self):
        pass
    
    def random_valid_cvalue(self, wasm_parzer:WasmParser):
        func_idx = funcidx_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
        return gen_export_funcidx_part(func_idx)
class ExportTableidxGen:
    def __init__(self):
        pass
    def random_valid_cvalue(self, wasm_parzer:WasmParser):
        table_idx = table_idx_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
        return gen_export_tableidx_part(table_idx)
class ExportMemidxGen:
    def __init__(self):
        pass
    def random_valid_cvalue(self, wasm_parzer:WasmParser):
        mem_idx = mem_idx_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
        return gen_export_memidx_part(mem_idx)
class ExportGlobalidxGen:
    def __init__(self):
        pass
    def random_valid_cvalue(self, wasm_parzer:WasmParser):
        global_idx = global_idx_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
        return gen_export_global_idx_part(global_idx)

export_memidx_field = ExportMemidxGen()
export_tableidx_field = ExportTableidxGen()
export_funidx_field = ExportFunidxGen()
export_globalidx_field = ExportGlobalidxGen()

class ExportIdxGen:
    def __init__(self):
        pass
    
    def random_valid_cvalue(self, wasm_parzer:WasmParser):
        generated_ones = []
        if SpecialModuleConst.CurFuncNum.get_concrete_value(wasm_parzer=wasm_parzer) > 0:
            generated_ones.append(export_funidx_field.random_valid_cvalue(wasm_parzer=wasm_parzer))
        if SpecialModuleConst.CurTableNum.get_concrete_value(wasm_parzer=wasm_parzer) > 0:
            generated_ones.append(export_tableidx_field.random_valid_cvalue(wasm_parzer=wasm_parzer))
        if SpecialModuleConst.CurMemNum.get_concrete_value(wasm_parzer=wasm_parzer) > 0:
            generated_ones.append(export_memidx_field.random_valid_cvalue(wasm_parzer=wasm_parzer))
        if SpecialModuleConst.CurGlobalNum.get_concrete_value(wasm_parzer=wasm_parzer) > 0:
            generated_ones.append(export_globalidx_field.random_valid_cvalue(wasm_parzer=wasm_parzer))
        return choice(generated_ones)

export_idx_desc_field = ExportIdxGen()

# class ExportDescGen:
#     def __init__(self):
#         pass
#     def

import_attr_field = keyConditionField(
    {
        'table':oneTableDescGenerator.generate_valid_one,
        'memory':memDescGenerator.generate_valid_one,
        'global':globaltype_field, 
        'func':funcidx_field
    }
)

