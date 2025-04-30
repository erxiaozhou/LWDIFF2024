from ..WasmParser import WasmParser
from ..SpecialConst import SpecialModuleConst
from .DefGenerator import data_count_field

def can_apply_insert_data_count(wasm_parser:WasmParser) -> bool:
    return wasm_parser.data_count_sec_data is None


def insert_data_count(wasm_parser:WasmParser):
    wasm_parser.data_count_sec_data = generate_valid_data_count_section(wasm_parser) 


def generate_valid_data_count_section(wasm_parser:WasmParser):
    data_count = data_count_field.random_valid_cvalue(loader=wasm_parser)
    return data_count
