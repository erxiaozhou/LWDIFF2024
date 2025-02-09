from typing import Optional
from .PlaceHolder import OperandPH, ImmPH
from .Constraint import Constraint
from z3 import BoolRef


class ValConstraint(Constraint):
    def __init__(self, 
                 related_imms:Optional[set[ImmPH]], 
                 related_ops:Optional[set[OperandPH]]):
        if related_imms is None:
            related_imms = set()
        self.related_imms = related_imms
        self.related_to_imm = len(related_imms) > 0
        
        if related_ops is None:
            related_ops = set()
        self.related_ops = related_ops
        
        self.related_to_op = len(related_ops) > 0
        
        self.related_to_both = self.related_to_imm and self.related_to_imm
    @property
    def related_imm_idxs(self)->set[int]:
        return {imm.idx for imm in self.related_imms}
    @property
    def related_op_idxs(self)->set[int]:
        return {op.idx for op in self.related_ops}
    
    @property
    def related_sybl_num(self):
        return len(self.related_imms) + len(self.related_ops)
    @property
    def related_multi_val(self):
        return self.related_sybl_num > 1
    def get_symbol_constraint(self,*args, **kwds)->BoolRef:
        raise NotImplementedError(f'Unimplemented for {self.__class__}')
