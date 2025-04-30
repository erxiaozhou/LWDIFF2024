from typing import List, Union
from extract_block_mutator.ModuleFuzzerUtil.ValueField import ListedField, discreteValueField

from util.get_random_type import get_random_type

from ..parser_to_file_util import insert_func_core
from ..WasmParser import WasmParser
from random import choice, choices, randint, random
from ..InstUtil.Inst import Inst, is_if_inst
from ..InstGeneration.InstFactory import InstFactory
from ..InstGeneration.insts_generator import  insts_under_ty
from ..randomFuncTypeGenerator import generate_random_funcType
from ..tool import get_func0_context_from_wasm_parser, get_func_n_context_from_wasm_parser
from ..wasmFunc import wasmFunc
from ..funcTypeFactory import funcTypeFactory


def insert_type(wasm_parser: WasmParser) -> None:
    new_type = generate_random_funcType()
    wasm_parser.types.append(new_type)


def insert_func(wasm_parser: WasmParser) -> None:
    generated_func = _generate_a_func_randomly(wasm_parser)
    insert_func_core(wasm_parser, generated_func)


gen_func_locals_field = ListedField(discreteValueField(
    ['i32', 'i64', 'f32', 'f64', 'funcref', 'externref'],
    [0.2, 0.2, 0.2, 0.2, 0.1, 0.1]))




def gen_local_seq(max_=10):
    return gen_func_locals_field.random_valid_cvalue(length=randint(0, max_))


def _generate_a_func_randomly(wasm_parser):
    new_type = generate_random_funcType()
    defined_locals = gen_local_seq()
    context = get_func0_context_from_wasm_parser(wasm_parser)
    context.cur_func_ty = new_type
    context.local_types = new_type.param_types + defined_locals
    context.label_types = [new_type.result_types]
    inst_type = funcTypeFactory.generate_one_func_type_default(param_type=[], result_type=new_type.result_types)
    insts:List[Inst] = insts_under_ty(inst_type, context)
    new_func = wasmFunc(insts=insts, defined_local_types=defined_locals, func_ty=new_type)
    return new_func


def insert_local(wasm_parser: WasmParser) -> None:
    func0:wasmFunc = wasm_parser.defined_funcs[0]
    to_insert_num= randint(1, 300)
    rand_num = random()
    consider_all = rand_num < 1 / 8
    if consider_all:
        new_locals = [get_random_type() for _ in range(to_insert_num)]
    else:
        new_locals = [get_random_type()] * to_insert_num
    func0.defined_local_types.extend(new_locals)

def can_extend_return_type(wasm_parser: WasmParser) -> bool:
    if wasm_parser.start_sec_data == 0:
        return False
    insts = wasm_parser.defined_funcs[0].insts
    has_br_table = any([inst.opcode_text == 'br_table' for inst in insts])
    if has_br_table:
        return False
    return True

def extend_return_type(wasm_parser: WasmParser):
    followed_op_types = [get_random_type() for _ in range(randint(1, 3))]
    extend_return_type_core(wasm_parser, followed_op_types)


def extend_return_type_core(parser: WasmParser, followed_op_types, func_idx=0, to_skip_inst_idxs=None):
    if to_skip_inst_idxs is None:
        to_skip_inst_idxs = []
    _func: wasmFunc = parser.defined_funcs[func_idx]
    ori_func_type = _func.func_ty
    new_func_type = funcTypeFactory.generate_one_func_type_default(ori_func_type.param_types, ori_func_type.result_types + followed_op_types)
    new_context= get_func_n_context_from_wasm_parser(parser, func_idx)
    new_context.label_types = [new_func_type.result_types]
    to_insert_insts = insts_under_ty(funcTypeFactory.generate_one_func_type_default([], followed_op_types), new_context, no_ereturn=True)
    ereturn_pos, br_if_pos = _get_to_rewrite_pos(_func.insts)
    after_br_if_ops = [x+1 for x in br_if_pos]
    poss = ereturn_pos + br_if_pos + after_br_if_ops
    poss = list(set(poss))
    poss = sorted(poss, reverse=True)
    
    before_br_if_insts = [InstFactory.opcode_inst('drop'), 
                   *to_insert_insts, 
                   InstFactory.gen_binary_info_inst_high_single_imm('i32.const', choice([0, 1]))
                   ]
    after_br_if_insts = insts_under_ty(funcTypeFactory.generate_one_func_type_default(followed_op_types, []), new_context, no_ereturn=True)
    insts = _func.insts
    poss = [x for x in poss if x not in to_skip_inst_idxs]

    for pos in poss:
        if pos in ereturn_pos:
            insts[pos:pos] = to_insert_insts
        elif pos in br_if_pos:
            insts[pos:pos] = before_br_if_insts
        if pos in after_br_if_ops:
            insts[pos:pos] = after_br_if_insts
    new_func = wasmFunc(insts, _func.defined_local_types, new_func_type)
    parser.defined_funcs[func_idx] = new_func
    
def _get_to_rewrite_pos(insts:List[Inst]):
    depth = 1
    ereturn_pos = []
    br_if_pos = []
    for idx, inst in enumerate(insts):
        if inst.opcode_text == 'return':
            ereturn_pos.append(idx)
        elif inst.opcode_text == 'br':
            if inst.imm_part.val+1 == depth:
                ereturn_pos.append(idx)
        elif inst.opcode_text == 'br_if':
            if inst.imm_part.val+1 == depth:
                br_if_pos.append(idx)
        elif inst.opcode_text in ('block', 'loop'):
            depth += 1
        elif is_if_inst(inst):
            depth += 1
        elif inst.opcode_text == 'end':
            depth -= 1
    ereturn_pos.append(len(insts))
    return ereturn_pos, br_if_pos
                