from extract_block_mutator.funcTypeFactory import funcTypeFactory
from ..WasmParser import WasmParser
from ..funcType import funcType
from .DefGenerator import startSecGenerator



def can_insert_start(wasm_parser: WasmParser) -> bool:
    if wasm_parser.start_sec_data is not None:
        return False
    if len(wasm_parser.defined_funcs) == 0:
        return False
    return startSecGenerator.can_generate_valid_one(wasm_parser)


def insert_start(wasm_parser: WasmParser) -> None:
    start_sec = startSecGenerator.generate_valid_one(wasm_parser)
    wasm_parser.start_sec_data = start_sec


def can_generate_multi_valid(wasm_parser:WasmParser):
    enpry_ty = funcTypeFactory.generate_one_func_type_default([], [])
    defined_func_idxs = [idx for idx, func in enumerate(wasm_parser.defined_funcs) if func.func_ty == enpry_ty]
    return len(defined_func_idxs) > 1


def can_replace_start(wasm_parser: WasmParser) -> bool:
    if wasm_parser.start_sec_data is None:
        return False
    if len(wasm_parser.defined_funcs) == 0:
        return False
    return can_generate_multi_valid(wasm_parser)


def replace_start(wasm_parser: WasmParser) -> None:
    cur_func_idx = wasm_parser.start_sec_data 
    start_sec = startSecGenerator.generate_valid_one(wasm_parser, [cur_func_idx])
    wasm_parser.start_sec_data = start_sec
