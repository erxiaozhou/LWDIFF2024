from typing import List, Union
from ..CombinedConstraint import CombinedOrConstraint
from ..ExprConstraintFactory import ExprConstraintFactory
from ..InstValRelation import InstValRelation
from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory

from ..SpecialOperand import ConstVal, HeapTypeVal
from .IMConstraintResult import IMConstraintResult
from .IMConstraint import IMConstraint

SUPPORT_IMM_TYPES = Union[HeapTypeVal]


class NaiveImmScope(IMConstraint):
    def __init__(self, imm_repr:str, attrs:set, is_inclusive:bool):
        self.imm_repr = imm_repr
        self.attrs = attrs
        self.is_inclusive = is_inclusive
        # ! 
        assert is_inclusive
    def can_neg(self) -> bool:
        return False
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.imm_repr}, {self.attrs}, {self.is_inclusive})'
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3 and set(d.keys()) == {'v1', 'v2', 'relation'}:
            if d['relation'] == 'in':
                if isinstance(d['v2'], list):
                    if isinstance(d['v1'], str):
                        if d['v1'].startswith('imm_') and d['v1'][4:].isdigit():
                            return True
        return False
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        imm_name = d['v1']
        attrs = [_get_attr_from_str(s) for s in d['v2']]
        return cls(imm_name, set(attrs), d['relation'] == 'in')

    def release_both_constraints(self, ph_env,*args, **kwds)->List[IMConstraintResult]:
        # raise NotImplementedError(f'{self.__class__.__name__}.release_both_constraints not implemented: {self}')
        v1 = ph_env.get_ph(self.imm_repr)
        cs = []
        for target_v in self.attrs:
            val_c = self._get_single_val_constraint(ph_env, target_v)
            cs.append(val_c)
        final_val_c = CombinedOrConstraint(cs)
        select_c = SelectFuncConstraintFactory.get_default_func_constraint()

        result = IMConstraintResult(final_val_c, select_c)
        return [result]


    def _get_single_val_constraint(self, ph_env, target_v:SUPPORT_IMM_TYPES):
        v1 = ph_env.get_ph(self.imm_repr)
        # v2 = 
        val_c = ExprConstraintFactory.from_exprs(v1, target_v,InstValRelation.EQ)
        return val_c
        


def _get_attr_from_str(s:str):
    if HeapTypeVal.is_valid_str(s):
        return HeapTypeVal.from_str(s)
    if s.isdigit():
        return ConstVal.from_str(s)
    raise NotImplementedError(f'_get_attr_from_str not implemented for {s}')

