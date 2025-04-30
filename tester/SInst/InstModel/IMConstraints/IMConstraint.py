from typing import List, Tuple
from ..Constraint import Constraint
from .IMConstraintResult import IMConstraintResult

class IMConstraint(Constraint): 
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        raise NotImplementedError
        
    @classmethod
    def from_dict(cls, d:dict):
        raise NotImplementedError

    def can_neg(self) -> bool:
        raise NotImplementedError

    def as_neg_constraint(self):
        raise NotImplementedError(f'self is {self}')

    def release_both_constraints(self, *args, **kwds)->List[IMConstraintResult]:
        raise NotImplementedError(f'self is {self}')
