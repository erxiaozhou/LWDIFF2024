from typing import Any, List, Optional

from extract_block_mutator.encode.byte_define.DecoderID import PartDescMemory
from extract_block_mutator.encode.byte_define.structure_decoder import StructuredDecoder

from ..InstModel.Exceptions import UNSolveException
from ..InstModel.PHEnv import PHEnv
from ..InstModel.PlaceHolder import ImmPH
from ..InstModel.SpecialOperand import HeapTypeVal, ImmTypeVal, v1282byteseq, v128val2str

from extract_block_mutator.InstGeneration.InstFactory import InstFactory

from ..InstModel.solver import ValConstraintSolver
from ..InstModel.OpImmValSoluiton import OpImmValSoluiton

from .RuleV2 import CSSatisfiable, RuleV2
from extract_block_mutator.Context import Context
from extract_block_mutator.InstUtil.Inst import Inst


'''
To generate insts for a rule. Each rerule contain the constraints which cover all operands and imms for an inst
'''
# TODO target instcontext，context rule，


def just_get_target_inst_for_rulev2(rule: RuleV2, context:Optional[Context])->Optional[Inst]:
    # assue the rule is appliable
    try:
        val_solution: OpImmValSoluiton = ValConstraintSolver.solve_main(rule, context)
        target_inst = determine_target_inst(rule, val_solution)
    except UNSolveException:
        if rule.satisfiable == CSSatisfiable.SATISFIABLE:
            raise ValueError(f'Constraints are unsatisfiable:{rule.op} ;; {rule.val_constraints}, {context}')
        else:
            # print(f'DEBUGINFO: {rule.val_constraints}, {context}')
            target_inst = None
    return target_inst


def determine_target_inst(rule: RuleV2, val_solution: OpImmValSoluiton)->Inst:
    # print('BIDFNVPPF[CDSV]', val_solution)
    ph_env = rule.ph_env
    if not rule.need_determine_target_inst():
        target_inst = rule.target_inst
        assert target_inst is not None
        return target_inst
    else:
        imm_reprs = _get_imm_reprs(val_solution, ph_env)
        if len(imm_reprs) <= 1:
            if rule.raw_op_name ==  'select_1C~t':
                if not isinstance(imm_reprs[0][1], list):
                    repr0 = [imm_reprs[0][1]]
                else:
                    repr0 = imm_reprs[0][1]
            else:
                repr0 = imm_reprs[0][1]
            return InstFactory.gen_binary_info_inst_high_single_imm(rule.raw_op_name, repr0)
        else:
            imm_dict= {}
            raw_opcode = rule.raw_op_name
            part_desc = PartDescMemory.get_desc(raw_opcode)
            reqired_names=  part_desc.not_fix_part_names
            if  len(reqired_names) == len(imm_reprs) :
                unknown_names = []
                unmatched_idxs = []
                # print('PPPPPPPPPPPPP raw_opcode', raw_opcode)
                if raw_opcode == 'table.init':   # can remove
                    # print('table.init', imm_reprs)
                    imm_reprs = imm_reprs[::-1]
                # if raw_opcode == 'select_1C~t':
                #     print('raw_opcode', raw_opcode, imm_reprs)
                #     if not isinstance(imm_reprs[0][1], list):
                #         repr0 = imm_reprs[0]
                #         imm_reprs = [(repr0[0], [repr0[1]])]
                    
                for idx, (imm_name, imm_val) in enumerate(imm_reprs):
                    if imm_name in reqired_names:
                        imm_dict[imm_name] = imm_val
                    else:
                        unknown_names.append(imm_name)
                        unmatched_idxs.append(idx)
                unmatched_reqired_names = [x for x in reqired_names if x not in imm_dict]
                for cur_idx, unknown_name_idx in enumerate(unmatched_idxs):
                    imm_dict[unmatched_reqired_names[cur_idx]] = imm_reprs[unknown_name_idx][1]
                    

                return InstFactory.gen_binary_info_inst_high(rule.raw_op_name, imm_dict)
            else:
                if len(reqired_names) == 1:
                    required_decoder = part_desc.not_fix_decoders[0]
                    assert isinstance(required_decoder, StructuredDecoder)
                    imm = []
                    for imm_name, imm_val in imm_reprs:
                        imm.append(imm_val)
                    return InstFactory.gen_binary_info_inst_high_single_imm(rule.raw_op_name, imm)
                else:
                    raise NotImplementedError(f'raw_opcode:{raw_opcode} not implemented;  reqired_names : {reqired_names} ;; imm_reprs:{imm_reprs}')

def _get_imm_reprs(val_solution, ph_env):
    imm_reprs:list[tuple[str, Any]] = []

    for imm_idx in range(ph_env.imm_num):
        imm_repr = get_imm_name2val_mapping(val_solution, ph_env, imm_idx)
        imm_reprs.append(imm_repr)
    
    return imm_reprs

def get_imm_name2val_mapping(val_solution, ph_env, imm_idx)->tuple[str, Any]:

    imm_name = f'imm_{imm_idx}'
    imm_ph = ph_env.get_ph(imm_name)
    imm_val = val_solution.get_concrete_val_by_name(imm_name)
    assert isinstance(imm_ph, ImmPH)
    return wrap_imm_repr(imm_val, imm_ph.attr)


def wrap_imm_repr(v, imm_attr)->tuple[str, Any]:
    # !  table.copy attrimm  。 DataPayload 
    # assert 0, print(ori_str, imm_attr)
    
    if imm_attr == 'offset':
        return ('offset', v)
    elif imm_attr == 'align':
        return ('align', v)
    elif imm_attr == 'v128':
        return ( 'v128', v1282byteseq(v))
    elif imm_attr == 'heaptype':
        return ('heaptype', HeapTypeVal.from_int(v).concrete_valtype())
    elif imm_attr == 'type':
        # return f'(result {ImmTypeVal.from_int(v).concrete_str()})'
        return ('type', ImmTypeVal.from_int(v).concrete_str())
    else:
        return (imm_attr, v)

