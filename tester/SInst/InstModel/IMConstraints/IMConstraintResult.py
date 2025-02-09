

from ..ValConstraint import ValConstraint
from ..SelectFuncConstraint import SelectFuncConstraint


class IMConstraintResult:
    def __init__(self, val_constraint:ValConstraint, select_func_constraint:SelectFuncConstraint) -> None:
        self.val_constraint: ValConstraint = val_constraint
        self.select_func_constraint: SelectFuncConstraint = select_func_constraint

    def __repr__(self) -> str:
        return f'IMConstraintResult({self.val_constraint}, {self.select_func_constraint})'
