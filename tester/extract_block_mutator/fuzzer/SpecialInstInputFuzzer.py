from pathlib import Path
import random
from typing import  List, Optional, Union


from ..SpecialInstInputUtil.SpecialInstInputFactoryUtil import wrap_generated_insts
from ..ModuleFuzzerUtil.func_related import gen_local_seq
from ..ModuleFuzzerUtil.func_related import extend_return_type_core, insert_func_core
from ..inst_pose_selector import PosCandi
from ..watFunc import watFunc
from ..parser_to_file_util import parser2wasm
from ..WasmParser import WasmParser
from .Fuzzer import Fuzzer

from ..InstGeneration.insts_generator import InstsGenerator
from ..Context import Context, generate_context_by_out_layers_reuse_data
from ..funcTypeFactory import funcTypeFactory
from ..InstGeneration.InstFactory import InstFactory
from ..tool import get_func0_context_from_wat_parser
from ..blockParser.inst_pos_for_insert import inst_pos2type_layers_for_insert, generate_inst_pos2type_layers_for_insert
from ..SpecialInstInputUtil.RuleV2InstInputFactory import   RuleV2InputFactory, generate_insts_for_rule, generated_insts_for_rule_core
from ..tool import set_parser_func_local_by_func0_context
from time import time
# !  generate_directWasmBlock_with_type
# ! 


class SpecialInstInputFuzzer(Fuzzer):
    def __init__(self, support_ops=None, support_pos_candis=None, support_wraps=None) -> None:
        super().__init__()
        # assert self.logger is not None
        self.reset_op_factory = RuleV2InputFactory(support_ops, support_pos_candis, support_wraps)
        self.padding_inst_generator = InstsGenerator.from_insts_features(
            0, 0, True, True, no_unreachable=True
        )


    def fuzz_one(self, ori_wasm: Union[Path, str], tgt_wasm_path, parser:Optional[WasmParser]=None, remove_loop_=False):
        t0 = time()
        
        assert self.logger is not None
        logger = self.logger
        ori_parser = self.get_parser_of_ori_wasm(ori_wasm, parser, remove_loop_)
        assert ori_parser.func0 is not None
        func0_context = get_func0_context_from_wat_parser(ori_parser)
        # 

        rule, rule_idx = self.reset_op_factory.select_rule(func0_context, [], ori_parser.sop_pos_candis, None, self.logger)
        position_to_insert, pos_candi = self.reset_op_factory.select_pos(
            rule_idx,
            insts=ori_parser.func0.insts,
            length_considering_early_exit=ori_parser.insts0_early_return_pos,
            ori_supported_pos_candis=ori_parser.sop_pos_candis,
            logger=self.logger)
        
        print(f'In sop fuzzer PosCandi: {pos_candi}; Rule: {rule};tgt_wasm_path:{Path(tgt_wasm_path).name}')
        wrap = self.reset_op_factory.select_wrap(rule_idx, pos_candi)
        insts_type = self.write_a_case_by_rule(tgt_wasm_path, ori_parser, func0_context, rule, position_to_insert, pos_candi,  wrap)
        # log something
        t1 = time()
        print(f'In sop fuzzer concrete_insts_type: {insts_type}; Wrap: {wrap}')
        info_str = f'PosCandi: {pos_candi}; Rule: {rule};tgt_wasm_path:{Path(tgt_wasm_path).name}; concrete_insts_type: {insts_type}; Wrap: {wrap}'
        # print('In sop fuzzer info_str:', info_str)
        logger.info(info_str)
        logger.info(f'Fuzzing {Path(ori_wasm).name} finished, time cost: {t1-t0} seconds')
        self.reset_op_factory.confirm_selection(pos_candi, rule_idx, wrap, logger=self.logger)


    def least_pos(self):
        return self.reset_op_factory.least_pos_candi
    def write_a_case_by_rule(self, tgt_wasm_path, ori_parser, func0_context:Context, rule, position_to_insert, pos_candi, wrap):
        # print('pos_candi', pos_candi)
        if pos_candi == PosCandi.NewFunc:
            cur_context = func0_context.copy()
            defined_locals = gen_local_seq()
            assert rule.op not in set(('br', 'br_table', 'br_if', 'if', 'end', 'else', 'return'))  # context， functype，control op
            # whether can determine the inst type first
            # ! no localconstraint
            # get inst type
            _, exec_get_inst_type = generate_insts_for_rule(rule, cur_context, wrap)

            if exec_get_inst_type is None:
                func_type = funcTypeFactory.generate_one_func_type_default([], [])
            else:
                func_type = exec_get_inst_type
            cur_context.cur_func_ty = func_type
            cur_context.label_types = [func_type.result_types]
            cur_context.local_types = rule.operand_types + defined_locals
            # has_determine_func_type = True
            
            # ! ANYOP。
            result_insts, insts_type = generate_insts_for_rule(rule, cur_context, wrap)   # ! 
            if func_type is None:
                func_type = funcTypeFactory.generate_one_func_type_default([], insts_type.result_types)

            pre_insts = [InstFactory.gen_binary_info_inst_high_single_imm('local.get', i) for i in range(len(insts_type.param_types))]
            # if not has_determine_func_type:
            #     cur_context.cur_func_ty = func_type
            # 
            print('In sop fuzzer new insts 0:', result_insts)
            new_func = watFunc(pre_insts+result_insts, defined_locals, func_type)
            insert_func_core(ori_parser, new_func)
            rewrite_func_idx= len(ori_parser.defined_funcs) - 1
        elif pos_candi == PosCandi.ForceReturn:
            # assert 0
            cur_context = _get_context_of_insert_pos(func0_context, position_to_insert, ori_parser.func0_block)
            target_inst,pre_insts,concrete_inst_type, _post_insts = generated_insts_for_rule_core(rule, cur_context, max_local=300)
            # ereturn_pre_insts_len = len(pre_insts)
            extend_ops = concrete_inst_type.result_types
            #
            result_insts, insts_type = wrap_generated_insts(pre_insts, target_inst  , concrete_inst_type, wrap, cur_context, _post_insts)
            # print('|||||||||||||||', 'result_insts', result_insts)
            # 
            ori_return_types = cur_context.cur_func_ty.result_types
            pre_insts = self.padding_inst_generator.get_insts_with_ty(funcTypeFactory.generate_one_func_type_default([], ori_return_types + insts_type.param_types), cur_context)
            post_insts = [InstFactory.opcode_inst('return')]
            insts = pre_insts + result_insts + post_insts
            return_idx = position_to_insert + len(pre_insts) + len(result_insts)
            print('In sop fuzzer new insts 2:', insts)
            ori_parser.func0_insts[position_to_insert: position_to_insert] = insts
            # print(position_to_insert)
            extend_return_type_core(ori_parser, extend_ops, 0, [return_idx])
            ori_parser.clean_pre_info()
            assert ori_parser._func0_block is None and ori_parser._insts0_early_return_pos is None
            rewrite_func_idx= 0
            
            
        else:
            cur_context = _get_context_of_insert_pos(func0_context, position_to_insert, ori_parser.func0_block)
            # print('YYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
            # print('Cur rule:', rule)
            # print('XXXXXXXXXXXXXXXXXXXXX')
            # print('|||||', rule.context_condition_func)
            # # print('Cur rule:', rule)
            # print('XXXXXXXXXXXXXXXXXXXX')
            
            result_insts, insts_type = generate_insts_for_rule(rule, cur_context, wrap)

            pre_insts = self.padding_inst_generator.get_insts_with_ty(funcTypeFactory.generate_one_func_type_default([], insts_type.param_types), cur_context)
            # print('@#R(KFSLFLSFLDS)', insts_type, pre_insts)
            post_insts = self.padding_inst_generator.get_insts_with_ty(funcTypeFactory.generate_one_func_type_default(insts_type.result_types, []), cur_context)
            insts = pre_insts + result_insts + post_insts
            print('In sop fuzzer new insts 3:', insts)
            ori_parser.func0_insts[position_to_insert: position_to_insert] = insts
            ori_parser.clean_pre_info()
            assert ori_parser._func0_block is None and ori_parser._insts0_early_return_pos is None
            rewrite_func_idx= 0



        set_parser_func_local_by_func0_context(ori_parser, cur_context, rewrite_func_idx)
        parser2wasm(ori_parser, tgt_wasm_path)
        return insts_type
            
        

def _get_context_of_insert_pos(func0_context, position_to_insert, block):
    block_position_for_insert = generate_inst_pos2type_layers_for_insert(block)
    outer_laters = inst_pos2type_layers_for_insert(position_to_insert, block_position_for_insert)
    cur_context = generate_context_by_out_layers_reuse_data(func0_context, outer_laters)
    return cur_context


