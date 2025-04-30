import re
import traceback
from typing import List, Dict

from extract_block_mutator.InstGeneration.InstFactory import InstFactory

from .wasm_code_text.canli_nan_funcs import get_process_nan_func
from .wasmFunc import two_func_has_same_and_inst_op, wasmFunc
from .InstUtil.SpecialImm import predefined_funca_names, predefinedFuncIdx
from .WasmParser import WasmParser



def insert_predefined_func_if_not_exist_and_get_actual_func_id(parser: WasmParser, required_predefined_func_names: List[str]) -> Dict[str, int]:
    func_name2func_idx = {}
    for func_name in required_predefined_func_names:
        assert func_name in predefined_funca_names, 'Will not process generated function here'
        expected_func = get_process_nan_func(func_name)
        func_idx = _locate_generated_func(parser.defined_funcs, expected_func)
        if func_idx is not None:
            func_name2func_idx[func_name] = func_idx
        else:
            append_func_core_base(parser, expected_func)
            func_name2func_idx[func_name] = len(parser.defined_funcs) - 1
    return func_name2func_idx


def _locate_generated_func(funcs: List[wasmFunc], generated_wasm_func: wasmFunc):
    possiple_idxs = []
    for idx, func in enumerate(funcs):
        if two_func_has_same_and_inst_op(func, generated_wasm_func):
            return idx
            possiple_idxs.append(idx)
    return None
    


def append_func_core_base(wasm_parser:WasmParser, generated_func):
    func_type = generated_func.func_ty
    type_idx = _identify_func_type_idx(wasm_parser, func_type)
    if type_idx is None:
        wasm_parser.types.append(func_type)
        type_idx = len(wasm_parser.types) - 1
    wasm_parser.defined_func_ty_ids.append(type_idx)
    wasm_parser.defined_funcs.append(generated_func)
    

def _identify_func_type_idx(wasm_parser, func_type):
    for type_idx, cur_type in enumerate(wasm_parser.types):
        if cur_type == func_type:
            return type_idx
    return None





def rewrite_special_call(parzer:WasmParser):
    func0_insts = parzer.func0_insts
    predefined_func_names = set()
    for inst in func0_insts:
        if inst.opcode_text == 'call': 
            if isinstance(inst.imm_part, predefinedFuncIdx):
                predefined_func_names.add(inst.imm_part.func_name)
    predefined_func_names = list(predefined_func_names)
    predefined_func_name2func_idx = insert_predefined_func_if_not_exist_and_get_actual_func_id(parzer,  predefined_func_names)
    
    for inst_idx in range(len(func0_insts)):
        inst = func0_insts[inst_idx]
        if inst.opcode_text == 'call':
            if isinstance(inst.imm_part, predefinedFuncIdx):
                target_func_id = predefined_func_name2func_idx[inst.imm_part.func_name]
                if inst_idx > 0 and func0_insts[inst_idx - 1].opcode_text == 'call':
                    if str(func0_insts[inst_idx - 1].imm_part) == str(target_func_id):
                        continue
                new_imm = predefined_func_name2func_idx[inst.imm_part.func_name]
                ori_op = func0_insts[inst_idx].opcode_text
                new_inst = InstFactory.gen_binary_info_inst_high_single_imm(ori_op, new_imm)
                func0_insts[inst_idx] = new_inst


