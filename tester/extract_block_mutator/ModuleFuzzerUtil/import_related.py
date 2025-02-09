from extract_block_mutator.DefShell import gen_import_desc
from extract_block_mutator.ModuleFuzzerUtil.ValueField import discreteValueField

from ..WasmParser import WasmParser

from .DefGenerator import common_utf8_field, import_attr_field


support_import_types = ['global', 'table', 'memory', 'func']
import_type_field = discreteValueField(support_import_types)

def gen_import_desc_(wasm_parzer: WasmParser):
    import_module_name = common_utf8_field.random_valid_cvalue()
    import_entity_name = common_utf8_field.random_valid_cvalue()
    
    import_attr_type =import_type_field.random_valid_cvalue()
    import_attr = import_attr_field.random_valid_cvalue(key=import_attr_type, wasm_parzer=wasm_parzer)
    import_desc = gen_import_desc(import_module_name, import_entity_name, import_attr)
    return import_desc
    

def insert_import(wasm_parzer: WasmParser):
    import_desc = gen_import_desc_(wasm_parzer)
    wasm_parzer.imports.append(import_desc)
