from extract_block_mutator.DefShell import gen_custom_sec
from ..WasmParser import WasmParser
from .DefGenerator import common_utf8_field
from .DefGenerator import common_bytes_field

def generate_a_custom_section():
    name = common_utf8_field.random_valid_cvalue()
    random_bytes = common_bytes_field.random_valid_cvalue()
    custom_section = gen_custom_sec(name,random_bytes)
    return custom_section


def can_insrt_custom_section(wasm_parzer: WasmParser) -> bool:
    return True


def insert_custom_section(wasm_parzer: WasmParser):
    custom_section = generate_a_custom_section()
    wasm_parzer.customs.append(custom_section)


def custom_section_exist(wasm_parzer: WasmParser) -> bool:
    return len(wasm_parzer.customs) > 0



def delete_custom_section(wasm_parzer: WasmParser):
    wasm_parzer.customs = []


def rewrite_custom_section(wasm_parzer: WasmParser):
    

    custom_section = generate_a_custom_section()
    wasm_parzer.customs.pop(-1)
    wasm_parzer.customs.append(custom_section)
