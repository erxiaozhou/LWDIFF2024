from typing import Optional
from extract_block_mutator.Context import Context
from enum import Enum, auto
from .get_data_shell import get_data_attr, get_elemseg_attr, get_memory_attr, get_table_attr

class SpecialDefConst(Enum):
    
    # MaxMemPages = auto()
    CommonMaxMemPages = auto()
    MaxMinMemPages = auto()
    CommonMaxTableLen = auto()
    MaxMinTableLen = auto()
    CommonMaxDataLen = auto()
    MaxMemNum = auto()
    MaxTableNum = auto()
    MaxOneElemLen = auto()
    def get_concrete_value(self):
        # if self == SpecialDefConst.MaxMemPages:
        #     return 65536
        if self == SpecialDefConst.CommonMaxMemPages:
            return 512
        if self == SpecialDefConst.MaxMinMemPages:
            return 5
        if self == SpecialDefConst.CommonMaxTableLen:
            return 512
        if self == SpecialDefConst.MaxMinTableLen:
            return 30
        if self == SpecialDefConst.CommonMaxDataLen:
            return 1024
        if self == SpecialDefConst.MaxMemNum:
            return 1
        if self == SpecialDefConst.MaxOneElemLen:
            return 100
        if self == SpecialDefConst.MaxTableNum:
            return 1
        raise NotImplementedError



class SpecialModuleConst(Enum):
    CurMemLen = auto()
    CurTableLength = auto()
    CurFuncNum = auto()
    CurTableNum = auto()
    CurDefMemNum = auto()
    CurDefTableNum = auto()
    CurDataSegNum = auto()
    CurElemSegNum = auto()
    CurGlobalNum = auto()
    CurMemNum = auto()
    def get_concrete_value(self, wasm_parzer, 
                            memory_idx:Optional[int]=None,
                            table_idx:Optional[int]=None,
                           **kwds):
        if self == SpecialModuleConst.CurMemLen:
            assert memory_idx is not None
            return get_memory_attr(wasm_parzer.defined_memory_datas[memory_idx], 'min') * 65536
        if self == SpecialModuleConst.CurDefMemNum:
            return wasm_parzer.mem_num
        if self == SpecialModuleConst.CurTableLength:
            assert table_idx is not None
            table_data = wasm_parzer.defined_table_datas[table_idx]
            return get_table_attr(table_data, 'min')
        if self == SpecialModuleConst.CurDefTableNum:
            return len(wasm_parzer.defined_table_datas)
        
        if self == SpecialModuleConst.CurFuncNum:
            return  wasm_parzer.func_num
        if self == SpecialModuleConst.CurDataSegNum:
            return len(wasm_parzer.data_sec_datas)
        if self == SpecialModuleConst.CurTableNum:
            return len(wasm_parzer.defined_table_datas)
        if self == SpecialModuleConst.CurElemSegNum:
            return len(wasm_parzer.elem_sec_datas)
        if self == SpecialModuleConst.CurGlobalNum:
            return len(wasm_parzer.defined_globals)
        if self == SpecialModuleConst.CurMemNum:
            return len(wasm_parzer.defined_memory_datas)
        
        # if 
        raise NotImplementedError
        

class specialContextConst(Enum):
    LocalNum = auto()
    GlobalNum = auto()
    CurMemNum = auto()
    OneMemCurSize = auto()
    OneMemMax = auto()
    FuncNum = auto()
    TableNum = auto()
    DataSegNum = auto()
    ElemSegNum = auto()
    OneTableLen = auto()
    OneDataSegLen = auto()
    OneElemSegLen = auto()
    def get_concrete_value(self,*, 
                           context:Context,
                           memory_idx:Optional[int]=None,
                           table_idx:Optional[int]=None,
                           elem_idx:Optional[int]=None,
                           data_idx:Optional[int]=None
                           )->int:
        if self == specialContextConst.LocalNum:
            return len(context.local_types)
        if self == specialContextConst.GlobalNum:
            return context.global_num
        if self == specialContextConst.CurMemNum:
            return len(context.defined_memory_datas)
        if self == specialContextConst.OneMemCurSize:
            assert memory_idx is not None
            return get_memory_attr(context.defined_memory_datas[memory_idx], 'min') * 65536
        if self == specialContextConst.OneMemMax:
            assert memory_idx is not None
            max_val = get_memory_attr(context.defined_memory_datas[memory_idx], 'max')
            if max_val is None:
                return SpecialDefConst.CommonMaxMemPages.get_concrete_value()
            else:
                return max_val
        if self == specialContextConst.FuncNum:
            return context.func_num
        if self == specialContextConst.TableNum:
            return len(context.defined_table_datas)
        if self == specialContextConst.DataSegNum:
            return context.data_sec_num
        if self == specialContextConst.ElemSegNum:
            return context.elem_sec_num
        if self == specialContextConst.OneTableLen:
            assert table_idx is not None
            table_data = context.defined_table_datas[table_idx]
            return get_table_attr(table_data, 'min')
        if self == specialContextConst.OneDataSegLen:
            assert data_idx is not None
            return get_data_attr(context.data_sec_datas[data_idx], 'data_len') # type: ignore
        if self == specialContextConst.OneElemSegLen:
            assert elem_idx is not None
            elem_seg = context.elem_sec_datas[elem_idx]
            return get_elemseg_attr(elem_seg, 'elem_len') # type: ignore
        
        raise NotImplementedError


# def get_module_const_or_0()