from .text_parsing_util import is_valid_one_val_expr_core
from .Expr import Expr
from ..CPlaceHolder import ImmPH, OperandPH
from ..SpecialContextConstVal.SpecialContextConstVal import SpecialContextConstVal
from ..SymbolValue import SymbolValue
from typing import Any, List, Optional, Tuple
from extract_block_mutator.Context import Context
from ..PHEnv import PHEnv


class OneValExpr(Expr):
    def __init__(self, val: SymbolValue) -> None:
        if isinstance(val, self.__class__):
            val = val.val
        assert isinstance(val, SymbolValue)
        
        self.val = val

    @staticmethod
    def is_valid_str(s: str) -> bool:
        return is_valid_one_val_expr_core(s)    

    @property
    def is_imm(self):
        return isinstance(self.val, ImmPH)

    @property
    def is_ph(self):
        return isinstance(self.val, (ImmPH, OperandPH))

    @property
    def related_imms(self) -> set[ImmPH]:
        vals = []
        if isinstance(self.val, ImmPH):
            vals.append(self.val)
        return set(vals)

    @property
    def related_ops(self) -> set[OperandPH]:
        vals = []
        if isinstance(self.val, OperandPH):
            vals.append(self.val)
        return set(vals)

    @property
    def contained_context_vals(self):
        vals = []
        if isinstance(self.val, SpecialContextConstVal):
            vals.append(self.val)
        return set(vals)

    def __repr__(self) -> str:
        return f'OneValExpr({self.val})'

    def __eq__(self, o: 'OneValExpr') -> bool:
        if not isinstance(o, OneValExpr):
            return False
        if not (type(self.val) == type(o.val)):
            return False
        if self.val == o.val:
            return True
        if str(self.val) == str(o.val):
            return True
        return False

    def __hash__(self) -> int:
        return hash(self.val)

    def get_symbol_and_constraints(self, context: Optional[Context], ph_env: Optional[PHEnv]) -> Tuple[Any, List]:
        return self.val.get_symbol_and_constraints(context=context, ph_env=ph_env)
