from ..funcType import funcType
from ..randomFuncTypeGenerator import randomFuncTypeGenerator
from ..Context import Context
from typing import List
from .BlockStruct2Insts import generate_insts_contain_block_under_ty_req
from ..InstGeneration.insts_generator import InstsGenerator
from ..InstUtil.Inst import Inst


def generate_insts_contain_block_under_ty_req_by_fuzzer(fuzzer,context:Context, expected_type:funcType, insts_generator:InstsGenerator, type_generator:randomFuncTypeGenerator)->List[Inst]:
    a_strct_tree = fuzzer.init_block()
    assert a_strct_tree is not None
    fuzzer.expand_tree(a_strct_tree)
    insts = generate_insts_contain_block_under_ty_req(a_strct_tree, context, expected_type, insts_generator, type_generator)
    return insts
