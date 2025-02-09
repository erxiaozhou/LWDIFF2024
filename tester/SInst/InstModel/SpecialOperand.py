from enum import Enum, auto
from random import choice, randint
import re
from typing import List, Union


from extract_block_mutator.Context import Context

from extract_block_mutator.InstUtil.InstFactory_util import  generate_randon_common_i32
from extract_block_mutator.InstUtil.InstFactory_util import generate_randon_i64
from extract_block_mutator.InstUtil.InstFactory_util import generate_randon_f32
from extract_block_mutator.InstUtil.InstFactory_util import generate_randon_f64
from .ExpExec import ExpExec
from numpy import inf

class NotIteratableEnum(Enum):
    def __iter__(self):
        raise Exception('Not iterable')

class I32SpecialVal(NotIteratableEnum):
    Zero = auto()
    One = auto()
    MinusOne = auto()
    Max = auto()
    Min = auto()
    Rdm = auto()
    PRdm = auto()

    def __iter__(self):
        raise Exception('Not iterable')

    def can_skip(self):
        return self == I32SpecialVal.Rdm
    def concrete_val(self, *arg, **kwds):
        if self == I32SpecialVal.PRdm:
            return generate_randon_common_i32()
        if self == I32SpecialVal.Zero:
            return 0
        if self == I32SpecialVal.One:
            return 1
        if self == I32SpecialVal.MinusOne:
            return -1
        if self == I32SpecialVal.Max:
            return 0x7fffffff
        if self == I32SpecialVal.Min:
            return -0x80000000
        if self == I32SpecialVal.Rdm:
            return randint(-0x80000000, 0x7fffffff)  # ，

class I64SpecialVal(NotIteratableEnum):
    Zero = auto()
    One = auto()
    MinusOne = auto()
    Max = auto()
    Min = auto()
    Rdm = auto()
    PRdm = auto()

    def can_skip(self):
        return self == I32SpecialVal.Rdm
    def concrete_val(self, *arg, **kwds):
        if self == I64SpecialVal.PRdm:
            return generate_randon_i64()
        if self == I64SpecialVal.Zero:
            return 0
        if self == I64SpecialVal.One:
            return 1
        if self == I64SpecialVal.MinusOne:
            return -1
        if self == I64SpecialVal.Max:
            return 0x7fffffffffffffff
        if self == I64SpecialVal.Min:
            return -0x8000000000000000
        if self == I64SpecialVal.Rdm:
            return randint(-0x8000000000000000, 0x7fffffffffffffff) # ，

class F32SpecialVal(NotIteratableEnum):
    P0 = auto()
    # N0 = auto()
    P1 = auto()
    # N1 = auto()
    Pinf = auto()
    Ninf = auto()
    Rdm = auto()

    def can_skip(self):
        return self == I32SpecialVal.Rdm
    def concrete_val(self, *arg, **kwds):
        if self == F32SpecialVal.P0:
            return 0.0
        # if self == F32SpecialVal.N0:
        #     return -0.0
        if self == F32SpecialVal.P1:
            return 1.0
        # if self == F32SpecialVal.N1:
        #     return -1.0
        if self == F32SpecialVal.Pinf:
            return inf
        if self == F32SpecialVal.Ninf:
            return -inf
        if self == F32SpecialVal.Rdm:
            return generate_randon_f32()

class F64SpecialVal(NotIteratableEnum):
    P0 = auto()
    # N0 = auto()
    P1 = auto()
    # N1 = auto()
    Pinf = auto()
    Ninf = auto()
    Rdm = auto()

    def can_skip(self):
        return self == I32SpecialVal.Rdm
    def concrete_val(self, *arg, **kwds):
        if self == F64SpecialVal.P0:
            return 0.0
        # if self == F64SpecialVal.N0:
        #     return -0.0
        if self == F64SpecialVal.P1:
            return 1.0
        # if self == F64SpecialVal.N1:
        #     return -1.0
        if self == F64SpecialVal.Pinf:
            return inf
        if self == F64SpecialVal.Ninf:
            return -inf
        if self == F64SpecialVal.Rdm:
            return generate_randon_f64()



class HeapTypeVal(NotIteratableEnum):
    func = 0
    extern = 1
    @classmethod
    def from_int(cls, i:int):
        if i == 0:
            return cls.func
        if i == 1:
            return cls.extern
        raise ValueError(f'Not valid for {i}')

    @staticmethod
    def is_valid_str(s:str) -> bool:
        if s == 'funcref':
            return True
        if s == 'externref':
            return True
        if s == 'func':
            return True
        if s == 'extern':
            return True
        return False

    @classmethod
    def from_str(cls, s:str):
        if s == 'funcref':
            return cls.func
        if s == 'externref':
            return cls.extern
        if s == 'func':
            return cls.func
        if s == 'extern':
            return cls.extern
        raise ValueError(f'Not valid for {s}')

    def concrete_val(self)->int:
        if self == HeapTypeVal.func:
            return 0
        if self == HeapTypeVal.extern:
            return 1
        raise ValueError(f'Not valid for {self}')

    def concrete_valtype(self):
        if self == HeapTypeVal.func:
            return 'funcref'
        if self == HeapTypeVal.extern:
            return 'externref'
        raise ValueError(f'Not valid for {self}')


    def concrete_imm_str(self):
        if self == HeapTypeVal.func:
            return 'funcref'
        if self == HeapTypeVal.extern:
            return 'externref'
        raise ValueError(f'Not valid for {self}')

class ImmTypeVal(Enum):
    I32 = auto()
    I64 = auto()
    F32 = auto()
    F64 = auto()
    V128 = auto()
    Funcref = auto()
    Externref = auto()
    @classmethod
    def from_int(cls, i:int):
        if i == 0:
            return cls.I32
        if i == 1:
            return cls.I64
        if i == 2:
            return cls.F32
        if i == 3:
            return cls.F64
        if i == 4:
            return cls.V128
        if i == 5:
            return cls.Funcref
        if i == 6:
            return cls.Externref
        raise ValueError(f'Not valid for {i}')
    @classmethod
    def from_str(cls, s:str):
        if s == 'i32':
            return cls.I32
        if s == 'i64':
            return cls.I64
        if s == 'f32':
            return cls.F32
        if s == 'f64':
            return cls.F64
        if s == 'v128':
            return cls.V128
        if s == 'funcref':
            return cls.Funcref
        if s == 'externref':
            return cls.Externref
        raise ValueError(f'Not valid for {s}')
    def concrete_val(self)->int:
        if self == ImmTypeVal.I32:
            return 0
        if self == ImmTypeVal.I64:
            return 1
        if self == ImmTypeVal.F32:
            return 2
        if self == ImmTypeVal.F64:
            return 3
        if self == ImmTypeVal.V128:
            return 4
        if self == ImmTypeVal.Funcref:
            return 5
        if self == ImmTypeVal.Externref:
            return 6
        raise ValueError(f'Not valid for {self}')
    def concrete_str(self):
        if self == ImmTypeVal.I32:
            return 'i32'
        if self == ImmTypeVal.I64:
            return 'i64'
        if self == ImmTypeVal.F32:
            return 'f32'
        if self == ImmTypeVal.F64:
            return 'f64'
        if self == ImmTypeVal.V128:
            return 'v128'
        if self == ImmTypeVal.Funcref:
            return 'funcref'
        if self == ImmTypeVal.Externref:
            return 'externref'
        raise ValueError(f'Not valid for {self}')
    
class RefReprVal(Enum):
    extern_null = 0
    funcref_null = 1

    @classmethod
    def from_int(cls, i:int):
        if i == 0:
            return cls.extern_null
        if i == 1:
            return cls.funcref_null
        raise ValueError(f'Not valid for {i}')
        
    def to_concrete_val(self)->int:
        if self == RefReprVal.extern_null:
            return 0
        if self == RefReprVal.funcref_null:
            return 1
        raise ValueError(f'Not valid for {self}')


class FuncNullSpecialOpVal(Enum):
    # TODO ， special val  ，，
    FuncNull = auto()
    ToSkip = auto()

    def generate_concrete_str(self, *arg, **kwds):
        # return 'funcref'
        raise NotImplementedError  # 
    def can_skip(self):
        return self == FuncNullSpecialOpVal.ToSkip
    def concrete_val(self):
        if self == FuncNullSpecialOpVal.FuncNull:
            return RefReprVal.funcref_null.to_concrete_val()
        raise ValueError(f'Not valid for {self}')


class ExternSpecialOpVal(Enum):
    ExternNull = auto()
    ToSkip = auto()
    
    def generate_concrete_str(self, *arg, **kwds):
        raise NotImplementedError  # 
    def can_skip(self):
        return self == ExternSpecialOpVal.ToSkip

    def concrete_val(self):  # repr
        if self == ExternSpecialOpVal.ExternNull:
            return RefReprVal.extern_null.to_concrete_val()
        raise ValueError(f'Not valid for {self}')


class V128SpecialVal(NotIteratableEnum):
    All0Vec = auto()
    All1Vec = auto()
    # ! ，
    Vec1 = auto()
    Vec2 = auto()
    Rdm = auto()
    # Vec3 = auto()

    def can_skip(self):
        return self == V128SpecialVal.Rdm

    def concrete_val(self, *arg, **kwds):
        if self == V128SpecialVal.All0Vec:
            return 0
        if self == V128SpecialVal.All1Vec:
            return sum([ 1<< (8*i) for i in range(16)])
        elif self == V128SpecialVal.Vec1:
            return sum([(255 * 256)<< (8*i) for i in range(8)])
        elif self == V128SpecialVal.Vec2:
            return 1 + (1<<64)
        elif self == V128SpecialVal.Rdm:
            return randint(0, 2**128-1)
        raise NotImplementedError
    

def v128val2str(ori_val):
    assert ori_val >= 0
    ba = bytearray(ori_val.to_bytes(16, 'big'))
    val_part = ' '.join([hex(x) for x in ba])
    full_repr = f'i8x16 {val_part}'
    return full_repr

def v1282byteseq(ori_val):
    assert ori_val >= 0
    ba = bytearray(ori_val.to_bytes(16, 'big'))
    return ba


SPECIAL_OP = Union[I32SpecialVal, I64SpecialVal, F32SpecialVal, F64SpecialVal, FuncNullSpecialOpVal, ExternSpecialOpVal, V128SpecialVal]

base_type2SpecialVal = {
    "i32": I32SpecialVal,
    "i64": I64SpecialVal,
    "f32": F32SpecialVal,
    "f64": F64SpecialVal,
    "v128": V128SpecialVal,
    "funcref": FuncNullSpecialOpVal,
    "externref": ExternSpecialOpVal
}


class TypeImmSpecialVal(NotIteratableEnum):
    I32 = auto()
    I64 = auto()
    F32 = auto()
    F64 = auto()
    V128 = auto()
    FuncRef = auto()
    ExternRef = auto()
    Rdm = auto()
    
    @classmethod
    def from_ty_str(cls, ty_str:str):
        if ty_str == "i32":
            return cls.I32
        if ty_str == "i64":
            return cls.I64
        if ty_str == "f32":
            return cls.F32
        if ty_str == "f64":
            return cls.F64
        if ty_str == "v128":
            return cls.V128
        if ty_str == "funcref":
            return cls.FuncRef
        if ty_str == "externref":
            return cls.ExternRef
        raise ValueError(f"Invalid type string {ty_str}")
    
common_2N = set([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
class AlignmentImmVal(NotIteratableEnum):
    
    
    One = auto()
    Two = auto()
    Four = auto()
    Invaid2N = auto()
    InvalidNaN = auto()
    # TODO ， 912
    # def __init__(self, *args, **kwds) -> None:
    #     self.ulimit = -1
    #     super().__init__(*args, **kwds)
    #     super().__init__()
    def set_ulimt(self, ulimit):
        self.ulimit = ulimit
    
    def concrete_val(self,*args, **kwds):
        ulimit = self.ulimit
        if self == AlignmentImmVal.One:
            return 1
        if self == AlignmentImmVal.Two:
            return 2
        if self == AlignmentImmVal.Four:
            return 4
        if self == AlignmentImmVal.Invaid2N:
            return choice([x for x in common_2N if x > ulimit])
        if self == AlignmentImmVal.InvalidNaN:
            possible_cals = set(range(1, ulimit+1))
            possible_cals = possible_cals - set(common_2N)
            assert len(possible_cals) > 0
            return choice(list(possible_cals))
        
        raise ValueError(f"Invalid AlignmentImmVal {self}")
    
class OffsetImmVal(NotIteratableEnum):  # !  RuleInst
    Zero = auto()
    One = auto()
    Max = auto()  # ，
    Valid = auto()
    PValid = auto()
    def concrete_val(self,*args, **kwds):
        ulimit = 0xffffffff
        if self == OffsetImmVal.PValid:
            return randint(0, 32768)
        if self == OffsetImmVal.Zero:
            return 0
        if self == OffsetImmVal.One:
            return 1
        if self == OffsetImmVal.Max:
            return ulimit
        if self == OffsetImmVal.Valid:
            # ! 
            return randint(0, 1024)
        raise ValueError(f"Invalid OffsetImmVal {self}")
   

class RefTypeImmVal(Enum):
    FuncRef = auto()
    ExternRef = auto()

class U32ImmVal(Enum):
    Zero = auto()
    One = auto()
    U32Max = auto()
    def exp_exec(self):
        if self == U32ImmVal.Zero:
            return ExpExec.Normal
        if self == U32ImmVal.One:
            return ExpExec.NotSure
        if self == U32ImmVal.U32Max:
            return ExpExec.Trap
        raise ValueError(f"Invalid U32ImmVal {self}")
    def concrete_val(self,*args,**kwds):
        if self == U32ImmVal.Zero:
            return 0
        if self == U32ImmVal.One:
            return 1
        if self == U32ImmVal.U32Max:
            return 0xffffffff
        raise ValueError(f"Invalid U32ImmVal {self}")

def is_float(s: str) -> bool:
    float_regex = re.compile(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$')
    return bool(float_regex.match(s))

class ConstVal:
    def __init__(self, n) -> None:
        self.n = n

    def concrete_val(self, *arg, **kwds):
        return self.n
  
    def can_skip(self):
        return False
    def __repr__(self) -> str:
        return f'ConstVal({self.n})'
    def __hash__(self) -> int:
        return hash(('ConstVal', self.n))

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ConstVal) and self.n == __value.n
    
    @staticmethod
    def is_const_val(s):
        # print('============xx===s', s)
        # assert 0
        if not isinstance(s, str):
            # return False
            s = str(s)
        # s = 
        # assert 0
        # print('===============s', s, is_float(s))
        if s.isdigit():
            return True
        if is_float(s):
            return True
        # if s.isf():
        #     return True
        if s.startswith('-') and s[1:].isdigit():
            return True
        if s.lower() in set(['inf', 'nan', 'infinity']):
            return True
        can_be = True
        try:
            eval(s)
        except:
            can_be = False
        return can_be
    @classmethod
    def from_str(cls, s:str):
        if s.isdigit():
            return cls(int(s))
        if s.startswith('-') and s[1:].isdigit():
            return cls(-int(s[1:]))
        if s.lower() in set(['inf', 'infinity']):
            return cls(float('inf'))
        if s.lower() in set(['nan']):
            return cls(float('nan'))
        return cls(eval(s))
        raise ValueError(f"Invalid const val str {s}")
    


SpecialAbOpVal = Union[I32SpecialVal, I64SpecialVal, F32SpecialVal, F64SpecialVal, V128SpecialVal, ExternSpecialOpVal, FuncNullSpecialOpVal, ConstVal]
SpecialImmVal = Union[RefTypeImmVal, TypeImmSpecialVal, AlignmentImmVal, OffsetImmVal, ConstVal, U32ImmVal]   # GlobalType，immattr imm 
