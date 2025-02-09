from .Expr import ONE_VAL_TYPE, OneValExpr
from .InstValRelation import InstValRelation
from .ExprConstraint import ExprConstraint
from typing import Union
from .Expr import BinExpr


def _preprocess_expr(val):
    if isinstance(val, (BinExpr, OneValExpr)):
        return val
    return OneValExpr(val)


class ExprConstraintFactory:
    @staticmethod
    def from_exprs(
                 expr1:Union[OneValExpr, BinExpr, ONE_VAL_TYPE], 
                 expr2:Union[OneValExpr, BinExpr, ONE_VAL_TYPE], 
                 relation:InstValRelation):
        expr1 = _preprocess_expr(expr1)
        expr2 = _preprocess_expr(expr2)
        # assert 0
        return ExprConstraint(expr1, expr2, relation)
