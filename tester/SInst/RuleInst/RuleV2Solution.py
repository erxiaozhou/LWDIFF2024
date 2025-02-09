from typing import Optional, List
from extract_block_mutator.SpecialInstInputUtil.SpecialOpVal import SpecialOpVal

from extract_block_mutator.SpecialInstInputUtil.insts_for_reset_op_util import generate_insts_for_byop, reverse_op_idxs

from ..InstModel.PHEnv import PHEnv
from extract_block_mutator.Context import Context
from extract_block_mutator.funcType import funcType
from extract_block_mutator.InstUtil.Inst import Inst


class RuleV2Solution:
    def __init__(self,
                 target_inst: Inst,
                 special_vals: List[SpecialOpVal],
                 reset_op_idxs:List[int],
                 target_and_post_type: funcType,
                 post_insts: Optional[List[Inst]] = None
                 ):
        self.target_inst = target_inst
        self.special_vals = special_vals
        self.reset_op_idxs = reset_op_idxs
        self.target_and_post_type = target_and_post_type
        if post_insts is None:
            post_insts = []
        self.post_insts = post_insts

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.target_inst}, {self.special_vals}, {self.reset_op_idxs}, {self.target_and_post_type}, {self.post_insts})'


def apply_solution_to_get_concrete_pre_insts(rulev2_solution:RuleV2Solution,
                                         ph_env:PHEnv,
                                        context:Context,
                                        max_local=300
                                        # insts:List[Inst]
                                        )->List[Inst]:
    reset_op_idxs = rulev2_solution.reset_op_idxs
    operand_types = ph_env.get_operand_types()
    special_vals = rulev2_solution.special_vals
    # ! not sure the next line
    operand_types, reset_op_idxs = reverse_op_idxs(operand_types, reset_op_idxs)
    pre_insts = generate_insts_for_byop(context, max_local, special_vals, operand_types, reset_op_idxs)
    # raise NotImplementedError
    return pre_insts
