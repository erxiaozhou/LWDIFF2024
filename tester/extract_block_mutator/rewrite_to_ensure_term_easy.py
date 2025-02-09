from WasmInfoCfg import globalValMut
from WasmInfoCfg import i32
from extract_block_mutator.DefShell import gen_global_data, gen_global_type
from extract_block_mutator.encode.new_defined_data_type import Blocktype
from extract_block_mutator.funcTypeFactory import funcTypeFactory
from .InstGeneration.InstFactory import InstFactory
from .InstUtil.Inst import Inst
from typing import List
from .WasmParser import WasmParser


def _cur_pos_is_wrapped(insts:List[Inst]):
    assert len(insts) == 9
    expected_ops = ['global.get', 'i32.eqz', 'if', 'unreachable', 'end', 'global.get', 'i32.const', 'i32.sub', 'global.set']
    for idx, inst in enumerate(insts):
        if inst.opcode_text != expected_ops[idx]:
            return False
    return True

def _determine_the_global_utilized(insts:List[Inst]):
    if len(insts) < 10:
        return None
    if insts[0].opcode_text != 'loop':
        return None
    for inst in insts[1:10]:
        if not _cur_pos_is_wrapped(insts[1:10]):
            return None
    idx = insts[1].imm_part.val
    return idx


def _determine_the_global_utilized_in_all_insts(insts:List[Inst]):
    global_idx = None
    for inst_idx, inst in enumerate(insts[:-9]):
        _g = _determine_the_global_utilized(insts[inst_idx:inst_idx+10])
        if _g is not None:
            global_idx = _g
            break
    return global_idx


def _determine_loop_pos_to_rewrite(insts:List[Inst]):
    pass
    poss = []
    if len(insts) <= 10:
        return poss
    for inst_idx, inst in enumerate(insts[:-9]):
        if inst.opcode_text == 'loop':
            if not _cur_pos_is_wrapped(insts[inst_idx+1:inst_idx+10]):
                poss.append(inst_idx)
    return poss

def _determine_wraped_pos(insts:List[Inst]):
    pass
    poss = []
    if len(insts) <= 10:
        return poss
    for inst_idx, inst in enumerate(insts[:-9]):
        if inst.opcode_text == 'loop':
            if _cur_pos_is_wrapped(insts[inst_idx+1:inst_idx+10]):
                poss.append(inst_idx)
    return poss

def _rewrite_new_insts_and_utilized_global_in_ori_insts(ori_insts, new_insts, target_global_idx):
    all_loop_poss_in_ori_insts = [idx for idx, inst in enumerate(ori_insts) if inst.opcode_text == 'loop']
    wrapped_pos_in_ori_insts = set(_determine_wraped_pos(ori_insts))

    # 
    ensure_term_insts_followed = [
        InstFactory.gen_binary_info_inst_high_single_imm('global.get', target_global_idx),
        InstFactory.opcode_inst('i32.eqz'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], []))),
        InstFactory.opcode_inst('unreachable'),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('global.get', target_global_idx),
        InstFactory.gen_binary_info_inst_high_single_imm('i32.const', 1),
        InstFactory.opcode_inst('i32.sub'),
        InstFactory.gen_binary_info_inst_high_single_imm('global.set', target_global_idx),
    ]
    # 

    for pos in all_loop_poss_in_ori_insts[::-1]:
        if pos in wrapped_pos_in_ori_insts:
            ori_insts[pos+1:pos+2] = [InstFactory.gen_binary_info_inst_high_single_imm('global.get', target_global_idx)]
            ori_insts[pos+6:pos+7] = [InstFactory.gen_binary_info_inst_high_single_imm('global.get', target_global_idx)]
            ori_insts[pos+9:pos+10] = [InstFactory.gen_binary_info_inst_high_single_imm('global.set',target_global_idx)]
        # else:

            # ori_insts[pos:pos+1] = [ori_insts[pos]]
            # ori_insts[pos+1:pos+1] = ensure_term_insts_followed
            
    # 
    all_loop_poss_in_new_insts = [idx for idx, inst in enumerate(new_insts) if inst.opcode_text == 'loop']
    poss_to_insert = set(_determine_loop_pos_to_rewrite(new_insts))
    for pos in all_loop_poss_in_new_insts[::-1]:
        if pos in poss_to_insert :
            new_insts[pos:pos+1] = [new_insts[pos]]
            new_insts[pos+1:pos+1] = ensure_term_insts_followed

            
    return ori_insts, new_insts


def _determine_global_idx_to_ensure_term(parser: WasmParser, insts:List[Inst]):
    global_type = gen_global_type('i32', globalValMut.from_bool(True))
    new_global = gen_global_data(global_type, InstFactory.gen_binary_info_inst_high_single_imm('i32.const', 100))
    parser.defined_globals.append(new_global)
    utilized_global_idx = len(parser.defined_globals) - 1
    return utilized_global_idx

def reweite_to_ensure_term_easy(parser: WasmParser, ori_insts, to_rewrite_insts:List[Inst]):
    target_global_idx = _determine_global_idx_to_ensure_term(parser, ori_insts)
    # print('ori insts size', len(ori_insts), 'to rewrite insts size', len(to_rewrite_insts))
    _rewrite_new_insts_and_utilized_global_in_ori_insts(ori_insts, to_rewrite_insts, target_global_idx)
    # print('ori insts size', len(ori_insts), 'to rewrite insts size', len(to_rewrite_insts))
