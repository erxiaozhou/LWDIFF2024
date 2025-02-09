from enum import Enum
from typing import Optional, Union

from .PlaceHolder import ImmPH, OperandPH

from .ValConstraint import ValConstraint


class NaiveSolveStrategy(Enum):
    One2One = 1
    One2Multi = 2


class NaiveSolvePreInfo:
    def __init__(self,
                 naive_solve_strategy: Optional[NaiveSolveStrategy],
                 ph2constraints: Optional[dict[Union[OperandPH, ImmPH],
                                               list[ValConstraint]]] = None
                 ):
        self._can_use_naive_solver = naive_solve_strategy is not None
        if naive_solve_strategy is not None:
            self._naive_solve_strategy = naive_solve_strategy
            self._ph2constraints = ph2constraints
        else:
            self._naive_solve_strategy = None
            self._ph2constraints = None

    @classmethod
    def empty_one(cls):
        return cls(None)

    @property
    def can_use_naive_solver(self) -> bool:
        return self._can_use_naive_solver

    @property
    def naive_solve_strategy(self):
        assert self._naive_solve_strategy is not None
        return self._naive_solve_strategy

    @property
    def ph2constraints(self):
        assert self._ph2constraints is not None
        return self._ph2constraints

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._naive_solve_strategy}, {self._ph2constraints})'