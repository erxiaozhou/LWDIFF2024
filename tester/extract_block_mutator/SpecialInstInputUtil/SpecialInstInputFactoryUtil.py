import enum
from random import choice, randint
from typing import List, Optional, Tuple

from extract_block_mutator.encode.new_defined_data_type import Blocktype

from ..InstGeneration.insts_generator import insts_under_ty
from ..InstGeneration.RandomInstFactory import RandomInstFactory

from ..InstUtil.InstReqUtil import get_inst_ty_req

from ..Context import Context
from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory
from ..InstGeneration.InstFactory import InstFactory
from ..InstUtil.Inst import Inst
from ..SpecialOpsParas import SpecialOpsParas
from .InsertWrap import InsertWrap
# ======================================== * ==== * ==== * ========================================
# SpecialOpFuncWatFactory

        
class InsertMethod(enum.Enum):
    BYCALL = 1
    BYOP = 2


class OpMutatePara:
    def __init__(self, special_ops:SpecialOpsParas, 
                 insert_m:InsertMethod=InsertMethod.BYOP, 
                 insert_wrap:InsertWrap=InsertWrap.NONE) -> None:
        self.special_ops = special_ops
        self.insert_m = insert_m
        self.insert_wrap = insert_wrap
    def __repr__(self) -> str:
        return f'OpMutatePara({self.special_ops}, {self.insert_m}, {self.insert_wrap})'
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, OpMutatePara):
            return False
        return self.special_ops == o.special_ops and self.insert_m == o.insert_m and self.insert_wrap == o.insert_wrap
    def __hash__(self) -> int:
        return hash((self.special_ops, self.insert_m, self.insert_wrap))


def wrap_generated_insts(init_input_insts:List[Inst], target_inst:Inst, concrete_inst_type:funcType, insert_wrap:InsertWrap, context:Context, post_insts:Optional[List[Inst]]=None)->Tuple[List[Inst], funcType]:
    # print('ZZZZZZZZZZZZZ', 'post_insts', post_insts)
    if post_insts is None:
        post_insts = []
    if insert_wrap == InsertWrap.NONE:
        result = init_input_insts+[target_inst] + post_insts
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.BLOCK:
        '''
        <*init_input_insts>
        block
            <target_inst>
            <post_insts>
        end
        '''
        # block_type_term = choice(['block', 'loop'])
        block_type_term = 'block'
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm(block_type_term,Blocktype(concrete_inst_type)), 
            target_inst, 
            *post_insts,
            InstFactory.opcode_inst('end')
            ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.LOOP:
        '''
        <*init_input_insts>
        loop
            <target_inst>
            <post_insts>
        end
        '''
        # PREPARE TYPE
        # actual block type
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm('loop', Blocktype(concrete_inst_type)), 
            target_inst,
            *post_insts,
            InstFactory.opcode_inst('end')
            ]
        insts_type = concrete_inst_type
        '''
        if check_loop_block_type(concrete_inst_type):
            result = [
                *init_input_insts,
                InstFactory.gen_binary_info_inst_high_single_imm('loop', Blocktype(concrete_inst_type)), 
                target_inst,
                *post_insts,
                InstFactory.opcode_inst('end')
                ]
            insts_type = concrete_inst_type
        else:
            ori_concrete_inst_type = concrete_inst_type
            concrete_inst_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.result_types, concrete_inst_type.result_types)
            prepare_insts = insts_under_ty(ori_concrete_inst_type, None, 0, 0, True)
            prepare_insts2 = insts_under_ty(funcTypeFactory.generate_one_func_type_default(
                ori_concrete_inst_type.result_types, ori_concrete_inst_type.param_types), None, 0, 0, True)
            
            result = [
                *prepare_insts,
                InstFactory.gen_binary_info_inst_high_single_imm('loop', Blocktype(concrete_inst_type)), 
                *prepare_insts2,
                *init_input_insts,
                target_inst,
                *post_insts,
                InstFactory.opcode_inst('end')
                ]
            insts_type = ori_concrete_inst_type
        '''
    elif insert_wrap == InsertWrap.IF:
        '''
        <*init_input_insts>
        i32.const 1
        if
            <target_inst>,
            *post_insts
        else
            <target_inst>,
            *post_insts
        end
        '''
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm('i32.const',  1),
            InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(concrete_inst_type)), 
            target_inst,
            *post_insts,
            InstFactory.opcode_inst('else'), 
            target_inst, 
            *post_insts,
            InstFactory.opcode_inst('end')
            ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.ELSE:
        '''
        <*init_input_insts>
        i32.const 0
        if
            <target_inst>
        else
            <target_inst>
        end
        '''
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm('i32.const',  0),
            InstFactory.gen_binary_info_inst_high_single_imm('if',Blocktype(concrete_inst_type)), 
            target_inst, 
            *post_insts,
            InstFactory.opcode_inst('else'), 
            target_inst, 
            *post_insts,
            InstFactory.opcode_inst('end')
            ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.PREBLOCK:
        '''
        <*init_input_insts>
        block
        end
        <target_inst>
        '''
        # TODO block
        block_kwd = choice(['block', 'loop'])
        empty_block_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, concrete_inst_type.param_types)
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm(block_kwd,Blocktype(empty_block_type)), 
            InstFactory.opcode_inst('end'),
            target_inst,
            *post_insts,
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.POSTBLOCK:
        '''
        <*init_input_insts>
        <target_inst>
        block
        end
        '''
        block_kwd = choice(['block', 'loop'])
        empty_block_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.result_types, concrete_inst_type.result_types)
        result = [
            *init_input_insts,
            target_inst,
            *post_insts,
            InstFactory.gen_binary_info_inst_high_single_imm(block_kwd,Blocktype(empty_block_type)), 
            InstFactory.opcode_inst('end'),
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.PREPTEIF1:
        '''
        <*init_input_insts>
        i32.const
        if
        end
        <target_inst>
        '''
        # block_kwd = choice(['block'])
        empty_block_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, concrete_inst_type.param_types)
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm('i32.const', 1),
            InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(empty_block_type)), 
            InstFactory.opcode_inst('end'),
            target_inst,
            *post_insts,
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.PREPTEIF0:
        '''
        <*init_input_insts>
        i32.const
        if
        end
        <target_inst>
        '''
        # block_kwd = choice(['block'])
        empty_block_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, concrete_inst_type.param_types)
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm('i32.const', 0),
            InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(empty_block_type)), 
            InstFactory.opcode_inst('end'),
            target_inst,
            *post_insts,
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.PRIF:
        '''
        <*init_input_insts>
        i32.const
        if <type>
        else
        end
        <target_inst>
        '''
        # block_kwd = choice(['block'])
        empty_block_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, concrete_inst_type.param_types)
        result = [
            *init_input_insts,
            InstFactory.gen_binary_info_inst_high_single_imm('i32.const', 0),
            InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(empty_block_type)), 
            InstFactory.opcode_inst(f'else'), 
            InstFactory.opcode_inst('end'),
            target_inst,
            *post_insts,
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.PREUNREACHABLE:
        '''
        <*init_input_insts>
        unreachable
        <target_inst>
        '''
        result = [
            *init_input_insts,
            InstFactory.opcode_inst('unreachable'),
            target_inst,
            *post_insts,
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.POSTUNREACHABLE:
        '''
        <*init_input_insts>
        <target_inst>
        unreachable
        '''
        result = [
            *init_input_insts,
            target_inst,
            *post_insts,
            InstFactory.opcode_inst('unreachable'),
        ]
        insts_type = concrete_inst_type
    elif insert_wrap == InsertWrap.ANYOP:
        '''
        br / br_table / return
        <*init_input_insts>
        <target_inst>
        '''
        any_op_inst = None
        candis = ['br_table', 'return', 'br']
        # candi_num = len(candis)
        # for i in range(len(candis)):
        param_num = len(concrete_inst_type.param_types)
        init_input_insts_num = len(init_input_insts)
        if init_input_insts_num == 0:
            to_skip_start_idx = 0
        else:
            to_skip_start_idx = choice(range(init_input_insts_num))
        while len(candis):
            selected_idx = choice(range(len(candis)))
            to_use_op = candis.pop(selected_idx)
            any_op_inst = RandomInstFactory.generate_random_inst(to_use_op, context, concrete_inst_type.param_types)
            if any_op_inst is not None:
                break
        if any_op_inst is None:
            raise ValueError(f'any_op_inst is None, to_use_op: {to_use_op}, concrete_inst_type.param_types: {concrete_inst_type.param_types}')
        # assert any_op_inst is not None
        any_op_inst_type = get_inst_ty_req(any_op_inst, context)
        assert any_op_inst_type is not None
        ty0 = any_op_inst_type.ty0
        if to_use_op == 'br_table':
            insts_before_anyop = []
        else:
            insts_before_anyop_type= funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, ty0.result_types)
            insts_before_anyop = insts_under_ty(insts_before_anyop_type, context, 0, 0, True)
        insts_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, concrete_inst_type.result_types)
        # 
        # 
        select_inst_ = [InstFactory.opcode_inst('select')]
        drop_inst_ = [InstFactory.opcode_inst('drop')]
        # lists = [(1,2)]
        # elems = [*x for x in lists]
        i32_and_select_insts = [InstFactory.gen_binary_info_inst_high_single_imm('i32.const', choice([0, 1])), InstFactory.opcode_inst('select')]
        select_drop_ops = []
        MAX_ADD_NUM = 4
        # print('iapsbvncipdsnuviom,sc,lcacascascas', concrete_inst_type.param_types, insts_before_anyop_type,any_op_inst_type)
        if init_input_insts_num - to_skip_start_idx != param_num:
        # if param_num+1<= to_skip_start_idx:
            for i in range(randint(0, MAX_ADD_NUM)):
                select_drop_ops.extend(choice([i32_and_select_insts, select_inst_, drop_inst_]))
        else:
            for i in range(randint(0, MAX_ADD_NUM)):
                select_drop_ops.append(InstFactory.opcode_inst('drop'))
        #     for i in range(randint(0, MAX_ADD_NUM)):
        #         select_drop_ops.extend(choice([i32_and_select_insts, select_inst_, drop_inst_]))
            
        # select_drop_ops = [choice([select_inst_, drop_inst_]) for _ in range(randint(0, 4))]
        # 
        result = [
            *insts_before_anyop,
            any_op_inst,
            *select_drop_ops,
            *init_input_insts[to_skip_start_idx:],
            target_inst,
            *post_insts,
        ]
        
    # elif insert_wrap == InsertWrap.PRIF:
    #     '''
    #     <*init_input_insts>
    #     i32.const
    #     if <type>
    #     else
    #     end
    #     <target_inst>
    #     '''
    #     # block_kwd = choice(['block'])
    #     empty_block_type = funcTypeFactory.generate_one_func_type_default(concrete_inst_type.param_types, concrete_inst_type.param_types)
    #     result = [
    #         *init_input_insts,
            # InstFactory.gen_binary_info_inst_high_single_imm('i32.const', 0),
    #         
            # InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(empty_block_type)), 
    #         InstFactory.opcode_inst('end'),
    #         target_inst,
    #     ]
    #     insts_type = concrete_inst_type
    else:
        raise NotImplementedError(f'insert_wrap: {insert_wrap} not implemented')

    return result, insts_type



