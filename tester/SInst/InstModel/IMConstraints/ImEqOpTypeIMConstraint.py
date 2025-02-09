from ..ExprConstraintFactory import ExprConstraintFactory
from ..IMConstraints.IMConstraintResult import IMConstraintResult
from ..IMConstraints.util import OPTypeUndeterminedException
from ..InstValRelation import InstValRelation
from ..PHEnv import PHEnv
from ..SpecialOperand import ImmTypeVal
from .IMConstraint import IMConstraint
from typing import List
from ..PlaceHolder import is_valid_imm_name
from ..PlaceHolder import ImmPH, OperandPH, is_op_ty_desc_str
from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory


class ImEqOpTypeIMConstraint(IMConstraint):
    def __init__(self, op_repr, imm_repr, is_eq) -> None:
        self.op_repr = op_repr
        self.imm_repr = imm_repr
        self.is_eq = is_eq
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.op_repr}, {self.imm_repr}, {self.is_eq})"

    def can_neg(self) -> bool:
        return True
    
    def as_neg_constraint(self):
        return ImEqOpTypeIMConstraint(self.op_repr, self.imm_repr, not self.is_eq)

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if set(d.keys()) == {'v1', 'v2', 'relation'}:
            if is_op_ty_desc_str(d['v1']) and is_valid_imm_name(d['v2']):
                if d['relation'] == 'eq':
                    return True
        return False

    @classmethod
    def from_dict(cls, d:dict):
        assert cls.is_valid_dict(d)
        op_repr = d['v1'][:-5]
        imm_repr = d['v2']
        eq = d['relation'] == 'eq'
        return cls(op_repr, imm_repr, eq)
   
    def release_both_constraints(self, ph_env:PHEnv, *args, **kwds)->List[IMConstraintResult]:
        select_func_constraint = SelectFuncConstraintFactory.get_default_func_constraint()
        try:
            # print(ph_env,'ngikdhgilds', ph_env.determined)
            op_ph = ph_env.get_ph(self.op_repr)
            assert isinstance(op_ph, OperandPH)
            op_type:str = op_ph.ty
            imm_ph = ph_env.get_ph(self.imm_repr)
            assert isinstance(imm_ph, ImmPH)
            symbolized_type_val = _get_symbolized_type_from_str(op_type)
            val_c = ExprConstraintFactory.from_exprs(imm_ph, symbolized_type_val,InstValRelation.EQ)
            results = [
                IMConstraintResult(val_c, select_func_constraint)
            ]
            return results
            # raise NotImplementedError(f'self is {self}')
        except KeyError as e:
            if  'op_' in str(e):
                raise OPTypeUndeterminedException(f'op type is undetermined')
            raise e

def _get_symbolized_type_from_str(s:str)->ImmTypeVal:
    # assert
    return ImmTypeVal.from_str(s)
 