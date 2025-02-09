from ..funcType import funcType
from .block import directWasmBlock, ifWasmBlock, loopWasmBlock, blockWasmBlock, start_block_ops, mixWasmBlock
from .block import wasmBlock
from ..InstUtil.Inst import Inst
from ..InstUtil.Inst import is_if_inst
from typing import Dict, List, Tuple


class InstPosException(Exception):
    pass


def get_block_from_insts(insts: List[Inst], depths=None, types=None) -> wasmBlock:
    if types is None:
        types = []
    # assert 0
    # whether directWasmBlock
    start_line_num = 0
    end_line_num = 0
    for inst in insts:
        if inst.opcode_text in start_block_ops:
            start_line_num += 1
        if inst.opcode_text == 'end':
            end_line_num += 1
    # ! may incorrect
    
    if start_line_num != end_line_num:
        raise Exception(f'start_line_num {start_line_num} != end_line_num {end_line_num}: insts:{insts}')

    # assert start_line_num == end_line_num
    if start_line_num == 0:
        return directWasmBlock(insts=insts)
    # if ... else ... end
    if depths is None:
        depths = _init_inst_depth(insts)
    # d0_insts = [insts[i] for i in range(len(insts)) if depths[i] == 0]
    d0_insts = [insts[i] for i, d in enumerate(depths) if d == 0]
        
    if len(d0_insts) == 3 and d0_insts[1].opcode_text == 'else' and d0_insts[2].opcode_text == 'end' and is_if_inst(insts[0]):
        # get else line index
        cur_type = insts[0].imm_part.val.concrete_type(types)
        # print('cur_type 1', cur_type,insts[0])
        else_line_index = [i for i in range(
            len(insts)) if depths[i] == 0][1]
        _if_block_depths = [_ -1 for _ in depths[1:else_line_index]]
        _else_block_depths = [_ -1 for _ in depths[else_line_index+1:-1]]
        _b = ifWasmBlock.from_if_else_block(
            if_block=get_block_from_insts(insts[1:else_line_index], depths=_if_block_depths, types=types), 
            else_block=get_block_from_insts(insts[else_line_index+1:-1], depths=_else_block_depths, types=types), 
            block_type=cur_type)
        return _b
    if len(d0_insts) == 2 and d0_insts[1].opcode_text == 'end' and insts[0].opcode_text in start_block_ops:
        _depths = [_ -1 for _ in depths[1:-1]]
        cur_type = cur_type = insts[0].imm_part.val.concrete_type(types)
        # print('cur_type 2', cur_type,insts[0])
        if is_if_inst(insts[0]):
            return ifWasmBlock.from_if_block(if_block=get_block_from_insts(insts[1:-1], _depths, types=types), block_type=cur_type)
        if insts[0].opcode_text == 'block':
            return blockWasmBlock(inner_blocks=[get_block_from_insts(insts[1:-1], _depths, types=types)], block_type=cur_type)
        if insts[0].opcode_text == 'loop':
            return loopWasmBlock(inner_blocks=[get_block_from_insts(insts[1:-1], _depths, types=types)], block_type=cur_type)

    depth = 0
    blocks_insts = []
    blocks_inst_idxs = []
    cur_block_insts = []
    cur_block_inst_idxs = []
    for idx, inst in enumerate(insts):
        if inst.opcode_text in start_block_ops:
            if depth == 0:
                blocks_insts.append(cur_block_insts)
                blocks_inst_idxs.append(cur_block_inst_idxs)
                cur_block_insts = []
                cur_block_inst_idxs = []
            depth += 1
            cur_block_insts.append(inst)
            cur_block_inst_idxs.append(idx)
        elif inst.opcode_text == 'end':
            depth -= 1
            cur_block_insts.append(inst)
            cur_block_inst_idxs.append(idx)
            if depth == 0:
                blocks_insts.append(cur_block_insts)
                blocks_inst_idxs.append(cur_block_inst_idxs)
                cur_block_insts = []
                cur_block_inst_idxs = []
        else:
            cur_block_insts.append(inst)
            cur_block_inst_idxs.append(idx)
        assert depth >= 0
    assert depth == 0
    blocks_insts.append(cur_block_insts)
    blocks_inst_idxs.append(cur_block_inst_idxs)
    blocks_insts = [_ for _ in blocks_insts if _]
    blocks_inst_idxs = [_ for _ in blocks_inst_idxs if _]
    blocks = []
    for _insts, _inst_idxs in zip(blocks_insts, blocks_inst_idxs):
        _depths = [depths[_] for _ in _inst_idxs]
        blocks.append(get_block_from_insts(_insts, _depths, types=types))
    if len(blocks) == 1:
        return blocks[0]
    return mixWasmBlock(blocks)


def inst_pos2type_layers(inst_index: int, pos_log: Dict[Tuple[int], List[list[str]]]):
    for pos, layers in pos_log.items():
        if pos[0] <= inst_index < pos[1]:
            return layers
    raise InstPosException(f'inst_index {inst_index} not in pos_log {pos_log}')


def _get_cur_block_type(block: wasmBlock):
    block_type = block.block_type
    assert block_type is not None
    return block_type


def _init_inst_depth(insts):
    inst_depth_log = []
    cur_depth = 0
    for inst in insts:
        if inst.opcode_text in start_block_ops:
            inst_depth_log.append(cur_depth)
            cur_depth += 1
        elif inst.opcode_text == 'else':
            inst_depth_log.append(cur_depth-1)
        elif inst.opcode_text == 'end':
            cur_depth -= 1
            inst_depth_log.append(cur_depth)
        else:
            inst_depth_log.append(cur_depth)
        assert cur_depth >= 0
    assert cur_depth == 0
    return inst_depth_log


