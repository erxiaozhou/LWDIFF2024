from SInst.InstModel.SelectFuncConstraintFactory import SelectFuncConstraintFactory
from .SymbolValue import SymbolValue
from .Expr.OneValExpr import OneValExpr
from .Expr.Expr import Expr
from .InstValRelation import InstValRelation
from .ValConstraint.ExprConstraint import ExprConstraint
from typing import Union


def _preprocess_expr(val):
    if isinstance(val, Expr):
        return val
    return OneValExpr(val)


class ExprConstraintFactory:
    @staticmethod
    def from_exprs_directly(
                 expr1:Union[Expr, SymbolValue], 
                 expr2:Union[Expr, SymbolValue], 
                 relation:InstValRelation):
        expr1 = _preprocess_expr(expr1)
        expr2 = _preprocess_expr(expr2)
        repr_ = f'{relation}   {expr1}   {expr2}'
        if expr1.invariant_in_context and expr2.invariant_in_context:
            print(repr_)
        return ExprConstraint(expr1, expr2, relation)

    @staticmethod
    def from_exprs_practically(
        expr1:Union[Expr, SymbolValue], 
        expr2:Union[Expr, SymbolValue], 
        relation:InstValRelation
    ):
        expr1 = _preprocess_expr(expr1)
        expr2 = _preprocess_expr(expr2)
        func_cs = []
        val_cs = []
        if expr1.invariant_in_context and expr2.invariant_in_context:
            assert not (expr1.is_constant and expr2.is_constant)  # ， check 。
            cur_relation = relation
            if expr2.is_constant:
                cur_expr1 = expr2
                cur_expr2 = expr1
                cur_relation = relation.reverse()
                
            else:
                cur_expr1 = expr1
                cur_expr2 = expr2
                cur_relation = relation
            func_c = SelectFuncConstraintFactory.compared_with_context_size_func(
                cur_expr1.val.n, 
                cur_expr2.val, 
                cur_relation)
            func_cs.append(func_c)
        else:
            val_cs.append(ExprConstraintFactory.from_exprs_directly(expr1, expr2, relation))
        return val_cs, func_cs