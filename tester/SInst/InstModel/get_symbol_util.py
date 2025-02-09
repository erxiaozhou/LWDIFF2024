from ..InstModel.Expr import Expr, OneValExpr
from .Expr import BinExpr, CalcType, get_expr_from_str
from typing import Any, Optional, Tuple, List, Union
from .PHEnv import PHEnv
from z3 import BitVec, And, Or, BitVecRef, Extract


from extract_block_mutator.Context import Context
from ..InstModel.Exceptions import RequireContextException

from .PlaceHolder import PH, ImmPH, OperandPH, is_default_imm_ph_name_or_op_ph_name
from .SpecialOperand import SPECIAL_OP, ConstVal, ExternSpecialOpVal, F32SpecialVal, F64SpecialVal, FuncNullSpecialOpVal, HeapTypeVal, I32SpecialVal, I64SpecialVal, V128SpecialVal, ImmTypeVal
from .SpecialOperand import OffsetImmVal, AlignmentImmVal
from .specialContextConstVal import specialContextConstVal
from .PHEnv import PHEnv


ONE_VAL_TYPE = Union[ConstVal, specialContextConstVal, OperandPH, ImmPH, SPECIAL_OP]

def get_symbol_val_for_sc_val(sc_val:specialContextConstVal, context:Context, ph_env:Optional[PHEnv])->Tuple[Any, List]:
    if sc_val._is_unsolved_length_symbol():
        assert ph_env is not None
        val, inner_constraints = _get_symbol_for_unsolved_length(sc_val, context=context, ph_env=ph_env)
    elif sc_val.can_generate_val():
        val = sc_val.get_concrete_value(context)
        inner_constraints = []
    elif sc_val.can_get_scope():
        raise NotImplementedError(f'get_symbol_val not implemented for {sc_val}')
    else:
        raise NotImplementedError(f'get_symbol_val not implemented for {sc_val}')
    return val, inner_constraints




def _get_symbol_for_unsolved_length(sc_val:specialContextConstVal, context:Context, ph_env:PHEnv)->Tuple[Any, List]:
    symbol = BitVec(f'inter_{sc_val.idx_repr}', 32)
    # idx_ph: = ph_env.get_ph(self.idx_repr)
    assert sc_val.idx_repr is not None
    idx_expr = get_expr_from_str(sc_val.idx_repr, ph_env)
    idx_symbol_expr, inner_cs = get_val_symbol_for_expr(idx_expr, context=context, ph_env=ph_env)
    each_idx_exprs = []
    assert sc_val.has_parent_size()
    concrete_parent_size = sc_val.get_parent_size_val().get_concrete_value(context)

    idx_ge0 = symbol >= 0
    for possible_idx in range(concrete_parent_size):
        idx_eq_c = idx_symbol_expr == possible_idx
        # 
        cur_val_ = specialContextConstVal(
            sc_val.context_val_type,
            str(possible_idx),
            sc_val.val_attr
        )
        concrete_cur_val = cur_val_.get_concrete_value(context)
        ls_max_size_c = symbol < concrete_cur_val
        final_cur_idx_c = And(idx_eq_c, ls_max_size_c)
        each_idx_exprs.append(final_cur_idx_c)
    idx_c = Or(each_idx_exprs)
    return symbol, inner_cs + [idx_ge0, idx_c]

# OneValExpr =====================================================
def _get_val_symbol_for_one_val_expr(one_val_symbol:OneValExpr, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None)->Tuple[Any, List]:
    if isinstance(one_val_symbol.val, (ImmPH, OperandPH)):
        val = one_val_symbol.val.get_val_symbol()
        inner_constraints = []
        if isinstance(one_val_symbol.val, ImmPH):
            if one_val_symbol.val.ty == 'u32':
                inner_constraints.append(val >= 0)
    elif isinstance(one_val_symbol.val, (I32SpecialVal, I64SpecialVal, F32SpecialVal,F64SpecialVal, ConstVal, V128SpecialVal, FuncNullSpecialOpVal, ExternSpecialOpVal)):
        val = one_val_symbol.val.concrete_val()
        if val is None:
            raise ValueError(f'Failed to get symbl val for {one_val_symbol.val}')
        inner_constraints = []
    elif isinstance(one_val_symbol.val, specialContextConstVal):
        if context is None:
            raise RequireContextException(f'context is required for {one_val_symbol.val}')
        assert context is not None
        val, inner_constraints = get_symbol_val_for_sc_val(one_val_symbol.val, context=context, ph_env=ph_env)
    elif isinstance(one_val_symbol.val, (OffsetImmVal, AlignmentImmVal,HeapTypeVal, ImmTypeVal)):
        val = one_val_symbol.val.concrete_val()
        inner_constraints = []
        if val is None:
            raise ValueError(f'Failed to get symbl val for {one_val_symbol.val}')
    else:
        raise NotImplementedError(f'Failed to get symbl val for {one_val_symbol.val}')
    return  val, inner_constraints


def _get_lane_symbol(lane_idx:int, simd_val:BitVecRef, bw:int):
    return Extract((lane_idx + 1) * bw - 1, lane_idx * bw, simd_val)
    # return (simd_val >> (lane_idx * bw)) & ((1 << bw) - 1)

# BinValExpr =====================================================
def _get_val_symbol_for_bin_val_expr(bin_expr:BinExpr, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None)->Tuple[Any, List]:
    op1_symbol, op1_cs = get_val_symbol_for_expr(bin_expr.op1, context=context, ph_env=ph_env)
    op2_symbol, op2_cs = get_val_symbol_for_expr(bin_expr.op2, context=context, ph_env=ph_env)
    
    if bin_expr.calc_type == CalcType.Add:
        cur_symbol = op1_symbol + op2_symbol
    elif bin_expr.calc_type == CalcType.Sub:
        cur_symbol = op1_symbol - op2_symbol
    elif bin_expr.calc_type == CalcType.Mul:
        cur_symbol = op1_symbol * op2_symbol
    elif bin_expr.calc_type == CalcType.Div:
        cur_symbol = op1_symbol / op2_symbol
    else:
        raise ValueError(f"Unsupported CalcType: {bin_expr.calc_type}")
    return cur_symbol, op1_cs + op2_cs



def get_val_symbol_for_expr(val_symbol:Expr, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None)->Tuple[Any, List]:
    if isinstance(val_symbol, OneValExpr):
        return _get_val_symbol_for_one_val_expr(val_symbol, context=context, ph_env=ph_env)
    elif isinstance(val_symbol, BinExpr):
        return _get_val_symbol_for_bin_val_expr(val_symbol, context=context, ph_env=ph_env)
    raise ValueError(f'Failed to get val symbol for {val_symbol}')

