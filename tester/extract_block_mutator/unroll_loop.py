from typing import Optional
from .InstGeneration.InstFactory import InstFactory
from .funcType import funcType
from .blockParser import wasmBlock, directWasmBlock, mixWasmBlock, loopWasmBlock, blockWasmBlock
from .InstGeneration.padding_input_type import padding_input_type
from .funcTypeFactory import funcTypeFactory


# * assume the instructions are initialized
def unroll_loop(loop_block:loopWasmBlock, loop_block_type:funcType, new_context):
    assert isinstance(loop_block, loopWasmBlock)
    inner_block = loop_block.inner_blocks[0].copy()
    # br1_block = dire
    _reset_depth_related_insts(inner_block, 0)
    exec_block_inner = mixWasmBlock([inner_block, directWasmBlock(insts=[InstFactory.gen_binary_info_inst_high_single_imm('br', 1)], block_type=funcTypeFactory.generate_one_func_type_default(loop_block_type.result_types, loop_block_type.result_types))])
    exec_block = blockWasmBlock([exec_block_inner], block_type=loop_block_type)
    # 
    loop_block = loop_block.copy()
    _reset_depth_related_insts(loop_block, 0)  # loop，+1
    # 
    if loop_block_type.result_types == loop_block_type.param_types:
        new_inner_blocks = [exec_block, loop_block]
    else:
        # type combine instructions
        new_func_type = funcTypeFactory.generate_one_func_type_default(loop_block_type.result_types, loop_block_type.param_types)
        combine_insts_block = generate_directWasmBlock_with_type(new_func_type, new_context)

        new_inner_blocks = [exec_block, combine_insts_block, loop_block]
    unroll_block_inner = mixWasmBlock(new_inner_blocks, block_type=loop_block_type)
    unroll_block = blockWasmBlock([unroll_block_inner], block_type=loop_block_type)
    return unroll_block


def generate_directWasmBlock_with_type(new_func_type:funcType, context=None)->directWasmBlock:
    combine_insts = padding_input_type(new_func_type.param_types, new_func_type.result_types, context)
    return directWasmBlock(insts=combine_insts, block_type=new_func_type)
    


def _reset_depth_related_insts(block: Optional[wasmBlock], depth:int):
    if block is None:
        return
    if isinstance(block, directWasmBlock):
        ori_insts = block.insts
        assert ori_insts is not None
        for inst_idx, inst in enumerate(ori_insts):
            if inst.opcode_text == 'br' or inst.opcode_text == 'br_if':
                # new_inst
                ori_layer_index = inst.imm_part.val
                if ori_layer_index >= depth:
                    new_imm_part = str(ori_layer_index + 1)
                    new_inst = InstFactory.gen_binary_info_inst_high_single_imm(inst.opcode_text, new_imm_part)
                    ori_insts[inst_idx] = new_inst
            if inst.opcode_text == 'br_table':
                imm_repr = inst.imm_part
                layer_idxs = imm_repr.split(' ')
                layer_idxs = [int(idx) for idx in layer_idxs]
                for i, layer_idx in enumerate(layer_idxs):
                    if layer_idx >= depth:
                        layer_idxs[i] = layer_idx + 1
                new_imm_part = ' '.join([str(idx) for idx in layer_idxs])
                new_inst = InstFactory.gen_binary_info_inst_high_single_imm(inst.opcode_text, new_imm_part)
                ori_insts[inst_idx] = new_inst

            # TODO BR_TABLE
    else:
        if isinstance(block, mixWasmBlock):
            new_depth = depth
        else:
            new_depth = depth + 1
        inner_blocks = block.inner_blocks
        assert inner_blocks is not None
        for inner_block in inner_blocks:
            _reset_depth_related_insts(inner_block, new_depth)
    

def unroll_loop_result_check(unrolled_block):
    assert isinstance(unrolled_block, blockWasmBlock)
    assert unrolled_block.inner_blocks is not None
    assert isinstance(unrolled_block.inner_blocks[0], mixWasmBlock)
    assert len(unrolled_block.inner_blocks[0].inner_blocks) in [2, 3]
    assert unrolled_block.inner_blocks[0].inner_blocks is not None
    assert isinstance(unrolled_block.inner_blocks[0].inner_blocks[0], blockWasmBlock)
    assert isinstance(unrolled_block.inner_blocks[0].inner_blocks[-1], loopWasmBlock)
    if len(unrolled_block.inner_blocks[0].inner_blocks) == 3:
        assert isinstance(unrolled_block.inner_blocks[0].inner_blocks[1], directWasmBlock)
# * assume the instructions are initialized
# * only unroll a part of the loop
