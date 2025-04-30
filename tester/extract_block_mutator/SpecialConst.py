from typing import Callable, Optional
from .Context import Context
from .InfoLoader import InfoLoader
from enum import Enum, auto

from .get_data_shell import get_data_attr, get_elemseg_attr, get_memory_attr, get_table_attr


class SpecialDefConst(Enum):  # configuration for definition generation
    CommonMaxMemPages = auto()
    MaxMinMemPages = auto()
    CommonMaxTableLen = auto()
    MaxMinTableLen = auto()
    CommonMaxDataLen = auto()
    MaxMemNum = auto()
    MaxTableNum = auto()
    MaxOneElemLen = auto()
    def get_concrete_value(self):
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
    CurMemNum = auto()
    CurGlobalNum = auto()
    LocalNum = auto()


class SpecialModuleConstGetter:
    const_type2get_val_func:dict[SpecialModuleConst, Callable] = {
         SpecialModuleConst.CurMemLen: lambda loader, memory_idx, **kwds: get_memory_attr(loader.defined_memory_datas[memory_idx], 'min') * 65536,
         SpecialModuleConst.CurDefMemNum: lambda loader, **kwds: loader.defined_memory_num,
         SpecialModuleConst.CurTableLength: lambda loader, table_idx, **kwds: get_table_attr(loader.defined_table_datas[table_idx], 'min'),
         SpecialModuleConst.CurDefTableNum: lambda loader, **kwds: loader.defined_table_num,
         SpecialModuleConst.CurFuncNum: lambda loader, **kwds: loader.func_num,
         SpecialModuleConst.CurDataSegNum: lambda loader, **kwds: len(loader.data_sec_datas),
         SpecialModuleConst.CurTableNum: lambda loader, **kwds: loader.table_num,
         SpecialModuleConst.CurElemSegNum: lambda loader, **kwds: len(loader.elem_sec_datas),
         SpecialModuleConst.LocalNum: lambda loader, **kwds: loader.local_num,
         SpecialModuleConst.CurGlobalNum: lambda loader, **kwds: loader.global_num,
         SpecialModuleConst.CurMemNum: lambda loader, **kwds: loader.mem_num
         
    }
    def __init__(self, special_module_const:SpecialModuleConst):
        self.special_module_const = special_module_const
        
    def get_concrete_value(self, loader, 
                            memory_idx:Optional[int]=None,
                            table_idx:Optional[int]=None,
                           **kwds):
        return self.const_type2get_val_func[self.special_module_const](loader, memory_idx=memory_idx, table_idx=table_idx, **kwds)

    __call__ = get_concrete_value


class SpecialContextOneDefConst(Enum):
    OneTableLen = auto()
    OneDataSegLen = auto()
    OneElemSegLen = auto()
    OneMemCurSize = auto()
    OneMemMax = auto()

    def get_concrete_value(self,*, 
                           context:Context,
                           idx:int
                        
                           ) ->int: 
        if self == SpecialContextOneDefConst.OneMemCurSize:
            return get_memory_attr(context.defined_memory_datas[idx], 'min') * 65536
        if self == SpecialContextOneDefConst.OneMemMax:
            max_val = get_memory_attr(context.defined_memory_datas[idx], 'max')
            if max_val is None:
                return SpecialDefConst.CommonMaxMemPages.get_concrete_value()
            else:
                return max_val
        if self == SpecialContextOneDefConst.OneTableLen:
            table_data = context.defined_table_datas[idx]
            return get_table_attr(table_data, 'min')
        if self == SpecialContextOneDefConst.OneDataSegLen:
            return get_data_attr(context.data_sec_datas[idx], 'data_len') # type: ignore
        if self == SpecialContextOneDefConst.OneElemSegLen:
            elem_seg = context.elem_sec_datas[idx]
            return get_elemseg_attr(elem_seg, 'elem_len') # type: ignore
        raise ValueError(f'get_concrete_value not implemented for {self}')

