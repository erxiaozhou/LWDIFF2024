from typing import Callable, List, Optional

from ..Context import Context
from .Inst import Inst
from ..funcType import funcType
from pathlib import Path
from ..typeReq import typeReq
from file_util import read_json
from ..funcTypeFactory import funcTypeFactory
from read_spec_util.SpecTypeDesc import OneInstFuncTypeDesc, desc_one_inst_full_type_part_practical

from config_inst_info import gpt_data_v2_dir

to_skip_ops = {'if', 'loop', 'block', 'else', 'end'}
expected_need_manual_ops = {'br', 'br_table', 'br_if', 'return', 'unreachable', 'call_indirect', 'call', 'ref.null'}


class InstTypeReqF:
    _all_support_inst_names = set()
    _raw_full_type_data = {}
    _full_desc_insts = set()
    _naive_single_type_inst_names = set()
    _naive_inst_name2typeReq = {}
    naive_inst_name2func_types: dict[str, list[funcType]] = {}
    _raw_op2return_num:dict[str, int] = {}
    _non_naive_inst_name2get_typeReq_func: dict[str, Callable[[Inst, Optional[Context], Optional[List[str]]], Optional[funcType]]] = {}
    _instname2functype_desc:dict[str, OneInstFuncTypeDesc] = {}
    def __init__(self, json_base_dir=gpt_data_v2_dir):
        if InstTypeReqF._need_init():
            InstTypeReqF._raw_full_type_data = _get_full_type_data_practical(json_base_dir)
            InstTypeReqF._all_support_inst_names = set(InstTypeReqF._raw_full_type_data.keys())
            InstTypeReqF._init_naive_ones()

    @staticmethod
    def just_get_type_req(inst: Inst, context_info: Optional[Context] = None, cur_params:Optional[List[str]]=None) -> Optional[typeReq]:
        opcode_text = inst.opcode_text
        
        if opcode_text in InstTypeReqF._naive_single_type_inst_names:
            return InstTypeReqF._naive_inst_name2typeReq[opcode_text]
        if cur_params is None and opcode_text in InstTypeReqF._naive_inst_name2typeReq:
            return InstTypeReqF._naive_inst_name2typeReq[opcode_text]
        if opcode_text in InstTypeReqF._non_naive_inst_name2get_typeReq_func:
            func_type =  InstTypeReqF._non_naive_inst_name2get_typeReq_func[opcode_text](inst, context_info, cur_params)
            if func_type is None:
                return None
            return typeReq([func_type])
        result = _just_get_type_req_manual(inst, context_info, cur_params)
        return result
    
    @staticmethod
    def _need_init():
        if len(InstTypeReqF._instname2functype_desc) == 0:
            return True
        return False
    @staticmethod
    def _init_naive_ones():
        for inst_name, full_type_part in InstTypeReqF._raw_full_type_data.items():
            if inst_name in expected_need_manual_ops:
                continue
            possible_spec_type_desc = desc_one_inst_full_type_part_practical(full_type_part)
            
            if possible_spec_type_desc is not None:
                InstTypeReqF._full_desc_insts.add(inst_name)
                InstTypeReqF._instname2functype_desc[inst_name] = possible_spec_type_desc
                continue
        for inst_name, inst_spec_type_desc in InstTypeReqF._instname2functype_desc.items():
            need_type_func = True
            if inst_spec_type_desc.determined_by_type_repr:
                need_type_func = False
                possible_types = inst_spec_type_desc.get_inst_type()
                InstTypeReqF._naive_inst_name2typeReq[inst_name] = typeReq(possible_types)
                InstTypeReqF.naive_inst_name2func_types[inst_name] = possible_types
                if inst_spec_type_desc.is_single_type():
                    InstTypeReqF._naive_single_type_inst_names.add(inst_name)
            return_num = inst_spec_type_desc.determined_result_num()
            if return_num is not None:
                InstTypeReqF._raw_op2return_num[inst_name] = return_num

            need_type_func = True
            if need_type_func:
                inst_type_func = inst_spec_type_desc.get_inst_type_func()
                InstTypeReqF._non_naive_inst_name2get_typeReq_func[inst_name] = inst_type_func

    @staticmethod
    def get_return_num(op):
        possible_result_num = InstTypeReqF._raw_op2return_num.get(op, None)
        if possible_result_num is None:
            raise NotImplementedError(f'op:{op} not implemented')
        else:
            return possible_result_num



def _just_get_type_req_manual(inst: Inst, context_info: Optional[Context] = None, cur_params:Optional[List[str]]=None) -> Optional[typeReq]:
    op = inst.opcode_text
    if op == 'ref.null':
        single_ty = funcTypeFactory.generate_one_func_type_default(param_type=[], result_type=[inst.imm_part.val])
        return typeReq([single_ty])
    if op == 'unreachable':
        return typeReq(
            tys=[funcTypeFactory.generate_one_func_type_default(param_type=[], result_type=[], )],
            req_type='unreachable'
        )
    if context_info is None:
        return None
    if op == 'call':
        func_idx = inst.imm_part.val
        if func_idx >= len(context_info.func_type_idxs):
            return None
        type_id = context_info.func_type_idxs[func_idx]
        req_ty = context_info.types[type_id]
        return typeReq.from_one_ty(req_ty)
    if op == 'call_indirect':
        type_idx = inst.imm_part.data['y']
        if type_idx >= len(context_info.func_type_idxs):
            return None
        single_ty = context_info.types[type_idx]
        req_ty = funcTypeFactory.generate_one_func_type_default(param_type=single_ty.param_types + ['i32'],
                        result_type=single_ty.result_types)
        return typeReq.from_one_ty(req_ty)
    if op == 'br':
        if context_info.label_types is None:
            return None
        req_ty = context_info.label_types[inst.imm_part.val]
        req_ty = funcTypeFactory.generate_one_func_type_default(req_ty, req_ty, determined_return_ty=True)
        return typeReq(
            tys=[req_ty],
            req_type='eg_param_and_result'
        )
    if op == 'br_if':
        if context_info.label_types is None:
            return None
        
        req_ty = context_info.label_types[inst.imm_part.val]
        req_ty = funcTypeFactory.generate_one_func_type_default(param_type=req_ty + ['i32'],
                        result_type=req_ty)
        return typeReq(
            tys=[req_ty],
            req_type='eg_param_f'
        )
    if op == 'return':
        req_ty = context_info.cur_func_ty
        req_ty = funcTypeFactory.generate_one_func_type_default(req_ty.result_types, req_ty.result_types, determined_return_ty=True)
        return typeReq(
            tys=[req_ty],
            req_type='eg_param_and_result'
        )
    if op == 'br_table':
        if context_info.label_types is None:
            return None
        imm_part_dict = inst.imm_part.data
        lable_idxs = imm_part_dict['l']
        if lable_idxs is None:
            lable_idxs = []
        default_label = imm_part_dict['l_N']
        l_list = lable_idxs + [default_label]

        return_types = [context_info.label_types[l] for l in l_list]
        longest_result_type = max(return_types, key=lambda x: len(x))
        for return_type in return_types:
            if longest_result_type[:len(return_type)] != return_type:
                return None
        req_tys = [funcTypeFactory.generate_one_func_type_default(longest_result_type + ['i32'],
                            longest_result_type, determined_return_ty=True)]
        
        return typeReq(
            tys=req_tys,
            req_type='eg_param_and_result'
        )
    return None



def _get_full_type_data_raw(base_dir=gpt_data_v2_dir):
    full_type_data = {}
    for p in Path(base_dir).iterdir():
        assert p.suffix == '.json'
        inst_name = p.stem
        type_part = read_json(p)['full_type_part']
        full_type_data[inst_name] = type_part
    return full_type_data


def _get_full_type_data_practical(json_base_dir)->dict[str, list[dict]]:
    _raw_full_type_data = _get_full_type_data_raw(json_base_dir)
    new_result = {}
    for inst_name, full_type_part in _raw_full_type_data.items():
        if inst_name in to_skip_ops:
            continue
        new_result[inst_name] = full_type_part
    return new_result

