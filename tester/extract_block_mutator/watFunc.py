import re
from typing import List, Optional

from extract_block_mutator.encode.NGDataPayload import DataPayloadName, DataPayloadwithName

from .InstUtil.Inst import Inst
from .InstGeneration.InstFactory import InstFactory
from .funcType import funcType
from .funcTypeFactory import funcTypeFactory
from .blockParser.block import start_block_ops

class watFunc:
    def __init__(self, insts, defined_local_types, func_ty:Optional[funcType]=None):
        if _need_append_end(insts):
            insts.append(InstFactory.opcode_inst('end'))
        self.insts:List[Inst] = insts
        self.defined_local_types:List[str] = defined_local_types
        self._func_ty: Optional[funcType] = func_ty
        

    @classmethod
    def from_local_def_repr(cls, insts, local_def_repr, func_ty:Optional[funcType]=None):
        locals = []
        
        for local_def in local_def_repr:
            for i in range(local_def['count']):
                locals.append(local_def['value_type'])
        return cls(
            insts=insts,
            defined_local_types=locals,
            func_ty=func_ty
        )

    @property
    def locals_with_def_repr(self):
        local_type_num = []
        cur_local = None
        for local_type in self.defined_local_types:
            if local_type == cur_local:
                local_type_num[-1][1] += 1
            else:
                cur_local = local_type
                local_type_num.append([local_type, 1])
        local_defs = []
        for local_type, count in local_type_num:
            local_def = DataPayloadwithName(
                data = {
                    'value_type': local_type,
                    'count': count
                },
                name = 'locals'
            )
            local_defs.append(local_def)
        return local_defs
    

    def copy(self):
        return watFunc(
            insts=[inst.copy() for inst in self.insts],
            defined_local_types=self.defined_local_types.copy(),
            func_ty=self.func_ty.copy()
        )

    @property
    def func_ty(self) -> funcType:  
        assert self._func_ty is not None
        return self._func_ty
    @func_ty.setter
    def func_ty(self, func_ty:funcType):
        self._func_ty = func_ty
    @property
    def param_types(self):
        # assert 0
        return self.func_ty.param_types
    
    @property
    def result_types(self):
        # assert 0
        return self.func_ty.result_types

    @property
    def local_types(self):
        return self.param_types + self.defined_local_types


def two_func_has_same_and_inst_op(func1: watFunc, func2: watFunc):
    locals1 = func1.defined_local_types
    locals2 = func2.defined_local_types
    if len(locals1) != len(locals2):
        return False
    inst_num1 = len(func1.insts)
    inst_num2 = len(func2.insts)
    if inst_num1 != inst_num2:
        return False
    # print('====Insts1 :', func1.insts)
    # print('====Insts2 :', func2.insts)
    # for debug
    op_same_info = []
    for i in range(inst_num1):
        if func1.insts[i].opcode_text != func2.insts[i].opcode_text:
            op_same_info.append((func1.insts[i].opcode_text, func2.insts[i].opcode_text))
        else:
            op_same_info.append('-')
    # print('LLLLLLLLL op_same_info:', op_same_info)
    # 
    for i in range(inst_num1):
        if func1.insts[i].opcode_text != func2.insts[i].opcode_text:
            return False
    return True

def _need_append_end(insts:list[Inst]):
    

    start_line_num = 0
    end_line_num = 0
    for inst in insts:
        if inst.opcode_text in start_block_ops:
            start_line_num += 1
        if inst.opcode_text == 'end':
            end_line_num += 1
    if start_line_num == end_line_num + 1:
        return True
    if start_line_num == end_line_num:
        return False
    raise Exception(f'start_line_num {start_line_num} != end_line_num {end_line_num}: insts:{insts}')