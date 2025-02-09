from extract_block_mutator.InstUtil.Inst import Inst, imm_is_blocktpye
from extract_block_mutator.encode.new_defined_data_type import Blocktype
from extract_block_mutator.funcType import funcType
from extract_block_mutator.WasmParzerUtil import rewrite_special_call
from .InstGeneration.InstFactory import InstFactory
from .ModuleFuzzerUtil.global_related import generate_global_def
from .WasmParser import WasmParser
from util.prepare_template import seq_encode_seq
from .encode.byte_define.SectionPart import custom_sec_decoder, type_sec_decoder, function_sec_decoder, import_sec_decoer,  table_sec_decoder,  memory_sec_decoder,  global_sec_decoder,  export_sec_decoder,  start_sec_decoder, elem_sec_decoder,  code_sec_decoder,  data_sec_decoder, data_count_sec_decoder

str2decoder = {
    'custom': custom_sec_decoder,
    'type': type_sec_decoder,
    'function': function_sec_decoder,
    'import': import_sec_decoer,
    'table': table_sec_decoder,
    'memory': memory_sec_decoder,
    'global': global_sec_decoder,
    'export': export_sec_decoder,
    'start': start_sec_decoder,
    'element': elem_sec_decoder,
    'code': code_sec_decoder,
    'data': data_sec_decoder,
    'data_count': data_count_sec_decoder
}
def parser2wasm_core(parser: WasmParser, out_path):
    # type_sec = 
    sec_name2ba = {
        'type': parser.types,
        'function': parser.defined_func_ty_ids,
        'import': parser.imports,
        'table': parser.defined_table_datas,
        'memory': parser.defined_memory_datas,
        'global': parser.defined_globals,
        'export': parser.exports,
        'start': parser.start_sec_data,
        'element': parser.elem_sec_datas,
        'code': parser.defined_funcs,
        'data': parser.data_sec_datas,
        'data_count': parser.data_count_sec_data,
        'custom': parser.customs
    }
    sec_name2ba = {k: v for k, v in sec_name2ba.items() if v is not None}
    bas:list = []
    for encoder_name in seq_encode_seq:
    # for sec_idx in range(13):
    #     sec_name = id_name_dict[sec_idx]
        if encoder_name not in sec_name2ba:
            continue
        decoder = str2decoder[encoder_name]

        if encoder_name == 'custom':
            for custom_sec in sec_name2ba['custom']:
                ba = decoder.encode(custom_sec)
                bas.append(ba)
        else:
            # print('YYYYYYYYYYY sec_name', sec_name)
            ba = decoder.encode(sec_name2ba[encoder_name])
            bas.append(ba)
    with open(out_path, 'wb') as f:
        f.write(b'\0asm\1\0\0\0')
        for ba in bas:
            f.write(ba)
        
    


def parser2wasm(parzer:WasmParser, wasm_path):
        # 1. determine which part to change
        # 2. change
        # 3. combine the code
        # the following two variable determine which line to insert and which line to remove 
        if parzer.func0 is not None:
            rewrite_special_call(parzer)
            has_reweite = rewrite_global_lines_of_definedfunc(parzer, 0)
            if has_reweite is not None:
                parzer.defined_globals.extend(has_reweite)

        replaced_num = 0
        for func in parzer.defined_funcs:
            for inst_idx, inst in enumerate(func.insts):
                if imm_is_blocktpye(inst):
                    imm = inst.imm_part.val
                    if imm.init_with_type():
                        indicated_type:funcType = imm.init_data
                        idx = locate_func(parzer.types, indicated_type)
                        if idx is None:
                            parzer.types.append(indicated_type)
                            idx = len(parzer.types) - 1
                        # print('----------------------')
                        # print('idx', idx, 'indicated_type', indicated_type)
                        # print('parzer.types len(parzer.types)', parzer.types, len(parzer.types))
                        block_type = Blocktype(idx)
                        func.insts[inst_idx] = InstFactory.gen_binary_info_inst_high_single_imm(inst.opcode_text, block_type)
                        replaced_num += 1
        # process function section
        func_type_idxs = []
        for func in parzer.defined_funcs:
            func_type = func.func_ty
            idx = locate_func(parzer.types, func_type)
            if idx is None:
                parzer.types.append(func_type)
                idx = len(parzer.types) - 1
            func_type_idxs.append(idx)
        parzer.defined_func_ty_ids = func_type_idxs
        # process data count
        need_insert_data_count = _need_insert_data_count(parzer)
        data_seg_num = len(parzer.data_sec_datas)
        if need_insert_data_count:
            parzer.data_count_sec_data = data_seg_num
        elif data_seg_num > 0 and (parzer.data_count_sec_data is not None):
            parzer.data_count_sec_data = data_seg_num
        
                    
                
        parser2wasm_core(parzer, wasm_path)


def _need_insert_data_count(parzer:WasmParser):
    need = False
    for func in parzer.defined_funcs:
        for inst in func.insts:
            op = inst.opcode_text
            if op == 'data.drop' or op == 'memory.init':
                need = True
                break
    return need


# the memory.init and data.drop in

def locate_func(types, to_locate:funcType):
    for idx, t in enumerate(types):
        if t == to_locate:
            return idx
    return None
# def _

def insert_func_core(wasm_parzer:WasmParser, generated_func):
    wasm_parzer.defined_funcs.append(generated_func)
    has_rewrite_global = rewrite_global_lines_of_definedfunc(wasm_parzer, len(wasm_parzer.defined_funcs) - 1)
    if has_rewrite_global is not None:
        wasm_parzer.defined_globals.extend(has_rewrite_global)


def rewrite_global_lines_of_definedfunc(parzer:WasmParser, func_idx):
    has_append_global = False
    insts = parzer.defined_funcs[func_idx].insts
    for inst in insts:
        if inst.has_special_global_idx():
            has_append_global = True
            break
    if not has_append_global:
        return None
    new_global_defs = []
    unconstrained_global_imm2new_global_idx = {}
    # for idx, inst in enumerate(insts):
    for idx in range(len(insts)):
        inst:Inst = insts[idx]
        if inst.has_unconstraint_global_idx():
            if inst.imm_part not in unconstrained_global_imm2new_global_idx:
                unconstrained_global_imm2new_global_idx[inst.imm_part] =  len(parzer.defined_globals) + len(new_global_defs)
                # print('GGGGGGGGGGGGGGG inst', inst, 'inst.imm_part.type_', inst.imm_part.type_.type_)
                new_global_def = generate_global_def(True, inst.imm_part.type_)
                new_global_defs.append(new_global_def)
            # 
            ori_op = inst.opcode_text
            new_imm = unconstrained_global_imm2new_global_idx[inst.imm_part]
            new_inst = InstFactory.gen_binary_info_inst_high_single_imm(ori_op, new_imm)
            insts[idx] = new_inst
    return new_global_defs


