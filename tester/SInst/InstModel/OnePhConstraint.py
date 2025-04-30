from typing import Union

from .Expr.OneValExpr import OneValExpr

from .SpecialContextConstVal.SpecialContextConstVal import SpecialContextConstVal
from .CPlaceHolder import OperandPH, ImmPH
from .InstValRelation import InstValRelation
from .ValConstraint.ExprConstraint import ExprConstraint
from .ConstVal import ConstVal
from .CVasSymVal import CVasSymVal


class OnePhConstraint(ExprConstraint):
    def __init__(self, ph:Union[OperandPH, ImmPH], val:Union[CVasSymVal, SpecialContextConstVal, ConstVal], relation:InstValRelation):
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


def generate_OpEqConst(operand_ph:OperandPH, val):
    return OnePhConstraint(operand_ph, val, InstValRelation.EQ)


