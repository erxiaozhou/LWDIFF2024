from .tool import _get_cur_block_type
from ..funcType import funcType
from .block import directWasmBlock, ifWasmBlock, loopWasmBlock, blockWasmBlock, mixWasmBlock
from .block import wasmBlock
from ..InstUtil import Inst
from typing import Dict, List, Tuple


def inst_pos2type_layers_for_insert(inst_index: int, pos_log_for_insert: Dict[Tuple[int], List[List[str]]]):
    for pos,layers in pos_log_for_insert.items():
        if pos[0] <= inst_index <= pos[1]:
            return layers
    raise ValueError(f'inst_index: {inst_index} not in pos_log_for_insert: {pos_log_for_insert}')



def generate_inst_pos2type_layers_for_insert(block_tree: wasmBlock) -> Dict[Tuple[int], List[List[str]]]:
    #  if else end block loopfuncType
    if isinstance(block_tree, directWasmBlock):
        # print('directWasmBlock')
        return {(0, block_tree.inst_num()): []}
    if isinstance(block_tree, blockWasmBlock):
        inner_block = block_tree.inner_blocks[0]
        inner_block_ty2insts = generate_inst_pos2type_layers_for_insert(inner_block)
        insts2ty = {}
        min_start = 0
        max_end = inner_block.inst_num() + 2
        for inst_slot, inner_block_ty in inner_block_ty2insts.items():
            inst_slot = (inst_slot[0]+1, inst_slot[1]+1)
            cur_block_type:list[str] = _get_cur_block_type(block_tree).result_types
            new_block_ty = inner_block_ty + [cur_block_type]
            insts2ty[inst_slot] = new_block_ty
        insts2ty[(min_start, min_start)] = []
        insts2ty[(max_end, max_end)] = []
        return insts2ty
    if isinstance(block_tree, loopWasmBlock):
        inner_block = block_tree.inner_blocks[0]
        inner_block_ty2insts = generate_inst_pos2type_layers_for_insert(inner_block)
        insts2ty = {}
        min_start = 0
        max_end = inner_block.inst_num() + 2
        for inst_slot, inner_block_ty in inner_block_ty2insts.items():
            inst_slot = (inst_slot[0]+1, inst_slot[1]+1)
            cur_block_type:list[str] = _get_cur_block_type(block_tree).param_types
            new_block_ty = inner_block_ty + [cur_block_type]
            insts2ty[inst_slot] = new_block_ty
        insts2ty[(min_start, min_start)] = []
        insts2ty[(max_end, max_end)] = []
        return insts2ty
    if isinstance(block_tree, ifWasmBlock):
        block0 = block_tree.inner_blocks[0]
        inner_block_ty2insts = generate_inst_pos2type_layers_for_insert(block0)
        insts2ty = {}
        insts2ty[(0, 0)] = []
        for inst_slot, inner_block_ty in inner_block_ty2insts.items():
            inst_slot = (inst_slot[0]+1, inst_slot[1]+1)
            cur_block_type = _get_cur_block_type(block_tree).result_types
            new_block_ty = inner_block_ty + [cur_block_type]
            insts2ty[inst_slot] = new_block_ty
        block0_length = block0.inst_num()
        block1 = block_tree.inner_blocks[1]
        if block1 is None:
            insts2ty[(block0_length+2, block0_length+2)] = []
            return insts2ty
        inner_block_ty2insts = generate_inst_pos2type_layers_for_insert(block1)
        offset = block0_length + 2
        for inst_slot, inner_block_ty in inner_block_ty2insts.items():
            # print('niksndnoonmnompm')
            inst_slot = (inst_slot[0]+offset, inst_slot[1]+offset)
            cur_block_type = _get_cur_block_type(block_tree).result_types
            new_block_ty = inner_block_ty + [cur_block_type]
            # print(inst_slot, 'inst_slot')
            # print(new_block_ty, 'new_block_ty')
            insts2ty[inst_slot] = new_block_ty
        block1_length = block1.inst_num()
        max_end = block0_length + block1_length + 3
        insts2ty[(max_end, max_end)] = []
        # insts2ty[(offset, offset)] = []
        return insts2ty
    if isinstance(block_tree, mixWasmBlock):
        children_length = [_.inst_num() for _ in block_tree.inner_blocks]
        insts2ty = {}
        start = 0
        for child_index, child in enumerate(block_tree.inner_blocks):
            child_ty2insts = generate_inst_pos2type_layers_for_insert(child)
            for inst_slot, child_ty in child_ty2insts.items():
                inst_slot = (inst_slot[0]+start, inst_slot[1]+start)
                insts2ty[inst_slot] = child_ty
            start += children_length[child_index]
        insts2ty[(start, start)] = []
        return insts2ty