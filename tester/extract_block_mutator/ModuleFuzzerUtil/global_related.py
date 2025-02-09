from ..InstGeneration.padding_input_type import get_inst_by_require_ty_const
from .ValueField import FieldFunc, OneFuncValueField
from ..DefShell import gen_global_data, gen_global_type
from ..encode.NGDataPayload import DataPayloadwithName
from ..WasmParser import WasmParser
from WasmInfoCfg import globalValMut
from .DefGenerator import gen_a_random_globaltype



global_init_field = OneFuncValueField(FieldFunc(get_inst_by_require_ty_const))

def generate_global_def(mut=None, val_type=None):
    if isinstance(mut,  bool):
        mut = globalValMut.from_bool(mut)
    global_type: DataPayloadwithName = gen_a_random_globaltype(val_type=val_type, mut=mut)
    init_part = global_init_field.random_valid_cvalue(ty=global_type.data['val_type'])
    # global_type_data = gen_global_type(global_type, mut)
    # print('|||=', 'global_type_data', global_type_data)
    # print('|||=', 'init_part', init_part)
    return gen_global_data(global_type, init_part)

def can_insert_global(wasm_parzer: WasmParser) -> bool:
    return True


def insert_global(wasm_parzer: WasmParser) -> None:
    new_global = generate_global_def()
    # print('|||=', 'new_global', new_global)
    wasm_parzer.defined_globals.append(new_global)
