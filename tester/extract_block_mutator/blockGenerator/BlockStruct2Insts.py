from typing import List

from .plot_util import save_tree

from ..typeReq import merge_req, typeReq
from ..InstGeneration.insts_generator import generate_wrapper_insts_for_ty_req, InstsGenerator
from ..InstUtil import Inst
from ..Context import Context, generate_context_by_insert_label_reuse_data
from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory
from ..randomFuncTypeGenerator import randomFuncTypeGenerator
from ..blockParser import mixWasmBlock, directWasmBlock, ifWasmBlock, blockWasmBlock, loopWasmBlock, wasmBlock
from .DerivationTree import DerivationTree


EMPTY_INSTS = None

# 1. determine the type of each direct block
# 2. determine the type of each block
# 3. generate concrete instructions

def _show_blokc_tree_type(block:wasmBlock, context, prefix=''):
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
    # print('*(U*(U(())))', expected_type, cur_ty)
    pre_insts, post_insts = generate_wrapper_insts_for_ty_req(expected_type, context, cur_ty)
    # print(f'pre_insts: {pre_insts}')
    # print(f'post_insts: {post_insts}')
    # print(f'cur_ty: {cur_ty}')
    # print(f'expected_type: {expected_type}')
    return pre_insts + ori_insts + post_insts
    

def _get_insts_by_block_struct(block_struct: DerivationTree, context: Context, insts_generator:InstsGenerator,type_generator:randomFuncTypeGenerator):
    # save_tree(block_struct, './tt/ori_block_struct.dot')
    block_tree = _get_block_by_block_struct(block_struct, type_generator)
    _init_insts_for_BlockTree(block_tree, context, insts_generator)
    assert block_tree is not None
    return block_tree.as_insts(), block_tree.get_ty_req(context).ty0


def _init_insts_for_BlockTree(block_tree:wasmBlock, context: Context, insts_generator:InstsGenerator):
    if isinstance(block_tree, directWasmBlock):
        block_tree.insts = insts_generator.get_insts_with_ty(block_tree.block_type, context)
    elif isinstance(block_tree, mixWasmBlock):
        # ，。directWasmBlock。，label
        assert block_tree.inner_blocks is not None
        for block_index, block in enumerate(block_tree.inner_blocks):
            _init_insts_for_BlockTree(block, context, insts_generator)

    else:
        assert block_tree.inner_blocks is not None
        # determine new context
        block_type = block_tree.get_type(context)
        if isinstance(block_tree, loopWasmBlock):
            new_label = block_type.param_types
        else:
            # assert 0
            new_label = block_type.result_types
        new_context = generate_context_by_insert_label_reuse_data(context, new_label)
  
        # # 
        for block_index, block in enumerate(block_tree.inner_blocks):
            if block is None:
                continue
            _init_insts_for_BlockTree(block, new_context, insts_generator)

       

def _get_block_by_block_struct(block_struct: DerivationTree, type_generator:randomFuncTypeGenerator)->wasmBlock:
    # 1. generate random funcType for each dblock
    # 2. generate block_type for each block
    # do not generate concrete instructions know
    assert not block_struct.need_expansion, save_tree(block_struct, './tt/tt')
    if block_struct.name == '<program>':
        assert len(block_struct.children) == 1 and block_struct.children[0].name == '<block>'
        return _get_block_by_block_struct(block_struct.children[0], type_generator)
    if block_struct.name == '<block>':
        if len(block_struct.children) == 1:
            return _get_block_by_block_struct(block_struct.children[0], type_generator)
        inner_blocks = []
        for child_idx, child in enumerate(block_struct.children):
            # blockblock，wrapper
            new_block = _get_block_by_block_struct(child, type_generator)
            if child_idx == 0:
                inner_blocks.append(new_block)
                cur_ty_req = new_block.get_ty_req()
                continue
            else:
                new_ty_req = new_block.get_ty_req()
                merged_ty_req = merge_req(cur_ty_req, new_ty_req)
                # print('>>>>>', new_block.__class__.__name__, cur_ty_req)
                if merged_ty_req.impossible():
                    wrapper_block_type = funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].result_types, new_ty_req.tys[0].param_types)
                    # print(f'===wrapper_block_type: {wrapper_block_type}')
                    wrapper_block = directWasmBlock(insts=EMPTY_INSTS, block_type=wrapper_block_type)
                    inner_blocks.append(wrapper_block)
                    inner_blocks.append(new_block)
                    # for check
                    req0 = merge_req(cur_ty_req, typeReq.from_one_ty(wrapper_block_type))
                    req0 = merge_req(req0, new_ty_req)
                    assert typeReq.from_one_ty(funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].param_types, new_ty_req.tys[0].result_types)) == req0, print(typeReq.from_one_ty(funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].param_types, new_ty_req.tys[0].result_types)), req0)
                    cur_ty_req = typeReq.from_one_ty(funcTypeFactory.generate_one_func_type_default(cur_ty_req.tys[0].param_types, new_ty_req.tys[0].result_types))
                else:
                    inner_blocks.append(new_block)
                    cur_ty_req = merged_ty_req
            # print('----------------------------')
            # for _ in inner_blocks:
            #     print(_.get_type())
            # print('==========================')
        mix_new_block = mixWasmBlock(inner_blocks)
        # print(f'mix_new_block_type: {mix_new_block.get_type()}')
        return mix_new_block
    if block_struct.name == '<dblock>':
        assert len(block_struct.children) == 1 and block_struct.children[0].name == '<inst*>'
        return directWasmBlock(insts=EMPTY_INSTS, block_type=type_generator.generate_one())
    if block_struct.name == '<ifblock>':
        # ! if 
        if len(block_struct.children) == 1:
            ori_generated_block = _get_block_by_block_struct(block_struct.children[0], type_generator)
            if ori_generated_block.get_ty_req().ty0 == funcTypeFactory.generate_one_func_type_default([], []):
                return ifWasmBlock.from_if_block(ori_generated_block)
            else:
                wrapped_block1 = _set_if_block2_type(ori_generated_block, funcTypeFactory.generate_one_func_type_default([], []))
            return ifWasmBlock.from_if_block(wrapped_block1)
        elif len(block_struct.children) == 2:
            # ! block
            # print(f'block_struct.children: {block_struct.children}')
            block1 = _get_block_by_block_struct(block_struct.children[0], type_generator)
            block2 = _get_block_by_block_struct(block_struct.children[1],type_generator)
            block1_type = block1.get_ty_req().ty0
            block2 = _set_if_block2_type(block2, block1_type)
            return ifWasmBlock.from_if_else_block(block1, block2)
        else:
            raise Exception('ifblock children number error')
    if block_struct.name == '<lblock>':
        ori_block = _get_block_by_block_struct(block_struct.children[0], type_generator)

        
        return loopWasmBlock(inner_blocks=[ori_block])
    if block_struct.name == '<bblock>':
        return blockWasmBlock(inner_blocks=[_get_block_by_block_struct(block_struct.children[0], type_generator)])
    raise Exception('block_struct name error')

def _set_if_block2_type(ori_block2:wasmBlock, block1_type:funcType):
    block2_req_ty = ori_block2.get_ty_req().ty0
    if block1_type.param_types != block2_req_ty.param_types:
        pre_block_type = funcTypeFactory.generate_one_func_type_default(block1_type.param_types, block2_req_ty.param_types)
        pre_block = directWasmBlock(insts=EMPTY_INSTS, block_type=pre_block_type)
    else:
        pre_block = None
    if block2_req_ty.result_types != block1_type.result_types:
        post_block_type = funcTypeFactory.generate_one_func_type_default(block2_req_ty.result_types, block1_type.result_types)
        post_block = directWasmBlock(insts=EMPTY_INSTS, block_type=post_block_type)
    else:
        post_block = None
    block2_subs = [_ for _ in [pre_block, ori_block2, post_block] if _ is not None]
    if len(block2_subs) == 1:
        block2 = block2_subs[0]
    else:
        block2 = mixWasmBlock(inner_blocks=block2_subs)
    
    return block2
