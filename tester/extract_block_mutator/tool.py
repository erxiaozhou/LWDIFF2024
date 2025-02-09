from .Context import Context
from .WasmParser import WasmParser



def get_func0_context_from_wat_parser(wasm_parzer:WasmParser):
    func_type_ids = wasm_parzer.defined_func_ty_ids
    local_types = wasm_parzer.defined_funcs[0].local_types
    types = wasm_parzer.types
    
    return Context.from_sep_paras(
        local_types=local_types,
        types=types,
        func_type_ids=func_type_ids,
        cur_func_ty=wasm_parzer.defined_funcs[0].func_ty,
        defined_globals=wasm_parzer.defined_globals,
        defined_memory_datas=wasm_parzer.defined_memory_datas,
        data_sec_datas=wasm_parzer.data_sec_datas,
        elem_sec_datas=wasm_parzer.elem_sec_datas,
        defined_table_datas=wasm_parzer.defined_table_datas,
        label_types=[wasm_parzer.func0.func_ty.result_types],
        func_idxs_in_elem=wasm_parzer.func_idxs_in_elem, 
        import_func_num=wasm_parzer.import_func_num
    )

def get_func_n_context_from_wat_parser(wasm_parzer:WasmParser, n):
    func_type_ids = wasm_parzer.defined_func_ty_ids
    local_types = wasm_parzer.defined_funcs[n].local_types
    types = wasm_parzer.types
    func_n_type = wasm_parzer.defined_funcs[n].func_ty
    return Context.from_sep_paras(
        local_types=local_types,
        types=types,
        func_type_ids=func_type_ids,
        cur_func_ty=func_n_type,
        defined_globals=wasm_parzer.defined_globals,
        defined_memory_datas=wasm_parzer.defined_memory_datas,
        data_sec_datas=wasm_parzer.data_sec_datas,
        elem_sec_datas=wasm_parzer.elem_sec_datas,
        defined_table_datas=wasm_parzer.defined_table_datas,
        label_types=[func_n_type.result_types],
        func_idxs_in_elem=wasm_parzer.func_idxs_in_elem, 
        import_func_num=wasm_parzer.import_func_num
    )




def set_parser_func_local_by_func0_context(wasm_parzer:WasmParser, context:Context, func_idx=0):
    wasm_parzer.defined_funcs[func_idx].defined_local_types = context.local_types[len(wasm_parzer.defined_funcs[func_idx].param_types):]
    # print(wasm_parzer.defined_funcs[func_idx].defined_local_types)
    wasm_parzer.defined_table_datas = context.defined_table_datas
    wasm_parzer.elem_sec_datas = context.elem_sec_datas
    wasm_parzer.data_sec_datas = context.data_sec_datas
    wasm_parzer.defined_memory_datas = context.defined_memory_datas
    wasm_parzer.types = context.types
    wasm_parzer.defined_globals = context.defined_globals
    