from random import choice, randint, sample
from typing import List, Union, Optional

from extract_block_mutator.Context import Context
from ..InstModel.Expr import OneValExpr

from .specialContextConstVal import specialContextConstVal
from .PlaceHolder import OperandPH, ImmPH
from .InstValRelation import InstValRelation
from .SpecialOperand import  SpecialImmVal, SpecialAbOpVal
from .ExprConstraint import ExprConstraint


class OnePhConstraint(ExprConstraint):
    def __init__(self, ph:Union[OperandPH, ImmPH], val:Union[SpecialImmVal, SpecialAbOpVal, specialContextConstVal], relation:InstValRelation):
        self.ph = ph
        self.val = val

        expr1 = OneValExpr(self.ph)
        expr2 = OneValExpr(self.val)  # 
        super().__init__(expr1, expr2, relation)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.ph}, {self.val}, {self.relation})'

    def as_neg_constraint(self):
        return OnePhConstraint(self.ph, self.val, self.relation.neg())
    def can_neg(self):
        return True


def generate_OpEqConst(operand_ph:OperandPH, val:SpecialAbOpVal):
    return OnePhConstraint(operand_ph, val, InstValRelation.EQ)


