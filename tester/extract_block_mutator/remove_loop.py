from typing import Optional
from .blockParser import wasmBlock, loopWasmBlock, directWasmBlock
from .unroll_loop import generate_directWasmBlock_with_type


def remove_loop(block_tree:Optional[wasmBlock]):
    if block_tree is None:
        return None
    if isinstance(block_tree, loopWasmBlock):
        assert block_tree.block_type is not None
        new_block = generate_directWasmBlock_with_type(block_tree.block_type)
        return new_block
    if isinstance(block_tree, directWasmBlock):
        return block_tree
    # if 
    # if isinstance(block_tree, wasmBlock):
    # assert block_tree
    assert block_tree.inner_blocks is not None
    assert len(block_tree.inner_blocks) >= 1
    for block_idx, inneer_block in enumerate(block_tree.inner_blocks):
        block_tree.inner_blocks[block_idx] = remove_loop(inneer_block)
    return block_tree
