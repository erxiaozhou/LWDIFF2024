from itertools import chain
import struct
from typing import List, NoReturn, Optional, Tuple, Union
from z3 import Solver, sat

from .specialContextConstVal import specialContextConstVal

from .NaiveSolvePreInfo import NaiveSolvePreInfo, NaiveSolveStrategy

from .PlaceHolder import ImmPH, OperandPH
from SInst.RuleInst.util import get_unique_cs_and_process_and, ph2constraint_idxs

from .EmptyValConstraint import EmptyValConstraint

from .CombinedConstraint import CombinedAndConstraint
from .Expr import OneValExpr
from .SpecialOperand import F32SpecialVal, F64SpecialVal, I32SpecialVal, I64SpecialVal, OffsetImmVal, TypeImmSpecialVal, V128SpecialVal
from .naive_solver import all_cs_are_finite,  one_c_can_solve_by_naive_solver,  one_gt_other_finite_candis, solve_one_constraint_vaive, solve_one_gt_other_finite_candis
from .ExprConstraint import ExprConstraint
from z3 import ModelRef
from z3 import FPNumRef
from z3 import is_bv, is_real, fpToIEEEBV
from SInst.RuleInst.RuleV2 import RuleV2
from SInst.RuleInst.RuleV2 import CSSatisfiable

from extract_block_mutator.Context import Context
from .InstValRelation import InstValRelation
from .ValConstraint import ValConstraint
from .PHEnv import PHEnv
from .OpImmValSoluiton import OpImmValSoluiton
from .Exceptions import UNSolveException


class ValConstraintSolver:
    @staticmethod
    def solve_main(rule:RuleV2, context:Context)->OpImmValSoluiton:
        if rule.can_use_naive_solver:
            result = ValConstraintSolver.naive_solve(rule, context)
            return result
        else:
            ph_env: PHEnv = rule.ph_env
            val_constraints:List[ValConstraint] = rule.val_constraints
            imm_idx2constraint_idx = rule.imm_idx2constraint_idx
            op_idx2constraint_idx = rule.op_idx2constraint_idx
            constrained_symbol_names = ValConstraintSolver.get_constrained_symbol_names(imm_idx2constraint_idx, op_idx2constraint_idx)
            name2concrete_vals = ValConstraintSolver._solve_core(val_constraints, context, ph_env)
            if name2concrete_vals is None:
                ValConstraintSolver.raise_exception_for_unsolved(rule)
            else:
                return OpImmValSoluiton(name2concrete_vals, constrained_symbol_names)

    @staticmethod
    def raise_exception_for_unsolved(rule) -> NoReturn:
        if rule.satisfiable == CSSatisfiable.SATISFIABLE:
            raise ValueError(f'Constraints are unsatisfiable: {rule}')
        else:
            raise UNSolveException(f'Constraints are unsatisfiable: {rule}')

    @staticmethod
    def get_constrained_symbol_names(imm_idx2constraint_idx, op_idx2constraint_idx):
        constrained_imm_idxs = [idx for idx, c_idxs in enumerate(imm_idx2constraint_idx) if len(c_idxs)]
        constrained_op_idxs = [idx for idx, c_idxs in enumerate(op_idx2constraint_idx) if len(c_idxs)]
        # 
        constrained_symbol_names = []
        for idx in constrained_imm_idxs:
            constrained_symbol_names.append(f'imm_{idx}')
        for idx in constrained_op_idxs:
            constrained_symbol_names.append(f'op_{idx}')
        return constrained_symbol_names

    @staticmethod
    def _solve_core(constraints, context:Optional[Context], ph_env:PHEnv)->Optional[dict]:
        # symbols = None
        """
        。

        :param symbols: ，， Z3 
        :param constraints: Z3 
        :return: ，，；， None
        """
        solver = Solver()
        z3_cs = []
        for c in constraints:
            z3_cs.append(c.get_symbol_constraint(context=context, ph_env=ph_env))
        solver.add(z3_cs)
        
        if solver.check() == sat:
            model = solver.model()
            result =  _get_name2concrete_val(model)
            # print('===============================================')
            # for _ in z3_cs:
            #     print(_)
            #     print()
            # print('===============================================')
            # for _ in constraints:
            #     print(_)
            #     print()
            # print(result)
            # print('===============================================')
            return result
            # result = {}
            # for name, symbol in symbols.items():
            #     result[name] = model[symbol]
            # return result
        else:
            # print(f'Unsolved Constraints are unsatisfiable: {constraints}')
            # constraints_repr = [str(c)+'\n' for c in constraints]
            # print('------------------------------------------------')
            # for _ in z3_cs:
            #     print(_)
            #     print()
            # print('------------------------------------------------')
            # for _ in constraints:
            #     print(_)
            #     print()
            # print('------------------------------------------------')
            # raise ValueError(f'Constraints are unsatisfiable: {constraints}')
            return None

    @staticmethod
    def get_ph2cs(constraints:List[ValConstraint])->Optional[dict[Union[ImmPH, OperandPH], list[ValConstraint]]]:
        ph2constraints = ph2constraint_idxs(constraints)
        result:dict[Union[ImmPH, OperandPH], list[ValConstraint]] = {}
        considered_idxs = set()
        for ph, c_idxs in ph2constraints.items():
            for c_idx in c_idxs:
                if c_idx in considered_idxs:
                    return None
                considered_idxs.add(c_idx)
            result[ph] = [constraints[idx] for idx in c_idxs]
        return result

    @staticmethod
    def _is_one_to_one_pattern(rule:RuleV2):
        val_constraints:List[ValConstraint] = rule.val_constraints
        for c in val_constraints:
            if c.related_multi_val:
                return False
        imm_idx2constraint_idx = rule.imm_idx2constraint_idx
        op_idx2constraint_idx = rule.op_idx2constraint_idx
        assert imm_idx2constraint_idx is not None
        assert op_idx2constraint_idx is not None
        # 
        for constraint_idxs in chain(imm_idx2constraint_idx, op_idx2constraint_idx):
            if len(constraint_idxs) > 1:
                # print(f'PP22 constraint_idxs : {constraint_idxs}')
                return False
        return True

    @staticmethod
    def get_naive_solve_pre_info(rule:RuleV2):
        naive_solve_strategy = None
        if ValConstraintSolver._is_one_to_one_can_naive_solve_pattern(rule):
            naive_solve_strategy = NaiveSolveStrategy.One2One
        elif ValConstraintSolver._is_one_to_one_oe_multi_can_naive_solve_pattern(rule):
            naive_solve_strategy = NaiveSolveStrategy.One2Multi
        if naive_solve_strategy is None:
            return NaiveSolvePreInfo.empty_one()
        ph2cs = ValConstraintSolver.get_ph2cs(rule.val_constraints)
        result = NaiveSolvePreInfo(naive_solve_strategy, ph2cs)
        return result
        

    @staticmethod
    def _is_one_to_one_can_naive_solve_pattern(rule:RuleV2):
        if ValConstraintSolver._is_one_to_one_pattern(rule):
            # return False
            # print('IS ONE TO ONE')
            assert rule.val_constraints is not None
            val_cs = rule.val_constraints
            if all(one_c_can_solve_by_naive_solver(c) for c in val_cs):
                return True
        return False

    @staticmethod
    def _is_one_to_one_oe_multi_can_naive_solve_pattern(rule:RuleV2):
        ph2cs = ValConstraintSolver.get_ph2cs(rule.val_constraints)
        if ph2cs is None:
            return False
        
        for cs_group in ph2cs.values():
            all_c_finite = all_cs_are_finite(cs_group)
            one_gt_other_finite_candis_ = one_gt_other_finite_candis(cs_group)
            if not (all_c_finite or one_gt_other_finite_candis_):
                return False
        return True

    @staticmethod
    def naive_solve(rule:RuleV2, context:Context)->OpImmValSoluiton:
        # assert 0
        use_naive_solver_info = rule.use_naive_solver_info
        constrained_symbol_names = set()
        result_dict = {}
        if use_naive_solver_info.naive_solve_strategy == NaiveSolveStrategy.One2One:
            ori_cs = rule.val_constraints
            assert ori_cs is not None
            for c in ori_cs:
                cur_ph_result = solve_one_constraint_vaive(c, context)
                key = list(cur_ph_result.keys())[0]
                # assert key not in result_dict
                assert key not in constrained_symbol_names
                constrained_symbol_names.add(key)
                result_dict.update(cur_ph_result)
            result = OpImmValSoluiton(result_dict, list(constrained_symbol_names))
        elif use_naive_solver_info.naive_solve_strategy == NaiveSolveStrategy.One2Multi:
            # print('LAST SOLVE NaiveSolveStrategy.One2Multi')
            # print('<------------------------------>')
            # for c in rule.val_constraints:
            #     print(c)
            # print('==================================')
            # print(f'XXXXXXXXXXXXXXXXXX ValConstraintSolver.get_ph2cs(rule.val_constraints): {ValConstraintSolver.get_ph2cs(rule.val_constraints)}\n\n {rule.val_constraints}')
            
            ph2constraints = use_naive_solver_info.ph2constraints
            # print(f'ph2constraints: {ph2constraints} ;;{ len(ph2constraints)}')
            for ph, cs in ph2constraints.items():
                ph_name = ph.get_symbol_name()
                constrained_symbol_names.add(ph_name)
                if len(cs) == 0:
                    raise ValueError(f'There is no constraint for the placeholder ph2constraints: \n{ph2constraints}')
                result_dict[ph_name] = solve_one_gt_other_finite_candis(cs, context)
            #     print(f'FFFFFFFFFFFFF {ph_name} ::: {result_dict[ph_name]}')
            # print('||| constrained_symbol_names', constrained_symbol_names)
            result = OpImmValSoluiton(result_dict, list(constrained_symbol_names))
        else:
            raise ValueError('Unexpected naive_solve_strategy')
        return result

    @staticmethod
    def init_can_use_solution_cache(rule:RuleV2)->bool:
        val_constraints = rule.val_constraints
        if ValConstraintSolver._all_eq_const(val_constraints):
            if rule.satisfiable in {CSSatisfiable.SATISFIABLE, CSSatisfiable.UNINITIALIZED}:

                return True
        return False
            
    @staticmethod
    def _all_eq_const(val_constraints:List[ValConstraint])->bool:
        val_constraints = get_unique_cs_and_process_and(val_constraints)
        if len(val_constraints) == 0:
            return True
        is_expected = True
        constrained_imm_phs = set()
        constrained_ph_phs = set()
        for c in val_constraints:
            if isinstance(c, EmptyValConstraint):
                continue
            if isinstance(c, ExprConstraint):
                if c.relation == InstValRelation.EQ:
                    cur_related_imms = c.related_imms
                    cur_related_ops = c.related_ops
                    if c.related_multi_val:
                        # assert 0, print(c)
                        is_expected = False
                        break
                    if constrained_imm_phs.intersection(cur_related_imms) or constrained_ph_phs.intersection(cur_related_ops):
                        # assert 0, print(c)
                        is_expected = False
                        break
                    constrained_imm_phs.update(cur_related_imms)
                    constrained_ph_phs.update(cur_related_ops)
                    # 
                    second_expr = c.expr2
                    # raise second
                    if isinstance(second_expr, OneValExpr):
                        second_val = second_expr.val
                        if second_val in {
                            I32SpecialVal.Rdm,
                            I64SpecialVal.Rdm,
                            F32SpecialVal.Rdm,
                            F64SpecialVal.Rdm,
                            V128SpecialVal.Rdm,
                            TypeImmSpecialVal.Rdm,
                            OffsetImmVal.Valid
                        }:
                            is_expected = False
                            # assert 0
                            break
                        elif isinstance(second_val, specialContextConstVal):
                            is_expected = False
                            # assert 0
                            break
                            
                    continue
            
            elif isinstance(c, CombinedAndConstraint):
                raise Exception('CombinedAndConstraint should be processed before')
            else:
                is_expected = False
                # assert 0, print(c)
                break
        return is_expected

    @staticmethod
    def is_satisfiable(rule:RuleV2, 
                       context:Optional[Context]=None,
                       ph_env:Optional[PHEnv]=None)->bool:
        # print('rule.val_constraints', rule.val_constraints)
        # assert 0, print(context is None)
        cs = []
        for c in rule.val_constraints:
            z3_c = c.get_symbol_constraint(context=context, ph_env=ph_env)
            cs.append(z3_c)
        solver =  Solver()
        solver.add(cs)
        return solver.check() == sat


def _get_name2concrete_val(model:ModelRef):
    symbol2concrete_val = {}
    for d in model.decls():
        value = model[d]
        if is_bv(value):
            cvalue = value.as_long()
        elif is_real(value):
            cvalue = float(value.as_decimal())
        # elif value.sort().kind() == BitVec:
        #     cvalue = value.as_long()
        elif isinstance(value, FPNumRef):
# 
            value_bv = fpToIEEEBV(value)
            value_bin = model.eval(value_bv).as_binary_string()
            # print('value_bin', value_bin, type(value_bin), value.as_string())
            # assert 0, print(value.sort().ebits(), value.sort().ebits()==8)
            # 
            value_int = int(value_bin, 2)
            if value.sort().ebits()==8:
                value_bytes = value_int.to_bytes(4, byteorder='big')
                cvalue = struct.unpack('>f', value_bytes)[0]
            else:
                value_bytes = value_int.to_bytes(8, byteorder='big')
                cvalue = struct.unpack('>d', value_bytes)[0]

        else:
            
            # value.as_decimal()
            raise ValueError(f'Unexpected sort: {value.sort()}')
        symbol2concrete_val[d.name()] = cvalue
    return symbol2concrete_val


def all_op_imm_constrained(rule:RuleV2)->bool:
    imm_idx2constraint_idx = rule.imm_idx2constraint_idx
    op_idx2constraint_idx = rule.op_idx2constraint_idx
    all_constrained =  all(len(x) for x in imm_idx2constraint_idx) and all(len(x) for x in op_idx2constraint_idx)
    return all_constrained
