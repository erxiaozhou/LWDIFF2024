from ..SpecialContextConstVal.SpecialContextConstVal import SpecialContextConstVal
from ..CPlaceHolder import ImmPH, OperandPH
from ..SymbolValue import SymbolValue
from enum import Enum, auto


class ExprType(Enum):
    OneVal = auto()
    Uop = auto()
    BinOp = auto()


class Expr(SymbolValue):
    @property
    def related_imms(self) -> set[ImmPH]:
        raise NotImplementedError

    @property
    def related_ops(self) -> set[OperandPH]:
        raise NotImplementedError

    @property
    def contained_context_vals(self)->set[SpecialContextConstVal]:
        raise NotImplementedError 

    @property
    def invariant_in_context(self)->bool:
        return len(self.related_imms) == 0 and len(self.related_ops) == 0

    @property
    def is_constant(self)->bool:
        return len(self.related_imms) == 0 \
            and len(self.related_ops) == 0 \
            and len(self.contained_context_vals) == 0



