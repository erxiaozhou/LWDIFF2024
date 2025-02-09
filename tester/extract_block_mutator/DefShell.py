from typing import Optional, Union
from extract_block_mutator.InstGeneration.InstFactory import InstFactory
from extract_block_mutator.InstUtil.ByteInst import ByteImmInst
from extract_block_mutator.InstUtil.Inst import Inst
from extract_block_mutator.encode.NGDataPayload import DataPayloadwithName



def gen_global_type(val_type, mut) -> DataPayloadwithName:
    return DataPayloadwithName({'val_type': val_type, 'mut': mut}, 'globaltype')


def get_offset_inst_from_int(i)->ByteImmInst:
    assert isinstance(i, int), f'Expect int, but got {type(i)}'
    inst = InstFactory.gen_binary_info_inst_high_single_imm('i32.const', i)
    return inst

def gen_offset_expr_from_int(i) -> DataPayloadwithName:
    assert isinstance(i, int), f'Expect int XX, but got {type(i)}'
    inst = get_offset_inst_from_int(i)
    return DataPayloadwithName({'expr': inst}, 'Expr')


def gen_global_data(global_type, init: Inst) -> DataPayloadwithName:
    expr_init = DataPayloadwithName({'expr': init}, 'Expr')
    return DataPayloadwithName(
        {'gt': global_type, 'e': expr_init},
        'GlobalData'
    )


def gen_mem_from_limit(limit: DataPayloadwithName) -> DataPayloadwithName:
    # maybe useless
    return limit


def gen_limit1(min_: int) -> DataPayloadwithName:
    return DataPayloadwithName({'min': min_}, 'limits_without_max')

def gen_limit2(min_: int, max_: int) -> DataPayloadwithName:
    return DataPayloadwithName({'min': min_, 'max': max_}, 'limits_with_max')

def gen_limit(min_, max_: Optional[int] = None):
    # if max_v is not None and min_v > max_v:
    #     min_v, max_v = max_v, min_v
    # return DataPayloadwithName
    if max_ is None:
        limit_ = gen_limit1(min_)
    else:
        limit_ = gen_limit2(min_, max_)
    return limit_


def gen_table_type(elem_type, limit: DataPayloadwithName) -> DataPayloadwithName:
    return DataPayloadwithName({'et': elem_type, 'lim': limit}, 'tabletype')


def  gen_export_funcidx_part(func_idx):
    return DataPayloadwithName({'desc': func_idx}, 'func_exportdesc')


def gen_export_tableidx_part(table_idx):
    return DataPayloadwithName({'desc': table_idx}, 'table_exportdesc')


def gen_export_memidx_part(memory_idx):
    return DataPayloadwithName({'desc': memory_idx}, 'mem_exportdesc')


def gen_export_desc(name, desc):
    return DataPayloadwithName({'name': name, 'desc': desc}, 'export')



def gen_export_global_idx_part(global_idx):
    return DataPayloadwithName({'desc': global_idx}, 'global_exportdesc')


def rename_export_desc(export_desc, new_name):
    payload = export_desc.data.copy()
    payload['name'] = new_name
    return DataPayloadwithName(payload, 'export')


def gen_func_import_attr(type_idx):
    return DataPayloadwithName({'typeidx': type_idx}, 'func_importdesc')

def gen_table_import_attr(table_type):
    return DataPayloadwithName({'tabletype': table_type}, 'table_importdesc')

def gen_memory_import_attr(memory_type):
    return DataPayloadwithName({'memtype': memory_type}, 'mem_importdesc')

def gen_global_import_attr(global_type):
    return DataPayloadwithName({'gt': global_type}, 'global_importdesc')

def gen_import_desc(module_name, entity_name, import_attr) -> DataPayloadwithName:
    return DataPayloadwithName(
        data={
            'module': module_name,
            'name': entity_name,
            'desc': import_attr
        },
        name='import'
    )


def gen_passive_data_seg(data) -> DataPayloadwithName:
    return DataPayloadwithName({'bytes': data}, 'passive_def')

def gen_active_data_seg0(data, init) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'bytes': data,
            'expression': gen_offset_expr_from_int(init)
            }, 
        'active_memory_zero')

def gen_active_data_seg1(data, init, mem_idx) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'bytes': data,
            'memory_index': mem_idx,
            'expression': gen_offset_expr_from_int(init)
            }, 
        'active_memory_index')


def gen_elem_seg0(funcidxs, offset) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'funcidxs': funcidxs,
            'offset': gen_offset_expr_from_int(offset)
        },
        'active_elem_seg0'
    )
# passive
def gen_elem_passive0(funcidxs) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'funcidxs': funcidxs,
            'elemkind': 'funcref'
        },
        'passive_elem_seg0'
    )

def gen_elem_seg2(table_idx, offset, funcidxs) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'table_idx': table_idx,
            'offset': gen_offset_expr_from_int(offset),
            'funcidxs': funcidxs,
            'elemkind': 'funcref'
        },
        'active_elem_seg1'
    )

# decl
def gen_elem_decl0(funcidxs) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'funcidxs': funcidxs,
            'elemkind': 'funcref'
        },
        'declarative_elem_seg0'
    )

def gen_elem_seg4(offset, exprs) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'offset': gen_offset_expr_from_int(offset),
            'exprs': exprs
        },
        'active_elem_seg2'
    )
# passive
def gen_elem_passive1(exprs, valtype) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'elemkind': valtype,
            'exprs': exprs
        },
        'passive_elem_seg1'
    )

def gen_elem_seg6(table_idx, offset, exprs, valtype) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'tableidx': table_idx,
            'offset': gen_offset_expr_from_int(offset),
            'exprs': exprs,
            'elemkind': valtype
        },
        'active_elem_seg3'
    )

# decl
def gen_elem_decl1(exprs, valtype) -> DataPayloadwithName:
    return DataPayloadwithName(
        {
            'exprs': exprs,
            'elemkind': valtype
        },
        'declarative_elem_seg1'
    )

def gen_exprs_repr_ref_insts(func_idxs_or_null_list:list[Union[int, None]], ref_type) -> list[Inst]:
    if ref_type == 'externref':
        assert all([idx is None for idx in func_idxs_or_null_list])
    return [InstFactory.gen_binary_info_inst_high_single_imm('ref.func', idx) if idx is not None else InstFactory.gen_binary_info_inst_high_single_imm('ref.null', ref_type) for idx in func_idxs_or_null_list]

def gen_custom_sec(name, data) -> DataPayloadwithName:
    # ! I  know there will be an Exception, since the process of section_length
    return DataPayloadwithName(data={
        'custom': DataPayloadwithName(
            data={
                'name': name,
                'payload': data
            },
            name='custom'
        )
        }, name='custom_section')

