from .Context import Context
from .WasmParser import WasmParser


def get_func0_context_from_wasm_parser(wasm_parser:WasmParser):
    return get_func_n_context_from_wasm_parser(wasm_parser, 0)

def get_func_n_context_from_wasm_parser(wasm_parser:WasmParser, n):
    func_type_idxs = wasm_parser.defined_func_ty_ids
    local_types = wasm_parser.defined_funcs[n].local_types
    types = wasm_parser.types
    func_n_type = wasm_parser.defined_funcs[n].func_ty
    return Context.from_sep_paras(
        local_types=local_types.copy(),
        types=[t.copy() for t in types],
        func_type_idxs=wasm_parser.func_type_idxs,
        cur_func_ty=func_n_type,
        defined_globals=[g.copy() for g in wasm_parser.defined_globals],
        defined_memory_datas=[d.copy() for d in wasm_parser.defined_memory_datas],
        data_sec_datas=[d.copy() for d in wasm_parser.data_sec_datas],
        elem_sec_datas=[e.copy() for e in wasm_parser.elem_sec_datas],
        defined_table_datas=[t.copy() for t in wasm_parser.defined_table_datas],
        import_func_num=wasm_parser.import_func_num,
        import_global_num=wasm_parser.import_global_num,
        import_table_num=wasm_parser.import_table_num,
        import_memory_num=wasm_parser.import_memory_num,
        label_types=[func_n_type.result_types.copy()]
    )


def set_parser_func_local_by_func0_context(wasm_parser:WasmParser, context:Context, func_idx=0):
    wasm_parser.defined_funcs[func_idx].defined_local_types = context.local_types[len(wasm_parser.defined_funcs[func_idx].param_types):]
    wasm_parser.defined_table_datas = context.defined_table_datas
    wasm_parser.elem_sec_datas = context.elem_sec_datas
    wasm_parser.data_sec_datas = context.data_sec_datas
    wasm_parser.defined_memory_datas = context.defined_memory_datas
    wasm_parser.types = context.types
    wasm_parser.defined_globals = context.defined_globals
    