from typing import List

from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory
from .IMConstraint import IMConstraint
from .IMConstraintResult import IMConstraintResult
from ..CombinedConstraint import CombinedAndConstraint
from ..ValConstraint import ValConstraint
from ..SelectFuncConstraint import SelectFuncConstraint, SelectFuncConstraintFactoryAnd


class AssignedIMConstraint(IMConstraint):
    def __init__(self, 
                    val_constraints:List[ValConstraint],
                    select_func_constraints:List[SelectFuncConstraint]) -> None:
        self.val_constraints = val_constraints
        self.select_func_constraints = select_func_constraints

    @classmethod
    def from_val_constraints(cls, val_constraints:List[ValConstraint]):
        return cls(val_constraints, [
            SelectFuncConstraintFactory.get_default_func_constraint()
        ])
        
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val_constraints}, {self.select_func_constraints})'
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        return False
    
    @classmethod
    def from_dict(cls, d: dict):
        raise ValueError('This class is not supposed to be used in this way')
    
    def can_neg(self) -> bool:
        return False
        
    def as_neg_constraint(self):
        raise ValueError('This class is not supposed to be used in this way')
    
    def release_both_constraints(self, *args, **kwds)->List[IMConstraintResult]:
        if len(self.val_constraints) == 1:
            val_c = self.val_constraints[0]
        else:
            val_c = CombinedAndConstraint(self.val_constraints)
        func_c = SelectFuncConstraintFactoryAnd.generate_a_combined_func_from_SelectFuncConstraints(self.select_func_constraints)
        results = [
            IMConstraintResult(
                val_c,
                func_c
            )
        ]
        return results
    

