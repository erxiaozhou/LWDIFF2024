from random import choice, randint
from extract_block_mutator.Context import Context
from .CombinedConstraint import CombinedAndConstraint, CombinedOrConstraint
from .InstValRelation import InstValRelation
from .PlaceHolder import ImmPH, OperandPH
from .ScopeValConstraint import ExprInContextScope
from .get_symbol_util import _get_val_symbol_for_one_val_expr
from .Expr import OneValExpr, Expr
from .ExprConstraint import ExprConstraint
from .ValConstraint import ValConstraint
from typing import List, Optional, Union
from .OpImmValSoluiton import OpImmValSoluiton
from .Exceptions import UNSolveException


class OneValConstraintSolver:
    @staticmethod
    def is_can_solve_constraint(c:ValConstraint)->bool:
        raise NotImplementedError(f'Unimplemented for {c.__class__}')
    
    @staticmethod
    def solve_constraint(c:ValConstraint, context: Context)->dict[str, Union[int, float, str]]:
        raise NotImplementedError(f'Unimplemented for {c.__class__}')

    @staticmethod
    def has_finite_candis(c:ValConstraint)->bool:
        raise NotImplementedError(f'Unimplemented for {c.__class__}')

    @staticmethod
    def get_a_random_candidate(c:ValConstraint, context:Context)->Union[int, float, str]:
        raise NotImplementedError(f'Unimplemented for {c.__class__}')


class FiniteOneValConstraintSolver(OneValConstraintSolver):
    @staticmethod
    def has_finite_candis(c:ValConstraint)->bool:
        raise NotImplementedError(f'Unimplemented for {c.__class__}')


    @staticmethod
    def get_all_candis(c:ValConstraint, context: Context)->List[OpImmValSoluiton]:
        raise NotImplementedError(f'Unimplemented for {c.__class__}')
    

class EqExprConstraintNaiveSolver(FiniteOneValConstraintSolver):
    @staticmethod
    def is_can_solve_constraint(c:ValConstraint)->bool:
        if not isinstance(c, ExprConstraint):
            return False
        expr1 = c.expr1
        expr2 = c.expr2
        if not isinstance(expr1, OneValExpr):
            return False
        if not isinstance(expr2, OneValExpr):
            return False
        if not expr1.is_ph:
            return False
        # assert 0
        # pattern 1
        if c.relation ==  InstValRelation.EQ:
            if (not isinstance(expr2.val, (ImmPH, OperandPH))):
                return True
        return False

    @staticmethod
    def has_finite_candis(c:ValConstraint)->bool:
        if EqExprConstraintNaiveSolver.is_can_solve_constraint(c):
            return True
        return False

    @staticmethod
    def get_all_candis(c: ValConstraint, context: Context) -> set:
        assert isinstance(c, ExprConstraint)
        expr2 = c.expr2
        assert isinstance(expr2, OneValExpr)
        val, cs = _get_val_symbol_for_one_val_expr(expr2, context=context)
        return {val}

    @staticmethod
    def get_a_random_candi(c: ExprConstraint, context: Context) ->  Union[int, float, str]:
        all_candis = EqExprConstraintNaiveSolver.get_all_candis(c, context)
        all_candi_list = list(all_candis)
        assert len(all_candi_list) == 1
        return all_candi_list[0]
        
    @staticmethod
    def solve_constraint(c:ValConstraint, context: Context)->dict[str, Union[int, float, str]]:
        assert isinstance(c, ExprConstraint)
        expr1 = c.expr1
        assert isinstance(expr1, OneValExpr)
        assert isinstance(expr1.val, (ImmPH, OperandPH))
        name = expr1.val.get_symbol_name()
        val = EqExprConstraintNaiveSolver.get_a_random_candi(c, context)
        assert isinstance(val, (int, float, str)), print('An invalid value:', val)
        return {name: val}


class LCExprConstraintNaiveSolver(FiniteOneValConstraintSolver):
    @staticmethod
    def is_can_solve_constraint(c:ValConstraint)->bool:
        if not isinstance(c, ExprConstraint):
            return False
        expr1 = c.expr1
        expr2 = c.expr2
        if not isinstance(expr1, OneValExpr):
            return False
        if not isinstance(expr2, OneValExpr):
            return False
        if not expr1.is_ph:
            return False
        
        if c.relation in {InstValRelation.LE, InstValRelation.LT} and expr1.is_imm:
            imm_val = expr1.val
            # just check
            assert isinstance(imm_val, ImmPH)
            # assert 0, imm_val.is_unsigned
            if imm_val.is_unsigned:
                return True
        return False
        
    @staticmethod
    def has_finite_candis(c:ValConstraint)->bool:
        if LCExprConstraintNaiveSolver.is_can_solve_constraint(c):
            return True
        return False
    

    @staticmethod
    def get_all_candis(c: ValConstraint, context: Context) -> set:
        assert isinstance(c, ExprConstraint)
        expr2 = c.expr2
        assert isinstance(expr2, OneValExpr)
        max_val = LCExprConstraintNaiveSolver._determin_max(c, context, expr2)
        
        return set(range(max_val+1))
        
    @staticmethod
    def get_a_random_candi(c: ExprConstraint, context: Context) ->  Union[int, float, str]:
        assert isinstance(c, ExprConstraint)
        expr2 = c.expr2
        assert isinstance(expr2, OneValExpr)
        max_val = LCExprConstraintNaiveSolver._determin_max(c, context, expr2)
        concrete_val = randint(0, max_val)
        return concrete_val

    @staticmethod
    def _determin_max(c, context, expr2):
        max_val, cs = _get_val_symbol_for_one_val_expr(expr2, context=context)
        if isinstance(max_val, float):
            if max_val - int(max_val) < 1e-6:
                max_val = int(max_val)
            else:
                raise ValueError(f'An invalid value: {max_val}, {c}')
        elif isinstance(max_val, str):
            raise ValueError(f'An invalid value: {max_val}, {c}')
        if max_val == 0 and c.relation == InstValRelation.LT:
            raise UNSolveException
        if c.relation == InstValRelation.LT:
            max_val -= 1
        return max_val
    
    @staticmethod
    def solve_constraint(c:ValConstraint, context: Context)->dict[str, Union[int, float, str]]:
        assert isinstance(c, ExprConstraint)
        expr1 = c.expr1
        assert isinstance(expr1, OneValExpr)
        assert isinstance(expr1.val, ImmPH)
        assert expr1.val.is_unsigned
        name = expr1.val.get_symbol_name()
        candi = LCExprConstraintNaiveSolver.get_a_random_candi(c, context)
        return {name:candi}


class ScopeValConstraintSolver(FiniteOneValConstraintSolver):
    @staticmethod
    def is_can_solve_constraint(c:ValConstraint)->bool:
        if not isinstance(c, ExprInContextScope):
            return False
        expr = c.expr
        # 
        assert isinstance(expr, Expr)
        if not isinstance(expr, OneValExpr):
            return False
        if not expr.is_ph:
            return False
        return True
   
    @staticmethod
    def has_finite_candis(c:ValConstraint)->bool:
        if ScopeValConstraintSolver.is_can_solve_constraint(c):
            return True
        return False

    @staticmethod
    def get_all_candis(c: ValConstraint, context: Context) -> set:
        assert isinstance(c, ExprInContextScope)
        scope = c.scope
        concrete_value_set = scope.get_concrete_valset_from_context(context)
        return concrete_value_set

    @staticmethod
    def get_a_random_candi(c: ExprInContextScope, context: Context) ->  Union[int, float, str]:
        concrete_value_set = ScopeValConstraintSolver.get_all_candis(c, context)
        if len(concrete_value_set) == 0:
            raise UNSolveException
        return choice(list(concrete_value_set))
    
    @staticmethod
    def solve_constraint(c:ValConstraint, context: Context)->dict[str, Union[int, float, str]]:
        assert isinstance(c, ExprInContextScope)
        expr = c.expr
        assert isinstance(expr, OneValExpr)
        val = expr.val
        assert isinstance(val, (ImmPH, OperandPH))
        name = val.get_symbol_name()
        concrete_result_val = ScopeValConstraintSolver.get_a_random_candi(c, context)
        return {name: concrete_result_val}


def solve_one_constraint_vaive(c:ValConstraint, context:Context)->dict[str,Union[int, float, str]]:
    if LCExprConstraintNaiveSolver.is_can_solve_constraint(c):
        return LCExprConstraintNaiveSolver.solve_constraint(c, context)
    if EqExprConstraintNaiveSolver.is_can_solve_constraint(c):
        return EqExprConstraintNaiveSolver.solve_constraint(c, context)
    if ScopeValConstraintSolver.is_can_solve_constraint(c):
        return ScopeValConstraintSolver.solve_constraint(c, context)
    raise NotImplementedError(f'Unimplemented for {c.__class__}: {c}')


def one_c_can_solve_by_naive_solver(c:ValConstraint)->bool:
    if EqExprConstraintNaiveSolver.is_can_solve_constraint(c):
        return True
    if LCExprConstraintNaiveSolver.is_can_solve_constraint(c):
        # assert 0
        return True
    if ScopeValConstraintSolver.is_can_solve_constraint(c):
        return True
    assert not isinstance(c, CombinedAndConstraint)  # Since a CombinedAndConstraint should exists heere, it should be splitted into multiple constraints before calling this function
    return False


def one_c_has_finite_candis(c:ValConstraint)->bool:
    if EqExprConstraintNaiveSolver.has_finite_candis(c):
        return True
    if LCExprConstraintNaiveSolver.has_finite_candis(c):
        return True
    if ScopeValConstraintSolver.has_finite_candis(c):
        return True
    assert not isinstance(c, CombinedAndConstraint)  # Since a CombinedAndConstraint should exists heere, it should be splitted into multiple constraints before calling this function
    if isinstance(c, CombinedOrConstraint):
        for sub_c in c.constraints:
            if not one_c_has_finite_candis(sub_c):
                return False
        return True
    return False

def all_cs_are_finite(cs:List[ValConstraint])->bool:
    for c in cs:
        if not one_c_has_finite_candis(c):
            return False
    return True


def one_gt_other_finite_candis(cs:List[ValConstraint]):
    cs_not_finite = []
    for c in cs:
        if not one_c_has_finite_candis(c):
            cs_not_finite.append(c)
    if len(cs_not_finite) == 0:
        return False
    may_gt_c = cs_not_finite[0]
    finite_c_num = len(cs) - len(cs_not_finite)
    if finite_c_num == 0:
        return False
    if _is_can_handle_gt(may_gt_c):
        return True
    return False
    

def _is_can_handle_gt(c:ValConstraint)->bool:
    if not isinstance(c, ExprConstraint):
        return False
    if c.relation in {InstValRelation.GE, InstValRelation.GT}:
        return True
    expr1 = c.expr1
    expr2 = c.expr2
    if not isinstance(expr1, OneValExpr):
        return False
    if not isinstance(expr1.val, (ImmPH, OperandPH)):
        return False
    return False


def get_candis_from_one_c(c:ValConstraint, context:Context)->set:
    if EqExprConstraintNaiveSolver.is_can_solve_constraint(c):
        return EqExprConstraintNaiveSolver.get_all_candis(c, context)
    elif LCExprConstraintNaiveSolver.is_can_solve_constraint(c):
        return LCExprConstraintNaiveSolver.get_all_candis(c, context)
    elif ScopeValConstraintSolver.is_can_solve_constraint(c):
        return ScopeValConstraintSolver.get_all_candis(c, context)
    elif isinstance(c, CombinedOrConstraint):
        result = set()
        for sub_c in c.constraints:
            result = result.union(get_candis_from_one_c(sub_c, context))
        return result
    raise NotImplementedError(f'Unimplemented for {c}')

def get_candi_of_multi_cs_all_finite(cs:List[ValConstraint], context:Context):
    # assert len(cs) > 1
    base_result = _get_all_candis_of_multi_csA_all_finite(cs, context)
    return choice(list(base_result))

def _get_concrete_gt_bar(c:ExprConstraint, context:Context):
    assert isinstance(c, ExprConstraint)
    expr1 = c.expr1
    expr2 = c.expr2
    assert isinstance(expr1, OneValExpr)
    assert isinstance(expr2, OneValExpr)
    assert isinstance(expr1.val, (ImmPH, OperandPH))
    min_val, cs = _get_val_symbol_for_one_val_expr(expr2, context=context)
    if c.relation == InstValRelation.GT:
        return min_val + 1
    elif c.relation == InstValRelation.GE:
        return min_val
    raise NotImplementedError(f'Unimplemented for {c.relation}')
    

def solve_one_gt_other_finite_candis(cs:List[ValConstraint], context:Context):
    # if len(cs) == 0:
    #     raise ValueError('There is no constraints.')
    may_g_cs = []
    other_cs = []
    for c in cs:
        if _is_can_handle_gt(c):
            may_g_cs.append(c)
            continue
                
        other_cs.append(c)
    all_candis = list(_get_all_candis_of_multi_csA_all_finite(other_cs, context))
    concrete_gt_bars = [_get_concrete_gt_bar(c, context) for c in may_g_cs]
    if len(concrete_gt_bars) == 0:
        possible_candis = all_candis
    else:
        max_bar = max(concrete_gt_bars)
        possible_candis = [c for c in all_candis if c >= max_bar]
    if len(possible_candis) == 0:
        raise UNSolveException(f'all_candis: {all_candis}')
    return choice(possible_candis)
    


def _get_all_candis_of_multi_csA_all_finite(cs, context):
    base_result = get_candis_from_one_c(cs[0], context)
    if len(base_result) == 0:
        raise UNSolveException
    for c in cs[1:]:
        base_result = base_result.intersection(get_candis_from_one_c(c, context))
        if len(base_result) == 0:
            raise UNSolveException
    return base_result
