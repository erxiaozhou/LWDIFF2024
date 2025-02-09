
from typing import Optional, Union
from enum import Enum, auto
import re

from util.util import FailedParsingException
from .PlaceHolder import PH, ImmPH, OperandPH, is_default_imm_ph_name_or_op_ph_name
from .SpecialOperand import SPECIAL_OP, AlignmentImmVal, ConstVal, ExternSpecialOpVal, F32SpecialVal, F64SpecialVal, FuncNullSpecialOpVal, HeapTypeVal, I32SpecialVal, I64SpecialVal, ImmTypeVal, OffsetImmVal, V128SpecialVal
from .specialContextConstVal import specialContextConstVal
from .PHEnv import PHEnv


ONE_VAL_TYPE = Union[ConstVal, specialContextConstVal, OperandPH, ImmPH, SPECIAL_OP]

class Expr:
    @property
    def related_imms(self):
        raise NotImplementedError
    @property
    def related_ops(self):
        raise NotImplementedError

    @property
    def contained_context_vals(self):
        raise NotImplementedError


class OneValExpr(Expr):
    # _default_op_
    def __init__(self, val:ONE_VAL_TYPE) -> None:
        self._check_val(val)
        self.val = val
        
    def _check_val(self, val):
        is_expected = False
        if isinstance(val, (ImmPH, OperandPH)):
            is_expected = True
        elif isinstance(val, (I32SpecialVal, I64SpecialVal, F32SpecialVal,F64SpecialVal, ConstVal, V128SpecialVal)):
            is_expected = True
        elif isinstance(val, specialContextConstVal):
            is_expected = True
        elif isinstance(val, (FuncNullSpecialOpVal, ExternSpecialOpVal)):
            is_expected = True
        elif isinstance(val, (OffsetImmVal, AlignmentImmVal)):
            is_expected = True
        elif isinstance(val, (HeapTypeVal, ImmTypeVal)):
            is_expected = True
        elif not is_expected:
            raise FailedParsingException(f'Unexpected value representation: {val}')
        assert is_expected

    @staticmethod
    def is_valid_str(s:str):
        if ConstVal.is_const_val(s):
            return True
        if specialContextConstVal.is_valid_str(s):
            return True
        if is_default_imm_ph_name_or_op_ph_name(s):
            return True
        return False

    @property
    def is_imm(self):
        return isinstance(self.val, ImmPH)

    @property
    def is_ph(self):
        return isinstance(self.val, (ImmPH, OperandPH))
    
    @property
    def related_imms(self):
        vals = []
        if isinstance(self.val, ImmPH):
            vals.append(self.val)
        return set(vals)

    @property
    def related_ops(self):
        vals = []
        if isinstance(self.val, OperandPH):
            vals.append(self.val)
        return set(vals)

    @property
    def contained_context_vals(self):
        vals = []
        if isinstance(self.val, specialContextConstVal):
            vals.append(self.val)
        return set(vals)

    def __repr__(self) -> str:
        return f'OneValExpr({self.val})'

    def __eq__(self, o: object) -> bool:
        # assert isinstance(o, OneValExpr)
        if not isinstance(o, OneValExpr):
            return False
        if not (type(self.val)==type(o.val)):
            return False
        return self.val == o.val

    def __hash__(self) -> int:
        return hash(self.val)


class CalcType(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()


class BinExpr(Expr):
    _from_str_p1 = re.compile(r'([^\+ ]+)\s*\+\s*([^\+ ]+)')
    def __init__(self, 
                 op1:Expr, 
                 op2:Expr, 
                 calc_type:CalcType):
        self.op1 = op1
        self.op2 = op2
        self.calc_type = calc_type


    def __repr__(self):
        return f"Expr({self.op1}, {self.op2}, {self.calc_type})"

    @staticmethod
    def is_valid_str(s):
        if not isinstance(s, str):
            return False
        tokens = set(_get_tokens(s))
        tokens = tokens - set('+-*/')
        for t in tokens:
            # print('-------', t, OneValExpr.is_valid_str(t))
            if not OneValExpr.is_valid_str(t):
                return False
        return True

    @property
    def contained_context_vals(self):
        vals = set()
        vals.update(self.op1.contained_context_vals)
        vals.update(self.op2.contained_context_vals)
        return vals
    
    @property
    def related_imms(self):
        vals = set()
        vals.update(self.op1.related_imms)
        vals.update(self.op2.related_imms)
        return vals
    
    @property
    def related_ops(self):
        vals = set()
        vals.update(self.op1.related_ops)
        vals.update(self.op2.related_ops)
        return vals


def get_expr_from_sub_exprs(s1:Union[str, BinExpr], 
                            s2:Union[str, BinExpr], 
                            ph_env:PHEnv, 
                            calc_type:CalcType):
    if isinstance(s1, str):
        v1 = get_one_val_expr(s1, ph_env)
        # print('ZZZZZZZWWW s1', s1, '|ph_env|', ph_env)
        assert v1 is not None
    else:
        v1 = s1
    if isinstance(s2, str):
        v2 = get_one_val_expr(s2, ph_env)
        assert v2 is not None
    else:
        v2 = s2
    return BinExpr(v1, v2, calc_type)



def get_one_val_expr(val_s:str, ph_env:PHEnv)->Optional[OneValExpr]:
    # p1: the val is an operand or imm
    val = _get_one_sybl_core(val_s, ph_env)
    if val is None:
        return None
    else:
        return OneValExpr(val)

def _get_one_sybl_core(val_s, ph_env):
    val = None
    if val_s in ph_env:
        val = ph_env[val_s]
    # p2: the val is a const
    if ConstVal.is_const_val(val_s):
        val = ConstVal.from_str(val_s)
    # p3: the val is a val indicated by the context
    try:
        val = specialContextConstVal.from_str(val_s)
    except NotImplementedError:
        pass
    return val




valid_token_p = re.compile(r'\w+')
invalid_chars = set('+-*/() ')
def _is_valid_token(token):
    chars = set(token)
    invalid_chars_in_token = chars & invalid_chars
    if len(invalid_chars_in_token) != 0:
        return False
    if not valid_token_p.findall(token):
        return False
    return True
    

# _token_pattern = re.compile(r'\s*(\d+|\w+|[+\-*/()])\s*')
_token_pattern = re.compile(r'\s*((?:[\d\w\.\[\]]+)|[+\-*/()])\s*')
_token_pattern = re.compile(r'\s*((?:[\d\w\.\[\]]+)|(?:[+\-*/()]+))\s*')
def _get_tokens(expr):
    tokens = _token_pattern.findall(expr)
    # print('OQWDKLCALC   tokens', tokens)
    # for token in tokens:
    #     if not valid_token_p.findall(token):
    #         raise FailedParsingException(f"Invalid token: {token}")
    return [token for token in tokens if token.strip()]

def _get_bin_expr_from_str(expression:str, ph_env:PHEnv):
    def parse(tokens):
        def parse_term():
            # print('DSFSFSD tokens', tokens)
            # print(tokens[0], _is_valid_token(tokens[0]))
            token = tokens.pop(0)
            if token == '(':
                expr = parse_expression()
                tokens.pop(0)  # Remove ')'
                return expr
            elif _is_valid_token(token):
                return token
            # print()
            raise SyntaxError(f"Invalid syntax: {token}")

        def parse_factor():
            term = parse_term()
            while tokens and tokens[0] in ('*', '/'):
                op = tokens.pop(0)
                next_term = parse_term()
                if op == '*':
                    term = get_expr_from_sub_exprs(term, next_term, ph_env, CalcType.Mul)
                elif op == '/':
                    term = get_expr_from_sub_exprs(term, next_term, ph_env, CalcType.Div)
            return term

        def parse_expression():
            factor = parse_factor()
            while tokens and tokens[0] in ('+', '-'):
                op = tokens.pop(0)
                next_factor = parse_factor()
                if op == '+':
                    factor = get_expr_from_sub_exprs(factor, next_factor, ph_env, CalcType.Add)
                elif op == '-':
                    factor = get_expr_from_sub_exprs(factor, next_factor, ph_env, CalcType.Sub)
            return factor

        return parse_expression()

    tokens = _get_tokens(expression)
    # print('expression', expression, '|tokens|', tokens, len(tokens))
    return parse(tokens)


def get_expr_from_str(expression, ph_env): 
    # print('expression', expression, type(expression))
    val = get_one_val_expr(expression, ph_env)
    if val is None:
        if expression[0] == '-' or expression[0] == '+':
            expression = '0' + expression
        val = _get_bin_expr_from_str(expression, ph_env)
    return val

def is_expr_str(s:str)->bool:
    if OneValExpr.is_valid_str(s):
        return True
    if BinExpr.is_valid_str(s):
        return True
    return False

