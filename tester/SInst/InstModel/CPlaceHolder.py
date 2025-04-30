from enum import Enum
from SInst.InstModel.SymbolValue import SymbolValue
from WasmInfoCfg import val_type_strs
from z3 import BitVec, FP, Float32, Float64
from .PlaceHolder import PHType
from .PlaceHolder import PH

class ImmPHFactory:
    _generated_objs = {}
    valid_ty_attr_combines = (
        ('i32', 'i32'),
        ('i64', 'i64'),
        ('f32', 'f32'),
        ('f64', 'f64'),
        ('funcref', 'funcref'),
        ('externref', 'externref'),
        ('heaptype', 'heaptype'), 
        ('valtype', 'type'),
        ('v128', 'v128'),
        ('u32', 'local_idx'),
        ('u32', 'align'),
        ('u32', 'offset'),
        ('u32', 'lane_idx'),
        ('u32', 'table_idx'),
        ('u32', 'data_idx'),
        ('u32', 'elem_idx'),
        ('u32', 'func_idx'),
        ('u32', 'global_idx')
    )
    default_attr2type = {
        'i32': 'i32',
        'i64': 'i64',
        'f32': 'f32',
        'f64': 'f64',
        'funcref': 'funcref',
        'externref': 'externref',
        'v128': 'v128',
        'local_idx': 'u32',
        'align': 'u32',
        'offset': 'u32',
        'lane_idx': 'u32',
        'table_idx': 'u32',
        'data_idx': 'u32',
        'elem_idx': 'u32',
        'func_idx': 'u32',
        'heaptype': 'heaptype', 
        'type': 'valtype', 
        'global_idx': 'u32'
    }

    @staticmethod
    def gen_ph(ty, idx, attr):
        assert (ty, attr) in ImmPHFactory.valid_ty_attr_combines, print(ty, attr)
        if (ty, idx, attr) not in ImmPHFactory._generated_objs:
            ImmPHFactory._generated_objs[(ty, idx, attr)] = ImmPH(ty, idx, attr)
        return ImmPHFactory._generated_objs[(ty, idx, attr)]
    @staticmethod
    def get_ph_by_attr(idx, attr):
        ty = ImmPHFactory.default_attr2type[attr]
        return ImmPHFactory.gen_ph(ty, idx, attr)

class ImmPH(PH, SymbolValue):
    _ph_attr = PHType.IMM
    def __init__(self, ty, idx, attr):
        self._ty = ty
        self._idx = idx
        self._attr = attr
        
    def __repr__(self) -> str:
        return f'ImmPH({self.ty}, {self.idx}, {self.attr})'

    @property
    def ph_attr(self):
        return self._ph_attr
    def __eq__(self, __value) -> bool:
        assert isinstance(__value, self.__class__)
        if self._idx != __value._idx:
            return False
        if self._ty != __value._ty:
            return False
        if self._attr != __value._attr:
            return False
        return True
    
    def __hash__(self) -> int:
        return hash((self._ty, self._idx, self._attr))

    @property
    def is_unsigned(self):
        return self._ty in {'u32'}

    @property
    def ty(self):
        return self._ty

    @property
    def idx(self):
        return self._idx

    @property
    def attr(self):
        return self._attr
    @staticmethod
    def is_valid_str(s:str)->bool:
        if s.startswith('imm_'):
            s = s[4:]
            if s.isdigit():
                return True
        return False
    
    def get_symbol_name(self):
        return f'imm_{self.idx}'

    def get_val_symbol(self):
        symbol_name = self.get_symbol_name()
        if self.ty == 'i32' or self.ty == 'u32':
            val_symbol = BitVec(symbol_name, 32)
        elif self.ty == 'i64':
            val_symbol = BitVec(symbol_name, 64)
        elif self.ty == 'f32':
            val_symbol = FP(symbol_name, Float32())
        elif self.ty == 'f64':
            val_symbol = FP(symbol_name, Float64())
        elif self.ty == 'v128':
            val_symbol = BitVec(symbol_name, 128)
        elif self.ty == 'heaptype':
            val_symbol = BitVec(symbol_name, 32)
        elif self.ty == 'valtype':
            val_symbol = BitVec(symbol_name, 32)
        elif self.ty == 'funcref':
            val_symbol = BitVec(symbol_name, 32)
        elif self.ty == 'externref':
            val_symbol = BitVec(symbol_name, 32)
        else:
            raise NotImplementedError(f'Not implemented for {self.ty}')
        return val_symbol

    def get_symbol_and_constraints(self, context=None, ph_env=None):
        val = self.get_val_symbol()
        constraints = []
        if self.ty == 'u32':
            constraints.append(val >= 0)
        return val, constraints


class OperandPHFactory:
    _generated_objs ={}

    @staticmethod
    def get_operand_ph(ty, idx):
        if (ty, idx) not in OperandPHFactory._generated_objs:
            OperandPHFactory._generated_objs[(ty, idx)] = OperandPH(ty, idx)
        return OperandPHFactory._generated_objs[(ty, idx)]


class OperandPH(PH, SymbolValue):
    _ph_attr = PHType.OPERAND
    def __init__(self, ty, idx):
        assert ty in val_type_strs
        self._ty = ty
        self._idx = idx
    @property
    def ph_attr(self):
        return self._ph_attr

    @property
    def ty(self):
        return self._ty

    @staticmethod
    def is_valid_str(s:str)->bool:
        if s.startswith('op_'):
            s = s[3:]
            if s.isdigit():
                return True
        return False

    @property
    def idx(self):
        return self._idx

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, self.__class__)
        return self.idx == __value.idx and self.ty == __value.ty
    def __hash__(self) -> int:
        return hash((self.ty, self.idx))

    def __repr__(self):
        return f'OperandPH({self.ty}, {self.idx})'

    def get_symbol_name(self):
        return f'op_{self.idx}'
    
    def get_val_symbol(self):
        symbol_name = self.get_symbol_name()
        if self.ty == 'i32':
            val_symbol = BitVec(symbol_name, 32)
        elif self.ty == 'i64':
            val_symbol = BitVec(symbol_name, 64)
        elif self.ty == 'f32':
            val_symbol = FP(symbol_name, Float32())
        elif self.ty == 'f64':
            val_symbol = FP(symbol_name, Float64())
        elif self.ty == 'v128':
            val_symbol = BitVec(symbol_name, 128)
        elif self.ty == 'externref':
            val_symbol = BitVec(symbol_name, 32)
        elif self.ty == 'funcref':
            val_symbol = BitVec(symbol_name, 32)
        else:
            raise NotImplementedError(f'Not implemented for {self.ty}')
        return val_symbol

    def get_symbol_and_constraints(self, context=None, ph_env=None):
        return self.get_val_symbol(), []


def is_valid_op_name(s:str)->bool:
    if not isinstance(s, str):
        return False
    if s.startswith('op_'):
        s = s[3:]
        if s.isdigit():
            return True
    return False

def is_valid_imm_name(s:str)->bool:
    if not isinstance(s, str):
        return False
    if s.startswith('imm_'):
        s = s[4:]
        if s.isdigit():
            return True
    return False

def is_op_ty_desc_str(s:str)->bool:
    if s.startswith('op_') and s.endswith('.type'):
        return True
    return False


def is_default_imm_ph_name_or_op_ph_name(s:str)->bool:
    return ImmPH.is_valid_str(s) or OperandPH.is_valid_str(s)