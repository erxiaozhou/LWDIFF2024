
from SInst.RuleInst.GptInst2GRule import GptInstKM

from typing import Optional, List

from extract_block_mutator.encode.byte_define.init_Inst_decoder import get_all_ng_names
from extract_block_mutator.get_data_shell import get_table_attr
from ..InstUtil.Inst import Inst
from random import choice, choices, randint, random
from ..Context import Context
from .InstFactory import InstFactory
from file_util import read_json
from functools import lru_cache
from ..encode.byte_define.SectionPart import op_has_no_imm_by_opcode2

        
    

@lru_cache(maxsize=1024)
def inst_has_no_imm_by_opcode(opcode_text:str):
    # assert isinstance(opcode_text, str)
    return opcode_text in op_has_no_imm_by_opcode2

def _init_factory_raw_inst_name2ValidInstGenerator():
    GptInstKM(just_valid_part=True)
    return GptInstKM.raw_inst_name2ValidInstGenerator


class RandomInstFactory:
    generated_opcode_insts = {}
    raw_inst_name2ValidInstGenerator = _init_factory_raw_inst_name2ValidInstGenerator()

    @staticmethod
    def generate_random_inst(opcode, context: Optional[Context] = None, cur_stack_param_types: Optional[List[str]] = None) -> Optional[Inst]:
        return RandomInstFactory._generate_random_inst_ng(opcode, context, cur_stack_param_types)
    

    @staticmethod
    def _generate_random_inst_ng(opcode, context: Optional[Context] = None, cur_stack_param_types: Optional[List[str]] = None) -> Optional[Inst]:
        select_path1 = inst_has_no_imm_by_opcode(opcode)

        # print9len( RandomInstFactory.raw_inst_name2ValidInstGenerator)
        # print('len( RandomInstFactory.raw_inst_name2ValidInstGenerator)', len( RandomInstFactory.raw_inst_name2ValidInstGenerator))
        covered_names = set( RandomInstFactory.raw_inst_name2ValidInstGenerator.keys())
        # all_names = set(get_all_ng_names())
        # uncovered_names = all_names - covered_names
        # print('uncovered_names', uncovered_names)
        if select_path1:
            result = InstFactory.opcode_inst(opcode)
        elif opcode in RandomInstFactory.raw_inst_name2ValidInstGenerator:
            generator = RandomInstFactory.raw_inst_name2ValidInstGenerator[opcode]
            # assert context is not None
            result = generator.generate_random_inst_candi(context, cur_stack_param_types)

        else:
            result = _generate_random_inst_manual(
                opcode, context, cur_stack_param_types)
        return result


def _generate_random_inst_manual(opcode: str, context: Optional[Context] = None, cur_stack_param_types: Optional[List[str]] = None):
    if opcode in ['br', 'br_if']:
        if context is None:
            return None
        else:
            label_num = len(context.label_types)
            possible_label = randint(0, label_num-1)
            return InstFactory.gen_binary_info_inst_high_single_imm(opcode, possible_label)
    elif opcode == 'call':
        if context is None:
            return None
        else:
            func_num = context.func_num
            possible_func_idx = randint(0, func_num-1)
            return InstFactory.gen_binary_info_inst_high_single_imm(opcode, possible_func_idx)
    elif opcode == 'br_table':
        # print('BBBBBB cur_stack_param_types', cur_stack_param_types)
        # print('LL context.label_types', context.label_types)
        if cur_stack_param_types is None or context is None:
            return None
        else:
            # possible_labels = list(range(len(context.label_types)))
            label_req_ops = context.label_types
            assert label_req_ops is not None
            if len(cur_stack_param_types) == 0 or cur_stack_param_types[-1] != 'i32':
                return None
            else:
                possible_label_idxs = [label_idx for label_idx in range(len(context.label_types)) if cur_stack_param_types[:-1] == label_req_ops[label_idx]]
                # print('BBBBBZZZZZZZZZZZZZZZZZZZBBBBBBBBBB possible_label_idxs', possible_label_idxs)
                label_num = len(context.label_types)
                # possible_label_idxs2 = [label_num - n -1 for n in possible_label_idxs]
                # possible_label_idxs = possible_label_idxs2
                # print('BBBBBZZZZZZZZZZZZZZZZZZZBBBBBBBBBB   new possible_label_idxs', possible_label_idxs)
                # possible_label_idxs2 = []
                if len(possible_label_idxs) == 0:
                    return None
                else:
                    table_length = randint(1, 100)  # 
                    label_idxs = choices(possible_label_idxs, k=table_length)
                    # imm_repr = ' '.join([str(label_idx)
                    #                     for label_idx in label_idxs])
                    ls = label_idxs[:-1]
                    lN = label_idxs[-1]
                    imm_dict = {'l': ls, 'l_N': lN}
                    return InstFactory.gen_binary_info_inst_high(opcode, imm_dict)
    else:
        if opcode != 'call_indirect':
            if context is None :
                return None
            if len(context.func_idxs_in_elem) == 0:
                return None
            # 
            table_num = context.table_num
            func_tale_idxs:list[int] = []
            for table_idx in range(table_num):
                if context.table_types[table_idx] == 'funcref':
                    func_tale_idxs.append(table_idx)
            if len(func_tale_idxs) == 0:
                return None
            table_idx = choice(func_tale_idxs)

            type_num = len(context.types)
            if type_num == 0:
                return None
            type_idx = randint(0, table_num-1)
            return InstFactory.gen_binary_info_inst_high(
                opcode, {
                    'y': type_idx,
                    'x': table_idx
                }
            )
            # 
            # func_idx = choice(context.func_idxs_in_elem)
            # func_type_idx = context.func_type_ids[func_idx]
            raise NotImplementedError(f'opcode is {opcode}')
        # assert opcode in ['call_indirect']
        return None
    #    "call_indirect": [
    #     [
    #         "prefix_0",
    #         "<Fix:11:hex>"
    #     ],
    #     [
    #         "y",
    #         "typeidx"
    #     ],
    #     [
    #         "x",
    #         "tableidx"
    #     ]
    # ],