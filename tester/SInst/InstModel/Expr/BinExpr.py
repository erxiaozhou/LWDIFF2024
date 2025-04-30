# from SInst.InstModel import PHEnv, SymbolValue
from .text_parsing_util import get_tokens, is_valid_one_val_expr_core
from extract_block_mutator.Context import Context
from ..PHEnv import PHEnv
from .Expr import Expr
from .util import CalcType
from ..CPlaceHolder import ImmPH, OperandPH
from typing import List, Optional, Union, Any, Tuple


class BinExpr(Expr):
    def __init__(self, 
                 op1:Expr, 
                 op2:Expr, 
                 calc_type:CalcType):
        self.op1 = op1
        self.op2 = op2
        self.calc_type = calc_type


    def __repr__(self):
        return f"{self.__class__.__name__}({self.op1}, {self.op2}, {self.calc_type})"

    @staticmethod
    def is_valid_str(s: str) -> bool:
        if not isinstance(s, str):
            return False
        tokens = set(get_tokens(s))
        operators = set('+-*/%')
        tokens -= operators
        return all(is_valid_one_val_expr_core(token) for token in tokens)

    def get_symbol_and_constraints(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None)->Tuple[Any, List]:
        op1_symbol, op1_constraints = self.op1.get_symbol_and_constraints(context=context, ph_env=ph_env)
        op2_symbol, op2_constraints  = self.op2.get_symbol_and_constraints(context=context, ph_env=ph_env)
        if self.calc_type == CalcType.Add:
            symbol = op1_symbol + op2_symbol
        elif self.calc_type == CalcType.Sub:
            symbol = op1_symbol - op2_symbol
        elif self.calc_type == CalcType.Mul:
            symbol = op1_symbol * op2_symbol
        elif self.calc_type == CalcType.Div:
            symbol = op1_symbol / op2_symbol
        elif self.calc_type == CalcType.Mod:
            symbol = op1_symbol % op2_symbol
        else:
            raise ValueError(f"Unsupported calc type: {self.calc_type}")
        return symbol, op1_constraints + op2_constraints
            
    @property
    def contained_context_vals(self):
        vals = set()
        vals.update(self.op1.contained_context_vals)
        vals.update(self.op2.contained_context_vals)
        return vals
    
    @property
    def related_imms(self)->set[ImmPH]:
        vals = set()
        vals.update(self.op1.related_imms)
        vals.update(self.op2.related_imms)
        return vals
    
    @property
    def related_ops(self)->set[OperandPH]:
        vals = set()
        vals.update(self.op1.related_ops)
        vals.update(self.op2.related_ops)
        return vals


    def __eq__(self, o: 'BinExpr') -> bool:
        if not isinstance(o, BinExpr):
            return False
        return self.op1 == o.op1 \
            and self.op2 == o.op2 \
            and self.calc_type == o.calc_type

    def __hash__(self) -> int:
        return hash((self.op1, self.op2, self.calc_type))



