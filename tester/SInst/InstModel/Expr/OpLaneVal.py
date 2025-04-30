from SInst.InstModel.Expr.OneValExpr import OneValExpr

from ..CPlaceHolder import OperandPH
from .LaneDesc import LaneDesc
from .LaneExpr import LaneExpr
from .text_parsing_util import is_lane_op_val_valid_str

class OpLaneVal(LaneExpr):
    def __init__(self, 
                 op_ph:OperandPH,
                 lane_desc:LaneDesc
                 ):
        self.op_ph = op_ph
        val = OneValExpr(op_ph)
        super().__init__(lane_desc, val)

    @staticmethod
    def is_valid_str(s:str):
        return is_lane_op_val_valid_str(s)
