from extract_block_mutator.funcTypeFactory import funcTypeFactory
from ..WasmParser import WasmParser
from ..funcType import funcType
from .DefGenerator import startSecGenerator



def can_insert_start(wasm_parzer: WasmParser) -> bool:
    if wasm_parzer.start_sec_data is not None:
        return False
    if len(wasm_parzer.defined_funcs) == 0:
        return False
    return startSecGenerator.can_generate_valid_one(wasm_parzer)


def insert_start(wasm_parzer: WasmParser) -> None:
    start_sec = startSecGenerator.generate_valid_one(wasm_parzer)
    wasm_parzer.start_sec_data = start_sec


def can_generate_multi_valid(wasm_parzer:WasmParser):
    enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
    defined_func_idxs = [idx for idx, func in enumerate(wasm_parzer.defined_funcs) if func.func_ty == enpry_ty]
    return len(defined_func_idxs) > 1


def can_replace_start(wasm_parzer: WasmParser) -> bool:
    if wasm_parzer.start_sec_data is None:
        return False
    if len(wasm_parzer.defined_funcs) == 0:
        return False
    return can_generate_multi_valid(wasm_parzer)


def replace_start(wasm_parzer: WasmParser) -> None:
    cur_func_idx = wasm_parzer.start_sec_data 
    start_sec = startSecGenerator.generate_valid_one(wasm_parzer, [cur_func_idx])
    wasm_parzer.start_sec_data = start_sec
