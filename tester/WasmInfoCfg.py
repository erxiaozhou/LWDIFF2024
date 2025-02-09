from enum import Enum, auto
from typing import Union


class SectionType(Enum):
    Custom = auto()
    Type = auto()
    Import = auto()
    Function = auto()
    Table = auto()
    Memory = auto()
    Global = auto()
    Export = auto()
    Start = auto()
    Element = auto()
    Code = auto()
    Data = auto()
    DataCount = auto()

# val type ==========================================
class valtype(Enum):
    i32 = auto()
    i64 = auto()
    f32 = auto()
    f64 = auto()
    v128 = auto()
    funcref = auto()
    externref = auto()


    # ! 
    def as_str(self) -> str:
        return self.name
    
base_ty_strs = ['i32', 'i64', 'f32', 'f64']
val_type_strs = {'i32', 'i64', 'f32', 'f64', 'funcref', 'externref', 'v128'}
naive_types = val_type_strs
val_type_strs_list = list(val_type_strs)
non_ref_types = {'i32', 'i64', 'f32', 'f64', 'v128'}
ref_types = {'funcref', 'externref'}

numtype = {valtype.i32, valtype.i64, valtype.f32, valtype.f64}
vectype = {valtype.v128}
reftype = {valtype.funcref, valtype.externref}

naive_module_component_types = {
    'i32', 'f64', 'v128', 'i64', 'f32', 'mut',
    'utf8str', 'u32', 'blocktype', 'byte', 'instr',
    'i32_tyrepr', 'i64_tyrepr', 'f32_tyrepr', 'f64_tyrepr',
    'v128_tyrepr', 'funcref_tyrepr', 'externref_tyrepr', 'mut_mut', 'mut_const'
}

i32 = 'i32'

class heaptype(Enum):
    func = auto()
    extern = auto()
 

class ContextValAttr(Enum):
    Locals = auto()
    OneLocal = auto()
    Globals = auto()
    OneGlobal = auto()
    MemSec = auto()
    OneMem = auto()
    TableSec = auto()
    OneTable = auto()
    DataSec = auto()
    OneDataSeg = auto()
    ElemSec = auto()
    OneElemSeg = auto()
    OneFunc = auto()
    Funcs = auto()
    OneFuncRef = auto()
    FuncRefs = auto()


class globalValMut(Enum):
    Mut = auto()
    Const = auto()
    def __bool__(self) -> bool:
        return self == globalValMut.Mut
    @classmethod
    def from_bool(cls, b:bool):
        if b:
            return cls.Mut
        return cls.Const
    

class ExportType(Enum):
    func = auto()
    table = auto()
    mem = auto()
    global_ = auto()


class ImportType(Enum):
    func = auto()
    table = auto()
    mem = auto()
    global_ = auto()

class ElemSecAttr(Enum):
    passive = auto()
    active = auto()
    declarative = auto()

    @staticmethod
    def is_valid_str(s:str)->bool:
        return s in {'elem.passive', 'elem.active', 'elem.declarative'}
    @classmethod
    def from_str(cls, s:str):
        assert cls.is_valid_str(s)
        if s == 'elem.passive':
            return cls.passive
        if s == 'elem.active':
            return cls.active
        if s == 'elem.declarative':
            return cls.declarative
        raise ValueError(f'invalid ElemSecAttr str: {s}')


class DataSegAttr(Enum):
    active = auto()
    passive = auto()
    @staticmethod
    def is_valid_str(s:str)->bool:
        return s in {'data.active', 'data.passive'}
    @classmethod
    def from_str(cls, s:str):
        assert cls.is_valid_str(s)
        if s == 'data.active':
            return cls.active
        if s == 'data.passive':
            return cls.passive
        raise ValueError(f'invalid DataSegAttr str: {s}')


AttrConst = Union[ElemSecAttr, DataSegAttr, globalValMut, str]
