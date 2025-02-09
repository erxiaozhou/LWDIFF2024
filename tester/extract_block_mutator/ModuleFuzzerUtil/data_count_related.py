from ..WasmParser import WasmParser
from ..specialConst import SpecialModuleConst
from .DefGenerator import data_count_field

def can_apply_insert_data_count(wasm_parzer:WasmParser) -> bool:
    return wasm_parzer.data_count_sec_data is None


def insert_data_count(wasm_parzer:WasmParser):
    wasm_parzer.data_count_sec_data = generate_valid_data_count_section(wasm_parzer) 


def generate_valid_data_count_section(wasm_parzer:WasmParser):
    data_count = data_count_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
    return data_count
