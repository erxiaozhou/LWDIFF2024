from SInst.InstModel.SpecialContextConstVal.SpecialContextConstVal import SpecialContextOneSecSize, SpecialContextSizeVal
from SInst.InstModel.SpecialContextConstVal.SpecialContextConstVal import SpecialContextConstVal
from .LaneExpr import LaneExpr
from ..PHEnv import PHEnv
from .OneValExpr import OneValExpr
from .BinExpr import BinExpr
from .text_parsing_util import is_lane_val_valid_str, is_valid_one_val_expr_core
from .str2Expr_util import get_bin_expr_from_str, get_lane_val_expr
from .UopExpr import UopExpr
from .str2Expr_util import get_one_val_expr
from .Expr import Expr
all_expr_types = [
    OneValExpr,
    BinExpr,
    LaneExpr
]


def is_expr_str(s:str)->bool:
    result = False
    for expr_type in all_expr_types:
        if expr_type.is_valid_str(s):
            result = True
            break
    return result


def get_expr_from_str(expr_repr:str, ph_env:PHEnv)->Expr: 
    assert isinstance(expr_repr, str)
    if is_valid_one_val_expr_core(expr_repr):
        val = get_one_val_expr(expr_repr, ph_env)
    elif is_lane_val_valid_str(expr_repr):
        val = get_lane_val_expr(expr_repr, ph_env)
    else:
        if expr_repr[0] == '-' or expr_repr[0] == '+':
            expr_repr = '0' + expr_repr
        val = get_bin_expr_from_str(expr_repr, ph_env)
    assert isinstance(val, Expr)
    return val

def is_context_size_expr(expr:Expr)->bool:
    if isinstance(expr, OneValExpr):
        val = expr.val
        if isinstance(val, SpecialContextSizeVal):
            return True
    return False
        
