from z3 import And, BoolRef, Or
from typing import List, Optional
from extract_block_mutator.Context import Context
from .PHEnv import PHEnv

from .ValConstraint import ValConstraint

class CombinedConstraint(ValConstraint):
    def __init__(self, constraints:List[ValConstraint]):
        self.constraints = constraints
        related_imms = set()
        related_ops = set()
        for c in constraints:
            related_imms.update(c.related_imms)
            related_ops.update(c.related_ops)
        # related_phs = []
        
        super().__init__(related_imms, related_ops)

class CombinedAndConstraint(CombinedConstraint):
    def __init__(self, constraints):
        super().__init__(constraints)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.constraints})'

    def get_symbol_constraint(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None):
        z3_cs = []
        for c in self.constraints:
            # print('GSF c', c)
            z3_c = c.get_symbol_constraint(context=context, ph_env=ph_env)
            assert isinstance(z3_c, (BoolRef, bool)), print('==== z3_c ====\n', z3_c)
            z3_cs.append(z3_c)
        if len(z3_cs) == 0:
            return True
        elif len(z3_cs) == 1:
            return z3_cs[0]
        else:
            return And(z3_cs)


class CombinedOrConstraint(CombinedConstraint):
    def __init__(self, constraints):
        super().__init__(constraints)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.constraints})'

    def get_symbol_constraint(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None):
        z3_cs = []
        for c in self.constraints:
            z3_c = c.get_symbol_constraint(context=context, ph_env=ph_env)
            assert isinstance(z3_c, BoolRef)
            z3_cs.append(z3_c)
        if len(z3_cs) == 0:
            raise ValueError('len(z3_cs) == 0')
        elif len(z3_cs) == 1:
            return z3_cs[0]
        else:
            return Or(z3_cs)