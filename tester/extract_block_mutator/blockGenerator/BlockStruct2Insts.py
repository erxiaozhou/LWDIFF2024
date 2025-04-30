from typing import List

from ..typeReq import merge_req, typeReq
from ..InstGeneration.insts_generator import generate_wrapper_insts_for_ty_req, InstsGenerator
from ..InstUtil import Inst
from ..Context import Context, generate_context_by_insert_label_reuse_data
from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory
from ..randomFuncTypeGenerator import randomFuncTypeGenerator
from ..blockParser import MixWasmBlock, DirectWasmBlock, IfWasmBlock, BlockWasmBlock, LoopWasmBlock, WasmBlock
from .DerivationTree import DerivationTree


EMPTY_INSTS = None


def _show_blokc_tree_type(block:WasmBlock, context, prefix=''):
    print(f'{block.__class__.__name__} type: {block.get_type(context)}')
    print('>==', prefix)
    if block.inner_blocks is None:
        return
    
    for _ in block.inner_blocks:
        if _ is None:
            continue
        _show_blokc_tree_type(_, context, prefix+'<<>>')


def generate_insts_contain_block_under_ty_req(block_struct: DerivationTree, context: Context, expected_type:funcType, insts_generator:InstsGenerator,type_generator:randomFuncTypeGenerator)->List[Inst]:
    ori_insts, cur_ty = _get_insts_by_block_struct(block_struct, context, insts_generator,type_generator)

    pre_insts, post_insts = generate_wrapper_insts_for_ty_req(expected_type, context, cur_ty)

    return pre_insts + ori_insts + post_insts
    

def _get_insts_by_block_struct(block_struct: DerivationTree, context: Context, insts_generator:InstsGenerator,type_generator:randomFuncTypeGenerator):

    block_tree = _get_block_by_block_struct(block_struct, type_generator)
    _init_insts_for_BlockTree(block_tree, context, insts_generator)
    assert block_tree is not None
    return block_tree.as_insts(), block_tree.get_ty_req(context).ty0


def _init_insts_for_BlockTree(block_tree:WasmBlock, context: Context, insts_generator:InstsGenerator):
    if isinstance(block_tree, DirectWasmBlock):
        block_tree.insts = insts_generator.get_insts_with_ty(block_tree.block_type, context)
    elif isinstance(block_tree, MixWasmBlock):
        
        assert block_tree.inner_blocks is not None
        for block_index, block in enumerate(block_tree.inner_blocks):
            _init_insts_for_BlockTree(block, context, insts_generator)

    else:
        assert block_tree.inner_blocks is not None
        block_type = block_tree.get_type(context)
        if isinstance(block_tree, LoopWasmBlock):
            new_label = block_type.param_types
        else:
            new_label = block_type.result_types
        new_context = generate_context_by_insert_label_reuse_data(context, new_label)
  
        for block_index, block in enumerate(block_tree.inner_blocks):
            if block is None:
                continue
            _init_insts_for_BlockTree(block, new_context, insts_generator)

       

def _get_block_by_block_struct(block_struct: DerivationTree, type_generator:randomFuncTypeGenerator)->WasmBlock:
    if block_struct.name == '<program>':
        assert len(block_struct.children) == 1 and block_struct.children[0].name == '<block>'
        return _get_block_by_block_struct(block_struct.children[0], type_generator)
    if block_struct.name == '<block>':
        if len(block_struct.children) == 1:
            return _get_block_by_block_struct(block_struct.children[0], type_generator)
        inner_blocks = []
        for child_idx, child in enumerate(block_struct.children):
            
            new_block = _get_block_by_block_struct(child, type_generator)
            if child_idx == 0:
                inner_blocks.append(new_block)
                cur_ty_req = new_block.get_ty_req()
                continue
            else:
                new_ty_req = new_block.get_ty_req()
                merged_ty_req = merge_req(cur_ty_req, new_ty_req)
                if merged_ty_req.impossible():
                    wrapper_block_type = funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].result_types, new_ty_req.tys[0].param_types)
                    wrapper_block = DirectWasmBlock(insts=EMPTY_INSTS, block_type=wrapper_block_type)
                    inner_blocks.append(wrapper_block)
                    inner_blocks.append(new_block)
                    req0 = merge_req(cur_ty_req, typeReq.from_one_ty(wrapper_block_type))
                    req0 = merge_req(req0, new_ty_req)
                    assert typeReq.from_one_ty(funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].param_types, new_ty_req.tys[0].result_types)) == req0, print(typeReq.from_one_ty(funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].param_types, new_ty_req.tys[0].result_types)), req0)
                    cur_ty_req = typeReq.from_one_ty(funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].param_types, new_ty_req.tys[0].result_types))
                else:
                    inner_blocks.append(new_block)
                    cur_ty_req = merged_ty_req
        mix_new_block = MixWasmBlock(inner_blocks)
        return mix_new_block
    if block_struct.name == '<dblock>':
        assert len(block_struct.children) == 1 and block_struct.children[0].name == '<inst*>'
        return DirectWasmBlock(insts=EMPTY_INSTS, block_type=type_generator.generate_one())
    if block_struct.name == '<ifblock>':
        if len(block_struct.children) == 1:
            ori_generated_block = _get_block_by_block_struct(block_struct.children[0], type_generator)
            if ori_generated_block.get_ty_req().ty0 == funcTypeFactory.generate_one_func_type_default([], []):
                return IfWasmBlock.from_if_block(ori_generated_block)
            else:
                wrapped_block1 = _set_if_block2_type(ori_generated_block, funcTypeFactory.generate_one_func_type_default([], []))
            return IfWasmBlock.from_if_block(wrapped_block1)
        elif len(block_struct.children) == 2:
            block1 = _get_block_by_block_struct(block_struct.children[0], type_generator)
            block2 = _get_block_by_block_struct(block_struct.children[1],type_generator)
            block1_type = block1.get_ty_req().ty0
            block2 = _set_if_block2_type(block2, block1_type)
            return IfWasmBlock.from_if_else_block(block1, block2)
        else:
            raise Exception('ifblock children number error')
    if block_struct.name == '<lblock>':
        ori_block = _get_block_by_block_struct(block_struct.children[0], type_generator)

        
        return LoopWasmBlock(inner_blocks=[ori_block])
    if block_struct.name == '<bblock>':
        return BlockWasmBlock(inner_blocks=[_get_block_by_block_struct(block_struct.children[0], type_generator)])
    raise Exception('block_struct name error')

def _set_if_block2_type(ori_block2:WasmBlock, block1_type:funcType):
    block2_req_ty = ori_block2.get_ty_req().ty0
    if block1_type.param_types != block2_req_ty.param_types:
        pre_block_type = funcTypeFactory.generate_one_func_type_default(block1_type.param_types, block2_req_ty.param_types)
        pre_block = DirectWasmBlock(insts=EMPTY_INSTS, block_type=pre_block_type)
    else:
        pre_block = None
    if block2_req_ty.result_types != block1_type.result_types:
        post_block_type = funcTypeFactory.generate_one_func_type_default(block2_req_ty.result_types, block1_type.result_types)
        post_block = DirectWasmBlock(insts=EMPTY_INSTS, block_type=post_block_type)
    else:
        post_block = None
    block2_subs = [_ for _ in [pre_block, ori_block2, post_block] if _ is not None]
    if len(block2_subs) == 1:
        block2 = block2_subs[0]
    else:
        block2 = MixWasmBlock(inner_blocks=block2_subs)
    
    return block2
