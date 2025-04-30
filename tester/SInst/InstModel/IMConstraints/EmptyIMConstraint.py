from .IMConstraintResult import IMConstraintResult, get_imconstraint_result_practical
from .IMConstraint import IMConstraint


class EmptyIMConstraint(IMConstraint):
    def __init__(self) -> None:
        assert 0
        pass

    def release_both_constraints(self, *args, **kwds)->list[IMConstraintResult]:
        results = [get_imconstraint_result_practical()]
        return results
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3:
            if all(len(v)==0 for v in d.values()):
                return True
        return False
    
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        return cls()
    def can_neg(self) -> bool:
        return False

