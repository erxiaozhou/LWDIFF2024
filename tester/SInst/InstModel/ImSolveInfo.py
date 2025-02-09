from typing import List, Optional
from .IMConstraints.IMConstraint import IMConstraint
from .PHEnv import PHEnv


class ImSolveInfo:
    def __init__(self,
                 ph_env: PHEnv,
                 im_constraints: List[IMConstraint],
                 all_constraints,
                 is_valid: bool,
                 trap_: Optional[bool] = None) -> None:
        self.ph_env = ph_env
        self.im_constraints = im_constraints
        self.all_constraints = all_constraints
        self.is_valid = is_valid
        if trap_ is None:
            if not is_valid:
                trap_ = True
        self.trap_ = trap_
        if not is_valid:
            assert trap_

    def __repr__(self) -> str:
        return f'ImSolveInfo({self.ph_env}, {self.im_constraints}, {self.all_constraints}, {self.is_valid}, {self.trap_})'

