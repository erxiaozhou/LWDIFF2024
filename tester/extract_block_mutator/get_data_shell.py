from typing import Optional, Union
from WasmInfoCfg import DataSegAttr, ElemSecAttr, ExportType, ImportType
from extract_block_mutator.encode.NGDataPayload import DataPayloadwithName




def get_globaltype_attr(globaltype_payload, attr_name):
    if attr_name == 'val_type':
        return globaltype_payload.data['val_type']
    if attr_name == 'mut':
        return globaltype_payload.data['mut']
    raise Exception('Not supported global type attr')


def get_global_attr(global_payload, attr_name):
    if attr_name == 'global_val_type':
        return global_payload.data['gt']['val_type']
    if attr_name == 'mut':
        return global_payload.data['gt']['mut']
    if attr_name == 'init':
        return global_payload.data['e'].value
    return global_payload.data[attr_name]

def get_func_idxs_or_null_list_from_exprs(exprs) -> list[Union[int, None]]:
    return [inst.imm_part.val if inst.opcode_text == 'ref.func' else None for inst in exprs]

def get_func_idxs_from_exprs(exprs) -> list[int]:
    func_idxs_and_null = get_func_idxs_or_null_list_from_exprs(exprs)
    return [idx for idx in func_idxs_and_null if idx is not None]

def get_func_idxs(datapayload:DataPayloadwithName) -> list[int]:
    name  = datapayload.inner_name.name
    if name == 'active_elem_seg0':
        return datapayload.data['funcidxs']
    if name == 'passive_elem_seg0':
        return datapayload.data['funcidxs']
    if name == 'active_elem_seg1':
        return datapayload.data['funcidxs']
    if name == 'declarative_elem_seg0':
        return datapayload.data['funcidxs']
    if name == 'active_elem_seg2':
        return  get_func_idxs_from_exprs(datapayload.data['exprs'])
    if name == 'passive_elem_seg1':
        return get_func_idxs_from_exprs(datapayload.data['exprs'])
    if name == 'active_elem_seg3':
        return get_func_idxs_from_exprs(datapayload.data['exprs'])
    if name == 'declarative_elem_seg1':
        return get_func_idxs_from_exprs(datapayload.data['exprs'])
    raise Exception('Not supported elem seg def')


def has_func_idx(datapayload:DataPayloadwithName) -> bool:
    func_idxs = get_func_idxs(datapayload)
    return len(func_idxs) > 0

def _get_elmseg_len(datapayload:DataPayloadwithName) -> int:
    name  = datapayload.inner_name.name
    if name == 'active_elem_seg0' or name == 'passive_elem_seg0' or name == 'active_elem_seg1' or name == 'declarative_elem_seg0':
        considered_key = 'funcidxs'
    elif name == 'active_elem_seg2' or name == 'passive_elem_seg1' or name == 'active_elem_seg3' or name == 'declarative_elem_seg1':
        considered_key = 'exprs'
    else:
        raise Exception('Not supported elem seg def')
    return len(datapayload.data[considered_key])

def get_elemseg_attr(elem_payload, attr_name):
    if attr_name == 'attr':
        def_name = elem_payload.inner_name.name 
        if def_name in {'active_elem_seg0', 'active_elem_seg1', 'active_elem_seg2', 'active_elem_seg3'}:
            return ElemSecAttr.active
        if def_name in {'passive_elem_seg0', 'passive_elem_seg1'}:
            return ElemSecAttr.passive
        if def_name in {'declarative_elem_seg0', 'declarative_elem_seg1'}:
            return ElemSecAttr.declarative
    if attr_name == 'ref_type':
        def_name = elem_payload.inner_name.name
        if def_name in {
            'active_elem_seg0', 'passive_elem_seg0', 'active_elem_seg1', 'declarative_elem_seg0', 'active_elem_seg2', 'active_elem_seg3'
        }:
            return 'funcref'
        else:
            return elem_payload.data['elemkind']
    if attr_name == 'elem_len':
        return _get_elmseg_len(elem_payload)


def get_data_attr(data_payload, attr_name):
    if attr_name == 'data':
        return data_payload.data['bytes']
    if attr_name == 'attr':
        name = data_payload.inner_name.name
        if name == 'passive_def':
            return DataSegAttr.passive
        else:
            return DataSegAttr.active
    if attr_name == 'data_len':
        return len(get_data_attr(data_payload, 'data'))


def get_export_attr(export_payload, attr_name):
    if attr_name == 'name':
        return export_payload.data['name']
    if attr_name == 'attr':
        name = export_payload.inner_name.name
        if name == 'func_exportdesc':
            return ExportType.func
        elif name == 'table_exportdesc':
            return ExportType.table
        elif name == 'mem_exportdesc':
            return ExportType.mem
        elif name == 'global_exportdesc':
            return ExportType.global_
        raise Exception('Not supported export type')
    if attr_name == 'desc':
        return export_payload.data['desc'].data['desc']
    if attr_name == 'idx':
        return export_payload.data['desc'].data['desc']
    

def get_impotr_attr(import_payload, attr_name):
    if attr_name == 'module_name':
        return import_payload.data['module']
    if attr_name == 'entity_name':
        return import_payload.data['name']
    if attr_name == 'import_attr':
        return import_payload.data['desc']
    if attr_name == 'type':
        attr_ = import_payload.data['desc']
        name = attr_.inner_name.name
        # print('name ',name)
        if name == 'func_importdesc':
            return ImportType.func
        elif name == 'table_importdesc':
            return ImportType.table
        elif name == 'mem_importdesc':
            return ImportType.mem
        elif name == 'global_importdesc':
            return ImportType.global_


def get_limit_attr(limit_payload, attr_name):
    # print('limit_payload.data', limit_payload.data)
    if attr_name == 'min':
        return limit_payload.data.get('min')
    if attr_name == 'max':
        return limit_payload.data.get('max')
    raise Exception('Not supported limit attr')

def get_memory_attr(memory_payload, attr_name):

    assert memory_payload.inner_name.name != 'memory'
    # if attr_name == 'mem_type':
    #     return memory_payload.data['mem_type']
    if attr_name == 'min' or attr_name == 'max':
        # print(type(memory_payload.data), memory_payload.data)
        return get_limit_attr(memory_payload, attr_name)
    raise Exception('Not supported memory attr')

def get_table_attr(table_payload, attr_name):
    if attr_name == 'val_type':
        return table_payload.data['et']
    if attr_name == 'lim':
        return table_payload.data['lim']
    if attr_name == 'max' or attr_name == 'min':
        limit_payload = table_payload.data['lim']
        return get_limit_attr(limit_payload, attr_name)
    raise Exception('Not supported table attr')