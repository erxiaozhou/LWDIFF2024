from .plot_util import save_tree
from ..funcType import funcType
from ..randomFuncTypeGenerator import randomFuncTypeGenerator
from ..Context import Context
from typing import List
from .util import block_grammar
from .BlockStructFuzzerOri import BlockStructFuzzerOri
from .BlockStruct2Insts import generate_insts_contain_block_under_ty_req
from ..InstGeneration.insts_generator import InstsGenerator
from ..InstUtil.Inst import Inst


def generate_insts_contain_block_under_ty_req_by_fuzzer(fuzzer:BlockStructFuzzerOri,context:Context, expected_type:funcType, insts_generator:InstsGenerator, type_generator:randomFuncTypeGenerator)->List[Inst]:
    a_strct_tree = fuzzer.init_block()
    assert a_strct_tree is not None
    fuzzer.expand_tree(a_strct_tree)
    # print('The size of the expaned tree', a_strct_tree.total_node_num())
    # save_tree(a_strct_tree, 'tt/a_strct_tree.dot')
    insts = generate_insts_contain_block_under_ty_req(a_strct_tree, context, expected_type, insts_generator, type_generator)
    return insts
