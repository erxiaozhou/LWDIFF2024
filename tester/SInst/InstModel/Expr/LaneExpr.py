from typing import Any, List, Optional, Tuple
from SInst.InstModel.Expr.text_parsing_util import is_lane_val_valid_str
from SInst.InstModel.PHEnv import PHEnv
from .get_lane_symbol_smry_util import get_lane_symbol_smry
from extract_block_mutator.Context import Context
from .LaneDesc import LaneDesc
from ..CPlaceHolder import ImmPH, OperandPH
from ..Expr import Expr
from .UopExpr import UopExpr


class LaneExpr(UopExpr):
    def __init__(self, 
                 lane_desc:LaneDesc,
                 val:Expr) -> None:
        self.lane_desc = lane_desc
        self.val = val
        
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.lane_desc}, {self.val})"

    def __hash__(self) -> int:
        return hash((self.lane_desc, self.val))
    
    def __eq__(self, o: 'LaneExpr') -> bool:
        if not isinstance(o, LaneExpr):
            return False
        return self.lane_desc == o.lane_desc \
            and self.val == o.val

    @staticmethod
    def is_valid_str(s:str)->bool:
        return is_lane_val_valid_str(s)

    @property
    def related_imms(self)->set[ImmPH]:
        return self.val.related_imms

    @property
    def related_ops(self)->set[OperandPH]:
        return self.val.related_ops

    @property
    def contained_context_vals(self):
        return self.val.contained_context_vals

    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> Tuple[Any, List]:
        inner_symbol, inner_constraints = self.val.get_symbol_and_constraints(context=context, ph_env=ph_env)
        val = get_lane_symbol_smry(self.lane_desc, inner_symbol)
        return val, inner_constraints
