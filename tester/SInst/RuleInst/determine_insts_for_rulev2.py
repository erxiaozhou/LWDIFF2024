from typing import Optional, Union, Tuple, List

from ..InstModel.PlaceHolder import ImmPH, OperandPH
from ..InstModel.SpecialOperand import RefReprVal, v1282byteseq, v128val2str
from WasmInfoCfg import non_ref_types, ref_types
from extract_block_mutator.InstGeneration.InstFactory import InstFactory
from extract_block_mutator.InstUtil.InstReqUtil import get_inst_ty_req
from extract_block_mutator.SpecialInstInputUtil.SpecialOpVal import SpecialOpVal

from ..InstModel.solver import ValConstraintSolver
from ..InstModel.OpImmValSoluiton import OpImmValSoluiton
from .RuleV2Solution import RuleV2Solution, apply_solution_to_get_concrete_pre_insts

from .RuleV2 import CSSatisfiable, RuleV2
from extract_block_mutator.Context import Context
from extract_block_mutator.funcType import funcType
from extract_block_mutator.InstUtil.Inst import Inst
from logging import Logger
from extract_block_mutator.funcTypeFactory import funcTypeFactory
from .determine_target_inst_for_rulev2 import determine_target_inst
from extract_block_mutator.InstUtil.InstReturnNumUtil import get_return_num
'''
To generate insts for a rule. Each rerule contain the constraints which cover all operands and imms for an inst
'''
# TODO target instcontext，context rule，


def generate_insts_for_rulev2_byop(rule: RuleV2, context:Context, max_local=300, logger:Optional[Logger]=None)->Tuple[Inst, List[Inst], funcType, List[Inst]]:
    # *   generate_insts_for_rule_byop ； wrap
    rule.apply_pre_func(context, [])
    if rule.need_solve:
        # print('=+++++++++++======== rule.opcode', rule.op, rule.ph_env)
        # print('RYTHRYTHKKGKKGRYTH', rule.can_apply_func)
        # print('+&*^&============================================================================')
        # print('EFWFSDFSDFSDFSDFSD', rule.raw_solve_info.im_constraints)
        # print('+&*^&============================================================================')
        val_solution: OpImmValSoluiton = ValConstraintSolver.solve_main(rule, context)
        rulev2_solution = _get_rule_v2_solution(rule, val_solution, context)
        # the second condition in the following if is to avoid solution is related to the context
        # print('TEST CACHE:XXXXXXXXXXXXXXX\n', rule.val_constraints)
        if rule.can_use_solution_cache:
            rule.val_solution = rulev2_solution
    else:
        
        # print('PERIKGKSDF      trigger cache')
        rulev2_solution = rule.val_solution
    assert rulev2_solution is not None
    pre_insts = apply_solution_to_get_concrete_pre_insts(rulev2_solution, rule.ph_env, context, max_local)
    
    target_inst:Inst = rulev2_solution.target_inst
    post_insts:List[Inst] = rulev2_solution.post_insts
    inst_type = rulev2_solution.target_and_post_type

    return target_inst,pre_insts, inst_type, post_insts



def _get_rule_v2_solution(rule:RuleV2, val_soluiton:OpImmValSoluiton, context:Context)->RuleV2Solution:
    # ph_env = rule.ph_env
    # unconstrained_ph_names = ph_env.get_unconstrained_ph_names(val_soluiton.constrained_symbol_names)
    # constrained_op_num = val_soluiton.constrained_op_num
    reset_op_idxs = val_soluiton.reset_op_idxs
    target_inst = determine_target_inst(rule, val_soluiton)
    inst_type, post_insts = _determine_inst_type(rule, context, target_inst)
    special_ops = _get_special_vals(rule, val_soluiton)
    return RuleV2Solution(target_inst, special_ops, reset_op_idxs, inst_type, post_insts)


def _get_special_vals(rule: RuleV2, val_soluiton:OpImmValSoluiton)->List[SpecialOpVal]:
    reset_op_names = val_soluiton.reset_op_names

    vals = []
    for reset_op_name in reset_op_names:
        concrete_val = val_soluiton.get_concrete_val_by_name(reset_op_name)
        op_ph = rule.ph_env.get_ph(reset_op_name)
        assert isinstance(op_ph, OperandPH)
        op_type = op_ph.ty
        if op_type in non_ref_types:
            if op_type == 'v128':
                val_str = v128val2str(concrete_val)
                toencode_val = v1282byteseq(concrete_val)
            else:
                val_str = str(concrete_val)
                toencode_val = concrete_val
            inst_ = InstFactory.gen_binary_info_inst_high_single_imm(f'{op_type}.const', toencode_val)
            special_val = SpecialOpVal(op_type, val_str, [inst_])
            vals.append(special_val)
        elif op_type in ref_types:
            assert isinstance(concrete_val, int)
            ref_repr_val = RefReprVal.from_int(concrete_val)
            # 
            if ref_repr_val == RefReprVal.extern_null:
                inst_ = InstFactory.gen_binary_info_inst_high_single_imm('ref.null', 'externref')
            elif ref_repr_val == RefReprVal.funcref_null:
                inst_ =InstFactory.gen_binary_info_inst_high_single_imm('ref.null', 'funcref')
            special_val = SpecialOpVal(op_type, 'null', [inst_])
            vals.append(special_val)
        else:
            raise NotImplementedError
    return vals


def _determine_inst_type(rule: RuleV2, context:Context, target_inst:Inst)->Tuple[funcType, List[Inst]]:
    if rule.illegal_type:
        raise NotImplementedError('Not implemented yet')
    else:
        # print('target_inst', target_inst)
        type_req = get_inst_ty_req(target_inst, context, rule.operand_types)
        # assert type_req is not None, print('rule.operand_types', rule.operand_types, 'target_inst', target_inst)
        if type_req is not None:
            if len(type_req.tys) == 1:
                inst_type = type_req.ty0
                post_insts = []
            else:
                raise NotImplementedError(f'Not implemented yet noerf: {rule.operand_types}, {target_inst}, {type_req}')
            inst_type = type_req.ty0
            post_insts = []
        else:
            # assert 0
            input_params = rule.operand_types
            inst_type = funcTypeFactory.generate_one_func_type_default(input_params, [])
            return_num = get_return_num(rule.raw_op_name)
            if return_num == 0:
                post_insts = []
            else:
                
                post_insts = [InstFactory.opcode_inst('drop')] * return_num
        return inst_type, post_insts
