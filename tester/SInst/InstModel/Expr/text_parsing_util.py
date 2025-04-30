from ..CPlaceHolder import ImmPH, OperandPH
from ..ConstVal import ConstVal
from ..SpecialContextConstVal.SpecialContextConstValFactory import SpecialContextConstValFactory
import re


str_representable_classes = [
    ConstVal,
    OperandPH,
    ImmPH,
    SpecialContextConstValFactory
]


def is_valid_one_val_expr_core(s: str) -> bool:
    if not isinstance(s, str):
        return False
    result = any(cls.is_valid_str(s) for cls in str_representable_classes)
    return result




def is_lane_val_valid_str(s: str) -> bool:
    return is_lane_op_val_valid_str(s)




def is_lane_op_val_valid_str(s: str) -> bool:
    return _extract_operation_core(s) is not None

_p1 = re.compile(r'^(op_\d+)\.(?:lane|element)_(\d+)$')
_p2 = re.compile(r'^(op_\d+)(?:(?:\.lane)|(?:\.element))?\[(\d+)\]')
def _extract_operation_core(text):
    r1 = _p1.findall(text)
    if r1:
        return r1[0]
    r2 = _p2.findall(text)
    if r2:
        return r2[0]
    return None



valid_token_p = re.compile(r'\w+')
invalid_chars = set('+-*%/() ')


def is_valid_token(token):
    chars = set(token)
    invalid_chars_in_token = chars & invalid_chars
    if len(invalid_chars_in_token) != 0:
        return False
    if not (is_valid_one_val_expr_core(token) or is_lane_op_val_valid_str(token)):
        return False
    return True


_token_pattern = re.compile(r'\s*((?:[\d\w\.\[\]]+)|[+\-\*%/()])\s*')
_token_pattern = re.compile(r'\s*((?:[\d\w\.\[\]]+)|(?:[+\-%\*/()]+))\s*')


def get_tokens(expr):
    tokens = _token_pattern.findall(expr)
    result = [token for token in tokens if token.strip()]
    return result


