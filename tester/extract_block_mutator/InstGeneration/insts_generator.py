from typing import Callable, Optional

from .RandomInstFactory import RandomInstFactory
from .get_possible_ty_util import get_possible_inst_ops_need_prefix
from ..Context import Context
from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory
from ..InstUtil.InstReqUtil import get_inst_ty_req, get_insts_ty_req
from ..InstUtil.get_skip_ops_by_Context import get_skip_ops_by_Context
from .insts_cfg import all_names_can_insert, non_v128_all_names_can_insert
from .padding_input_type import padding_input_type
from ..typeReq import check_ftype_match_req, typeReq, merge_req
import random
SKIP_CALL0 = True


class InstsGenerator:
    def __init__(self, short_limit, long_limit, considered_ops:set[str] ):
        self.short_limit = short_limit
        self.long_limit = long_limit
        self.considered_ops = considered_ops
        # 
        self._last_context:Optional[Context] = None
        self._last_context_to_skip_ops:Optional[set[str]] = None
        self._last_None_context_to_skip_ops:Optional[set[str]] = None

    @classmethod
    def from_insts_features(cls, short_limit=0, long_limit=6, non_v128=True, no_ereturn=False, no_unreachable=False):
        considered_ops = _get_considered_ops_by_feature(
            non_v128=non_v128, 
            no_unreachable=no_unreachable, 
            no_ereturn=no_ereturn
            )
        return cls(short_limit, long_limit, considered_ops)
    
    def get_insts_with_ty(self, required_type: funcType, context:Optional[Context]=None):# -> list[Any]:
        # !   ，context  insts ， Case ，
        context_to_skip_ops = self._infer_to_skip_ops(context)
        assert required_type is not None
        return insts_under_ty(required_type, context, self.short_limit, self.long_limit, considered_ops=self.considered_ops, context_to_skip_ops=context_to_skip_ops)

    def _infer_to_skip_ops(self, context:Optional[Context]):
        if context is None:
            if self._last_None_context_to_skip_ops is None:
                self._last_None_context_to_skip_ops = get_skip_ops_by_Context(context)
            return self._last_None_context_to_skip_ops
        else:
            _nop1()
            if (self._last_context_to_skip_ops is None) or (self._last_context is None) or (not context.use_same_variables(self._last_context)):
                self._last_context = context
                self._last_context_to_skip_ops = get_skip_ops_by_Context(context)
            return self._last_context_to_skip_ops

def _nop1():
    pass

# 
def insts_under_ty(required_type: funcType, context:Optional[Context]=None, short_limit=0, long_limit=6, non_v128=True, no_ereturn=False, no_unreachable=True, considered_ops:Optional[set[str]]=None, context_to_skip_ops:Optional[set[str]]=None):

    # TODO 
    # 
    cur_type = funcTypeFactory.generate_one_func_type_default([], required_type.param_types)
    cur_type_req = typeReq.from_one_ty(cur_type)
    ori_type_req = typeReq.from_one_ty(cur_type)
    cur_stack_param_types = cur_type.result_types
    cur_insts = []
    # ! ， cur_stack_req functype ，
    if considered_ops is None:
        considered_ops = _get_considered_ops_by_feature(non_v128, no_unreachable, no_ereturn)
    # 
    if context_to_skip_ops is None:
        to_skip_ops_by_context = get_skip_ops_by_Context(context)
    else:
        to_skip_ops_by_context = context_to_skip_ops
    considered_ops = considered_ops - to_skip_ops_by_context
    # 
    while True:
        if long_limit == 0:
            pre_insts, post_insts = generate_wrapper_insts_for_ty_req(required_type, context, funcTypeFactory.generate_one_func_type_default([], []) )
            cur_insts = pre_insts + cur_insts + post_insts
            assert None not in pre_insts, print(pre_insts)
            break
            
        # whether re-generate
        # cannot determine the type of the new_inst, continue
        # the generated code's code cannot exist
        assert cur_type is not None
        new_inst = _get_inst_randomly(considered_ops, context=context, cur_stack_param_types=cur_stack_param_types)
        if new_inst is None:
            continue
        new_stack_req, new_stack_ty = get_info_after_append_inst(cur_type_req, new_inst, context)
        # print('new_stack_req', new_stack_req)
        # print('new_stack_ty', new_stack_ty)
        # input()
        # ! ？？？
        if new_inst.opcode_text == 'ref.is_null' and len(cur_insts) > 0:
            raise Exception(f'ref.is_null: {new_inst} || {new_stack_ty} || {new_stack_req} {cur_insts[-1]} P2')
        # print('vnoaivjnhopavinoa[ovnioa]', new_stack_req, new_stack_ty)
        # input()
        if new_stack_req is None or new_stack_ty is None:
            continue
        if SKIP_CALL0:
            # ! import func num，context
            import_func_num = 0 if context is None else context.import_func_num
            if context is not None:
                assert context.import_func_num is not None
            if new_inst.opcode_text == 'call':
                if new_inst.imm_part.val == import_func_num:
                    continue
        '''
        if ((new_inst.opcode_text in ['br', 'return']) and check_ftype_match_req(required_type, new_stack_req)) or new_inst.opcode_text == 'br_table':
            if check_ftype_match_req(required_type, new_stack_req) :
                cur_insts.append(new_inst)
                insts_req = get_insts_ty_req(cur_insts, context)
                pre_insts, _ = generate_wrapper_insts_for_ty_req(required_type, context, insts_req.tys[0])
                cur_insts = pre_insts + cur_insts
                break
            else:
                continue
        '''
        cur_type_req = new_stack_req
        cur_type = new_stack_ty
        cur_stack_param_types = cur_type.result_types
        # if new_inst.opcode_text == 'ref.is_null':
        #     raise Exception(f'ref.is_null: {new_inst}  || {cur_insts} P2')
        # if new_inst.opcode_text == 'br' or new_inst.opcode_text == 'br_if':
        #     print(f'ZZZZZ Context.labels when generating brs: {new_inst} {context.label_types}')
        cur_insts.append(new_inst)
        assert cur_type is not None
        assert required_type is not None
        # TODO cur_type == required_type  typereq
        # TODO， cur_type == required_type  
        if ((len(cur_insts) >= short_limit) and check_ftype_match_req(required_type, new_stack_req)) or (len(cur_insts) > long_limit):
            insts_req = get_insts_ty_req(cur_insts, context)

            insts_type = random.choice(insts_req.tys)

            pre_insts, post_insts = generate_wrapper_insts_for_ty_req(required_type, context, insts_type)
            cur_insts = pre_insts + cur_insts + post_insts
            assert None not in pre_insts, print(pre_insts)
            break

    return cur_insts


def get_info_after_append_inst(existing_stack_req, new_inst, context):
    assert new_inst is not None
    try:
        new_inst_req = get_inst_ty_req(new_inst, context)
    except Exception as e:
        # logger.warning(f'Warning: {e} {new_inst}')
        if isinstance(e, AttributeError):
            raise e
        if isinstance(e, NotImplementedError):
            raise e
        if isinstance(e, AssertionError):
            raise e
        
        print(f'AAA Warning: {type(e)} {e} {new_inst}')
        return None, None
    if new_inst_req is None:
        return None, None

    merged_req = merge_req(existing_stack_req, new_inst_req)
    # print(existing_stack_req, new_inst_req, merged_req)
    if merged_req.impossible():
        new_req = None
        new_type = None
    # cur_ty
    elif len(merged_req.tys) > 1:
        new_type = random.choice(merged_req.tys)
        new_req=  typeReq.from_one_ty(new_type)
        return new_req, new_type
        return None, None
    # detect type and type requirement
    # detect control instruction situations
    else:
        new_req = merged_req
        new_type = merged_req.tys[0]
    # print('get_info_after_append_inst', '**************************************')
    # print(existing_stack_req, new_inst, new_req, new_type)
    # print('----------------------------------------------------')
    return new_req, new_type


def generate_wrapper_insts_for_ty_req(required_type, context, cur_ty):
    pre_insts = padding_input_type(
                required_type.param_types, cur_ty.param_types, context=context)
    post_insts = padding_input_type(
                cur_ty.result_types, required_type.result_types, context=context)
        
    return pre_insts, post_insts


def _get_inst_randomly(considered_ops:set[str], context:Optional[Context]=None, cur_stack_param_types=None):
    if cur_stack_param_types is not None:
        considered_ops = get_possible_inst_ops_need_prefix(cur_stack_param_types, considered_ops)
    considered_op_list = list(considered_ops)
    opcode_name = random.choice(considered_op_list)

    result = RandomInstFactory.generate_random_inst(opcode_name, context, cur_stack_param_types=cur_stack_param_types)
    # print('opcode_name', opcode_name)
    # print('result', result)
    return result

def _get_considered_ops_by_feature(non_v128, no_unreachable, no_ereturn):
    if non_v128:
        considered_ops = non_v128_all_names_can_insert
    else:
        considered_ops = all_names_can_insert
    if no_unreachable:
        considered_ops = considered_ops - {'unreachable'}
    if no_ereturn:
        considered_ops = considered_ops - {'return', 'br', 'br_if', 'br_table'}
    return considered_ops
