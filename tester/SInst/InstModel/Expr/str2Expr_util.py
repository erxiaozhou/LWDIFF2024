from ..CPlaceHolder import OperandPH
from .OpLaneVal import OpLaneVal
from .LaneDesc import LaneDesc
from .text_parsing_util import _extract_operation_core, get_tokens, is_lane_val_valid_str, is_valid_token
from ..SymbolValue import SymbolValue
from .OneValExpr import OneValExpr
from .BinExpr import BinExpr
from .util import CalcType
from ..PHEnv import PHEnv
from ..ConstVal import ConstVal
from ..SpecialContextConstVal.SpecialContextConstValFactory import SpecialContextConstValFactory
from .Expr import Expr



def get_one_val_expr(val_s: str, ph_env: PHEnv) -> OneValExpr:
    assert isinstance(val_s, str)
    if val_s in ph_env:
        inner_val = ph_env[val_s] # type: ignore
        assert isinstance(inner_val, SymbolValue)
    elif ConstVal.is_valid_str(val_s):
        inner_val = ConstVal.from_str(val_s)
    elif SpecialContextConstValFactory.is_valid_str(val_s):
        inner_val = SpecialContextConstValFactory.from_str(val_s)
    else:
        raise ValueError(f"Invalid value representation: {val_s}")
    return OneValExpr(inner_val)




def get_op_lane_val_expr(s:str, ph_env:PHEnv)->OpLaneVal:
        extracted_info = _extract_operation_core(s)
        assert extracted_info is not None
        ph_repr, lane_idx_repr = extracted_info
        lane_idx = int(lane_idx_repr)
        op_ph = ph_env.get_ph(ph_repr)
        assert isinstance(op_ph, OperandPH)  # may release the constraint in the future
        lane_type = ph_env.lane_type
        assert lane_type is not None, f'lane_type is None for {s}'
        return OpLaneVal(op_ph, LaneDesc(lane_idx, 
                                   lane_type))

def get_lane_val_expr(s:str, ph_env:PHEnv)->OpLaneVal:
    if OpLaneVal.is_valid_str(s):
        return get_op_lane_val_expr(s, ph_env)
    else:
        raise NotImplementedError

    






def get_bin_expr_from_str(expression: str, ph_env: PHEnv)->BinExpr:
    assert not is_valid_token(expression)
    def parse(tokens):
        def parse_term()->Expr:
            token = tokens.pop(0)
            if token == '(':
                expr = parse_expression()
                tokens.pop(0)  # Remove ')'
                return expr
            elif is_valid_token(token):
                if is_lane_val_valid_str(token):
                    return get_lane_val_expr(token, ph_env)
                else:
                    return get_one_val_expr(token, ph_env)
            

            raise SyntaxError(f"Invalid syntax: {token}")

        def parse_factor():
            term = parse_term()
            while tokens and tokens[0] in ('*', '/', '%'):
                op = tokens.pop(0)
                next_term = parse_term()
                if op == '*':
                    term = _get_expr_from_sub_exprs(
                        term, next_term, CalcType.Mul)
                elif op == '/':
                    term = _get_expr_from_sub_exprs(
                        term, next_term, CalcType.Div)
                elif op == '%':
                    term = _get_expr_from_sub_exprs(
                        term, next_term, CalcType.Mod)
            return term

        def parse_expression():
            factor = parse_factor()
            while tokens and tokens[0] in ('+', '-'):
                op = tokens.pop(0)
                next_factor = parse_factor()
                if op == '+':
                    factor = _get_expr_from_sub_exprs(
                        factor, next_factor, CalcType.Add)
                elif op == '-':
                    factor = _get_expr_from_sub_exprs(
                        factor, next_factor, CalcType.Sub)
            return factor

        return parse_expression()
    tokens = get_tokens(expression)
    expr = parse(tokens)
    assert isinstance(expr, BinExpr)
    return expr


def _get_expr_from_sub_exprs(s1:Expr, s2:Expr,calc_type: CalcType) -> BinExpr:
    return BinExpr(s1, s2, calc_type)

