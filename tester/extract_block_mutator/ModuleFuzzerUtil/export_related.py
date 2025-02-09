from extract_block_mutator.ModuleFuzzerUtil.ValueField import ValueField
from ..DefShell import rename_export_desc
from ..DefShell import gen_export_desc
from ..get_data_shell import get_export_attr
from ..WasmParser import WasmParser
from random import randint, random, shuffle
from .DefGenerator import common_utf8_field
from .DefGenerator import export_idx_desc_field


def can_insert_export(parser:WasmParser):
    if len(parser.defined_globals) == 0 and parser.defined_memory_num == 0 and len(parser.defined_table_datas) == 0 and len(parser.defined_funcs) == 0:
        return False
    return True


def gen_export_name(wasm_parser: WasmParser):
    export_names = [get_export_attr(export, 'name') for export in wasm_parser.exports] # type: ignore
    export_names:set[str] = set(export_names)
    max_try_num = 10
    final_name = None
    for _ in range(max_try_num):
        final_name = common_utf8_field.random_valid_cvalue()
        if final_name not in export_names:
            break
    # if final_name is None:
    assert final_name is not None
    return final_name



class ExportDescGen(ValueField):
    def __init__(self):
        pass
    
    def random_valid_cvalue(self, wasm_parzer:WasmParser):
        export_name = gen_export_name(wasm_parzer)
        export_idx = export_idx_desc_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
        return gen_export_desc(export_name, export_idx)

export_desc_field = ExportDescGen()



def insert_export(wasm_parzer: WasmParser):
    export_desc = export_desc_field.random_valid_cvalue(wasm_parzer=wasm_parzer)
    wasm_parzer.exports.append(export_desc)

def _generate_new_bytes(ori_str, to_skip_bytes):
    new_char = chr(randint(0, 0x7f))
    while ori_str  in to_skip_bytes:
        if random() < 0.5:
            ori_str = ori_str + new_char
        else:
            ori_str = new_char
    return ori_str


def can_apply_rewrite_export_name(parser:WasmParser):
    if  len(parser.exports) == 0:
        return False
    return True


def rewrite_export_name(parser:WasmParser):
    existing_field_bytes = []
    for export in parser.exports:
        cur_name = get_export_attr(export, 'name')
        existing_field_bytes.append(cur_name)

    export_idx2name = {}
    for i in range(2):
        to_rename_idx = randint(0, len(existing_field_bytes) - 1)
        to_rename = existing_field_bytes[to_rename_idx]
        to_rename = _generate_new_bytes(to_rename, existing_field_bytes)
        export_idx2name[to_rename_idx] = to_rename 
        # existing_field_bytes.append(to_rename)
    for export_idx, new_name in export_idx2name.items():
        # print(f'export_idx: {export_idx}, len(parser.exports) : {len(parser.exports)} : {len(existing_field_bytes)}')
        export = parser.exports[export_idx]
        new_export = rename_export_desc(export, new_name)
        parser.exports[export_idx] = new_export
