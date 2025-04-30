from typing import Any, Union

from SInst.InstModel.CombinedConstraint import CombinedAndConstraint
from SInst.InstModel.Constraint import Constraint
from SInst.InstModel.Expr import Expr
from SInst.InstModel.Expr.OneValExpr import OneValExpr
from SInst.InstModel.Expr.tool import is_context_size_expr
from SInst.InstModel.InstValRelation import InstValRelation
from SInst.InstModel.SelectFuncConstraintFactory import SelectFuncConstraintFactory
from SInst.InstModel.SpecialContextConstVal.SpecialContextConstVal import SpecialContextSizeVal
from SInst.InstModel.ValConstraint.EmptyValConstraint import EmptyValConstraint
from SInst.InstModel.ValConstraint.ExprConstraint import ExprConstraint
from ...ValConstraint import ValConstraint
from ...SelectFuncConstraint import SelectFuncConstraint, SelectFuncConstraintFactoryAnd


class IMConstraintResult:
    def __init__(self, val_constraint:ValConstraint, select_func_constraint:SelectFuncConstraint) -> None:
        self.val_constraint: ValConstraint = val_constraint
        self.select_func_constraint: SelectFuncConstraint = select_func_constraint

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val_constraint}, {self.select_func_constraint})'
    
    def __eq__(self, other):
        if not isinstance(other, IMConstraintResult):
            return False
        return self.val_constraint == other.val_constraint \
            and self.select_func_constraint == other.select_func_constraint


def get_imconstraint_result_practical(
    val_constraint:Union[ValConstraint, list[ValConstraint], None]=None,
    func_constraint:Union[SelectFuncConstraint, list[SelectFuncConstraint], None]=None
)->IMConstraintResult:
    val_constraints:list[ValConstraint] = get_constrains_from_various_repr(val_constraint)
    func_constraints:list[SelectFuncConstraint] = get_constrains_from_various_repr(func_constraint)
    for val_constraint in val_constraints:
        implied_func_constraints = _infer_select_constraint_from_val_constraint(val_constraint)
        func_constraints.extend(implied_func_constraints)
    if len(val_constraints) == 0:
        val_constraint = EmptyValConstraint()
    elif len(val_constraints) == 1:
        val_constraint = val_constraints[0]
    elif len(val_constraints) > 1:
        val_constraint = CombinedAndConstraint(val_constraints)

    
    if len(func_constraints) == 0:
        func_constraint = SelectFuncConstraintFactory.get_default_func_constraint()
    elif len(func_constraints) == 1:
        func_constraint = func_constraints[0]
    elif len(func_constraints) > 1:
        func_constraint = SelectFuncConstraintFactoryAnd.generate_a_combined_func_from_SelectFuncConstraints(func_constraints)
    if func_constraint is None or (isinstance(func_constraint, list) and len(func_constraint) == 0):
        func_constraint = SelectFuncConstraintFactory.get_default_func_constraint()
    
    assert isinstance(val_constraint, ValConstraint)
    assert isinstance(func_constraint, SelectFuncConstraint)
    return IMConstraintResult(val_constraint, func_constraint)



def get_constrains_from_various_repr(cs:Union[Any, list[Any],None])->list:
    if cs is None:
        return []
    elif isinstance(cs, Constraint):
        return [cs]
    elif isinstance(cs, list):
        return cs
    raise Exception(f'Invalid constraint(s): {cs}')


def _infer_select_constraint_from_val_constraint(val_constraint:ValConstraint)->list[SelectFuncConstraint]:
    if isinstance(val_constraint, ExprConstraint):
        expr1 = val_constraint.expr1
        expr2 = val_constraint.expr2
        relation = val_constraint.relation
        if is_context_size_expr(expr1) and relation.is_greater():
            ft0_c = get_gt0_func_constraint(expr1)
            return [ft0_c]
        if is_context_size_expr(expr2) and relation.is_less():
            ft0_c = get_gt0_func_constraint(expr2)
            return [ft0_c]
    return []

def get_gt0_func_constraint(expr:Expr)->SelectFuncConstraint:
    assert isinstance(expr, OneValExpr)
    val = expr.val
    assert isinstance(val, SpecialContextSizeVal)
    return SelectFuncConstraintFactory.compared_with_context_size_func(
        0, 
        val, 
        InstValRelation.LT
    )
