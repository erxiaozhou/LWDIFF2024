from itertools import product
from typing import Callable, List, Optional, Tuple

from util.util import FailedParsingException
from ..InstModel.IMConstraints.EmptyIMConstraint import EmptyIMConstraint
from ..InstModel.SpecialOperand import base_type2SpecialVal
from ..InstModel.set_unconstrained_imm_util import set_cs_for_unc_imm
from ..InstModel.IMConstraints.ConstraintFactory import IMConstraintFactory, is_valid_value_constraint
from ..InstModel.IMConstraints import IMConstraint
from ..InstModel.IMConstraints.AssignedIMConstraint import AssignedIMConstraint
from ..InstModel.ValConstraint import ValConstraint
from .extract_data_from_GPT_response import GptResponseData
from ..InstModel.TypeConstraint import OpTypeSolution, TypeConstraint, TypeEqConstConstraint, TypeScopeConstraint, combine_type_solution, naiveOpTypeSolution
from ..InstModel.ImSolveInfo import ImSolveInfo
from ..InstModel.InstValRelationHelper import InstValRelationHelper
from ..InstModel.OnePhConstraint import generate_OpEqConst
from ..InstModel.CPlaceHolder import ImmPH, ImmPHFactory, OperandPH, OperandPHFactory
from ..InstModel.PHEnv import PHEnv
from ..InstModel.solver import ValConstraintSolver
from .RuleV2 import CSSatisfiable, RuleV2
from WasmInfoCfg import val_type_strs
from .ValidationData import ValidationData
from .ValidRulesG import ValidInstGenerator
from .process_rule_util import one_rule_is_unsatisfiable


class ExtractedInfo:
    def __init__(self,
                 inst_info: GptResponseData,
                 raw_inst_name: Optional[str] = None,
                 op: Optional[str] = None,
                 valid_context_func: Optional[Callable] = None,
                 valid_inst_generator: Optional[ValidInstGenerator] = None,
                 rules: Optional[List[RuleV2]] = None,
                 ) -> None:
        self.inst_info = inst_info
        inferred_raw_inst_name = inst_info.raw_inst_name
        inferred_op = inst_info.op
        if raw_inst_name is None:
            raw_inst_name = inferred_raw_inst_name
        else:
            assert raw_inst_name == inferred_raw_inst_name
        if op is None:
            op = inferred_op
        else:
            assert op == inferred_op
        self.raw_inst_name = raw_inst_name
        self.op = op

        self._valid_context_func = valid_context_func
        self._valid_inst_generator = valid_inst_generator
        self._rules = rules

    @property
    def valid_context_func(self):
        assert self._valid_context_func is not None
        return self._valid_context_func

    @property
    def valid_inst_generator(self):
        assert self._valid_inst_generator is not None
        return self._valid_inst_generator

    @property
    def rules(self):
        assert self._rules is not None
        return self._rules

    def is_no_fully_initialized(self):
        not_initialized = False
        consided_attrs = [
            self._valid_context_func,
            self._valid_inst_generator,
            self._rules
        ]
        not_initialized = any([_ is None for _ in consided_attrs])
        if not_initialized:
            if not self.base_info_all_un_initialized():
                raise ValueError(
                    'Some of the base info is initialized. It is unexpected. There may be a logic bug.')
        return not_initialized

    def base_info_all_un_initialized(self):
        if self._valid_context_func is None:
            if self._valid_inst_generator is None:
                if self._rules is None:
                    return True
        return False

    def init_infos_by_gpt_info(self, exception_on_invalid: bool = False):
        assert self.is_no_fully_initialized()
        inst_info = self.inst_info
        valid_ty_cs, valid_im_cs = _get_valid_validation_info(inst_info)
        imm_ph_dict = _get_imm_ph_dict(inst_info.inner_type_part)
        valid_ph_envs = _determine_valid_ph_env(
            valid_ty_cs,
            imm_ph_dict,
            inst_info.op
        )
        validation_data = ValidationData(
            valid_ty_cs, valid_im_cs, valid_ph_envs)
        to_solve_validation_combinations = _determine_validation_constraints(
            valid_ty_cs, valid_im_cs, valid_ph_envs, imm_ph_dict, inst_info.op
        )
        exec_cs_list = _determine_spec_exec_comstraints(
            inst_info.execution_part, exception_on_invalid=exception_on_invalid)
        to_solve_final_infos: list[ImSolveInfo] = _get_to_solve_final_infos(
            to_solve_validation_combinations,
            exec_cs_list
        )
        rules = [RuleV2(raw_op_name=inst_info.raw_inst_name, op=inst_info.op,
                        raw_solve_info=info) for info in to_solve_final_infos]
        context_can_apply_func = validation_data.context_can_apply_func
        valid_inst_generator = ValidInstGenerator.from_op_name_and_validation_data(
            inst_info.raw_inst_name,
            inst_info.op,
            validation_data
        )
        self._valid_context_func = context_can_apply_func
        self._valid_inst_generator = valid_inst_generator
        self._rules = rules

    def polish_rules(self) -> None:
        if self._rules is None:
            raise ValueError('rules should not be None')
        polished_rules = _remove_unsatisfiable_constraints(self._rules)
        for rule in polished_rules:
            set_cs_for_unc_imm(rule)
            rule.use_naive_solver_info = ValConstraintSolver.get_naive_solve_pre_info(
                rule)
            if rule.val_constraints is not None:
                rule.can_use_solution_cache = ValConstraintSolver.init_can_use_solution_cache(
                    rule)
            if rule.context_condition_func is None:
                raise ValueError(
                    f'context_condition_func is None: op:{self.op}, rule:{rule}')
        self._rules = polished_rules


def _get_to_solve_final_infos(
    to_solve_validation_combinations,
    exec_cs_list
) -> list[ImSolveInfo]:
    to_solve_final_infos: List[ImSolveInfo] = []
    for solve_info in to_solve_validation_combinations:
        if solve_info.is_valid:
            all_constraints_groups = []
            all_constraints_groups.extend(exec_cs_list)
            
            if len(solve_info.ph_env.get_operand_types()):
                common_cs = get_common_constraints_by_type_core_by_ph_env(solve_info.ph_env)
                common_cs_groups = [[c] for c in common_cs]
                all_constraints_groups.extend(common_cs_groups)
            for constraints in all_constraints_groups:
                new_solve_info = create_solve_info(solve_info, constraints)
                to_solve_final_infos.append(new_solve_info)
        else:
            to_solve_final_infos.append(solve_info)
    return to_solve_final_infos


def create_solve_info(solve_info, additional_constraints):
    im_cs = solve_info.im_constraints + additional_constraints
    cur_all_cs = solve_info.all_constraints + additional_constraints
    new_solve_info = ImSolveInfo(
        solve_info.ph_env, 
        im_cs, 
        cur_all_cs, 
        True
        )
    return new_solve_info

def get_common_constraints_by_type_core_by_ph_env(ph_env: PHEnv) -> List[AssignedIMConstraint]:
    operand_types = ph_env.get_operand_types()
    val_cs_list = get_common_constraints_by_type_core(operand_types)
    assigned_im_cs = []
    for val_cs in val_cs_list:
        assigned_im_cs.append(
            AssignedIMConstraint.from_val_constraints(val_cs))
    return assigned_im_cs


def get_common_constraints_by_type_core(operand_types: List[str]) -> List[List[ValConstraint]]:
    operand_phs = [OperandPHFactory.get_operand_ph(
        ty, i) for i, ty in enumerate(operand_types)]
    special_vals = [base_type2SpecialVal[ty] for ty in operand_types]

    all_one_op_constraints = []
    for ph, vals in zip(operand_phs, special_vals):
        one_op_constraints = [(ph, val) for val in vals]
        all_one_op_constraints.append(one_op_constraints)

    all_op_val_combinations = [list(_) for _ in list(
        product(*all_one_op_constraints))]
    processed_operand_constraints = []
    for one_op_val_combination in all_op_val_combinations:
        cur_cs = []
        for _ph, _val in one_op_val_combination:
            if not _val.can_skip():
                c = generate_OpEqConst(_ph, _val)
                cur_cs.append(c)
        processed_operand_constraints.append(cur_cs)

    return processed_operand_constraints


def _get_valid_validation_info(inst_info: GptResponseData):
    all_cs_ds = inst_info.all_validate_constraints
    valid_ty_cs, valid_im_cs = IMConstraintFactory.determine_valid_constraint_group(
        all_cs_ds)
    validation_cs_from_type_part_dict = get_ty_validation_cs_from_type_part_dict(
        inst_info.inner_type_part)
    combine_ty_eq_const_constraints(
        valid_ty_cs, validation_cs_from_type_part_dict)
    valid_im_cs = valid_im_cs
    return valid_ty_cs, valid_im_cs


def _determine_validation_constraints(
    valid_ty_cs,
    valid_im_cs,
    valid_ph_envs,
    imm_ph_dict,
    op
) -> list[ImSolveInfo]:

    all_valid_cs = list(valid_ty_cs) + list(valid_im_cs)
    valid_ones = []
    for ph_env in valid_ph_envs:
        valid_ones.append(ImSolveInfo(ph_env, valid_im_cs, all_valid_cs, True))
    invalid_ones = _get_invalid_validition_info(
        imm_ph_dict,
        all_valid_cs,
        len(valid_ty_cs),
        valid_ph_envs,
        op
    )
    all_v_im_solve_infos = valid_ones + invalid_ones
    return all_v_im_solve_infos


def _get_invalid_validition_info(imm_ph_dict, all_valid_cs, ty_cs_num, valid_ph_envs, op) -> list[ImSolveInfo]:
    total_num = len(all_valid_cs)
    ty_invalid_ones = []
    other_invalid_ones = []
    for to_neg_idx in range(total_num):
        cur_to_solve_cs = all_valid_cs.copy()
        if not all_valid_cs[to_neg_idx].can_neg():
            continue
        neg_c = all_valid_cs[to_neg_idx].as_neg_constraint()
        cur_to_solve_cs[to_neg_idx] = neg_c
        cur_ty_cs = cur_to_solve_cs[:ty_cs_num]
        cur_im_cs = cur_to_solve_cs[ty_cs_num:]
        if to_neg_idx < ty_cs_num:
            invalid_ph_envs = [PHEnv(imm_ph_dict, op, cur_ty_cs)]
            for ph_env in invalid_ph_envs:
                ty_invalid_ones.append(ImSolveInfo(
                    ph_env, cur_im_cs, cur_to_solve_cs, False))
        else:
            for ph_env in valid_ph_envs:
                other_invalid_ones.append(ImSolveInfo(
                    ph_env, cur_im_cs, cur_to_solve_cs, False))
    return ty_invalid_ones + other_invalid_ones


def _determine_valid_ph_env(
    type_constraints: List[TypeConstraint],
    imm_ph_dict: dict[str, ImmPH], op: str
) -> List[PHEnv]:
    type_solutions: List[List[OpTypeSolution]] = []
    for c in type_constraints:
        type_solutions.append(c.get_valid_candis())
    final_solutions = _summary_type_slution(type_solutions)
    envs = []
    for fs in final_solutions:
        _op_ph_dicts = _get_op_ph_dicts_from_ty_solution(fs)
        for op_ph_dict in _op_ph_dicts:
            ph_dict = {**op_ph_dict, **imm_ph_dict}
            env = PHEnv(ph_dict, op=op)
            envs.append(env)
    return envs


def _summary_type_slution(type_solutions: List[List[OpTypeSolution]]) -> List[OpTypeSolution]:
    all_combes = product(*type_solutions)
    final_solutions = []
    for comb in all_combes:
        final_solution = combine_type_solution(comb)
        final_solutions.append(final_solution)
    return final_solutions


def _get_op_ph_dicts_from_ty_solution(ty_solution: OpTypeSolution) -> List[dict[str, OperandPH]]:
    if isinstance(ty_solution, naiveOpTypeSolution):
        op_num = len(ty_solution.op_idx2tycandis)
        tys = [ty_solution.op_idx2tycandis[i] for i in range(op_num)]
        ty_combs = product(*tys)
        ds = []
        for ty_comb in ty_combs:
            d = {}
            for i, ty in enumerate(ty_comb):
                d[f'op_{i}'] = OperandPHFactory.get_operand_ph(ty, i)
            ds.append(d)
        return ds
    raise NotImplementedError


def get_ty_validation_cs_from_type_part_dict(inner_type_part: dict[str, str]):
    ty_cs = []
    for ph_name, ph_type in inner_type_part.items():
        if not ph_name.startswith('op'):
            continue
        if ph_name.endswith('.type'):
            ph_name = ph_name[:-5]
        op_pos = int(ph_name.split('_')[-1])
        if isinstance(ph_type, str):
            if ph_type in val_type_strs:
                ty_cs.append(TypeEqConstConstraint(op_pos, ph_type, True))
                continue
            if ph_type == 'any':
                op_pos = int(ph_name.split('_')[-1])
                c = TypeScopeConstraint(op_pos, val_type_strs.copy())
                ty_cs.append(c)
                continue
            if ph_type == 'funcref or externref':  
                op_pos = int(ph_name.split('_')[-1])
                c = TypeScopeConstraint(op_pos, {'funcref', 'externref'})
                ty_cs.append(c)
                continue
        elif isinstance(ph_type, list):
            if all([_ in val_type_strs for _ in ph_type]):
                op_pos = int(ph_name.split('_')[-1])
                c = TypeScopeConstraint(op_pos, set(ph_type))
                ty_cs.append(c)
                continue
        raise FailedParsingException(f'Invalid type representation: {ph_type}')

    return ty_cs


def _get_imm_ph_dict(inner_type_part: dict):
    imm_ph_dict = {}
    for ph_name, ph_type in inner_type_part.items():
        if ph_name.startswith('imm'):
            idx_repr = ph_name[4:]
            if not idx_repr.isdigit():
                raise FailedParsingException(
                    f"The representation for immediate arguments {ph_name} is ill-formatted")
            idx = int(ph_name.split('_')[-1])
            try:
                imm_ph = ImmPHFactory.get_ph_by_attr(idx, ph_type)
            except Exception:
                raise FailedParsingException(
                    f"The representation for immediate arguments {ph_name}'s type {ph_type} is ill-formatted")
            imm_ph_dict[ph_name] = imm_ph
    return imm_ph_dict


def _determine_spec_exec_comstraints(raw_exec_dicts: List[dict], exception_on_invalid) -> List[List[IMConstraint]]:
    ori_im_single_cs = []
    ori_ds = []
    for raw_d in raw_exec_dicts:
        input_cs_dicts = raw_d['InputConstraint']
        context_cs_dicts = raw_d['ContextConstraint']
        all_cs_dicts = input_cs_dicts + context_cs_dicts
        for cs_dict in all_cs_dicts:
            if one_input_c_ill_formatted(cs_dict, exception_on_invalid):
                continue
            ori_ds.append(cs_dict)
    ds = _remove_duplicated_exec_input_ds(ori_ds)
    for ori_d in ds:
        try:
            cur_im_c = IMConstraintFactory.determine_value_constraint(ori_d)
        except FailedParsingException as e:
            if exception_on_invalid:
                raise e
            else:
                continue
        if isinstance(cur_im_c, EmptyIMConstraint):
            continue
        ori_im_single_cs.append(cur_im_c)

    im_c_combs = _determine_exec_cs_core(ori_im_single_cs)
    final_cs_combs = []
    for cs in im_c_combs:
        final_cs_combs.append(cs)
    return final_cs_combs


def _determine_exec_cs_core(ori_cs: List[IMConstraint]) -> List[List[IMConstraint]]:
    rs = []
    each_comb_and_neg: List[List[IMConstraint]] = []
    for c in ori_cs:
        cur_cs = _get_covered_cs_for_a_imc(c)
        each_comb_and_neg.append(cur_cs)
    exec_im_c_combinarions = list(product(*each_comb_and_neg))
    for combination in exec_im_c_combinarions:
        rs.append(list(combination))
    return rs


def _get_covered_cs_for_a_imc(c: IMConstraint):
    cs = [c]
    if c.can_neg():
        cs.append(c.as_neg_constraint())
    return cs


def _remove_duplicated_exec_input_ds(ori_ds):
    def _two_ds_same(d1, d2):
        return d1['v1'] == d2['v1'] and d1['v2'] == d2['v2'] and d1['relation'] == d2['relation']

    def _two_ds_neg(d1, d2):
        if d1['v1'] == d2['v1'] and d1['v2'] == d2['v2']:
            if InstValRelationHelper.is_valid_str(d1['relation']) and InstValRelationHelper.is_valid_str(d2['relation']):
                if InstValRelationHelper.from_str(d1['relation']).neg() == InstValRelationHelper.from_str(d2['relation']):
                    return True
        return False

    def _same(d1, d2):
        return _two_ds_same(d1, d2) or _two_ds_neg(d1, d2)
    saved_ds = []
    for d in ori_ds:
        if not any([_same(d, sd) for sd in saved_ds]):
            saved_ds.append(d)
    return saved_ds


def one_input_c_ill_formatted(cur_input_c, exception_on_invalid: bool):
    assert isinstance(cur_input_c, dict)
    invalid_tokens = {'undefined', 'invalid_vector'}  
    is_illformatted = None

    try:
        if len(cur_input_c) == 3:
            if set(cur_input_c.keys()) != {'v1', 'v2', 'relation'}:
                raise FailedParsingException(
                    f'Invalid constraint representation: {cur_input_c}. Specifically, the keys should be either {{"v1", "v2", "relation"}}. Rather than {set(cur_input_c.keys())}')
            v1 = _repr_val(cur_input_c['v1'])
            v2 = _repr_val(cur_input_c['v2'])
            relation = _repr_val(cur_input_c['relation'])
            if isinstance(v1, str) and isinstance(relation, str) and isinstance(v2, (str, list)):
                check_vals = [v1] + ([v2] if isinstance(v2, str) else v2)
                is_illformatted = bool(set(check_vals).intersection(invalid_tokens))
        else:
            is_illformatted = True
        if is_illformatted is None:
            raise FailedParsingException(
                f'Invalid constraint representation: {cur_input_c}')
    except FailedParsingException as e:
        if exception_on_invalid:
            raise e
        else:
            is_illformatted = True
    return is_illformatted


def _is_useable_c(c_dict: dict):
    if one_input_c_ill_formatted(c_dict, False):
        return False
    if not is_valid_value_constraint(c_dict):
        return False
    return True


def _repr_val(val):
    if isinstance(val, (dict, list)):
        return val
    return str(val)


def _remove_unsatisfiable_constraints(rules: List[RuleV2]) -> List[RuleV2]:
    to_solve_rules = []
    for _rule in rules:
        if _rule.illegal_type:
            continue
        _satisfiable = one_rule_is_unsatisfiable(_rule)
        if _satisfiable == CSSatisfiable.UNSATISFIABLE:
            continue
        else:
            _rule.satisfiable = _satisfiable
            to_solve_rules.append(_rule)
    return to_solve_rules


def combine_ty_eq_const_constraints(ori_ty_cs: list[TypeConstraint], ty_cs_from_type_part: list[TypeEqConstConstraint]):
    op_idx_covered_by_ori_ty_cs = set()
    for c in ori_ty_cs:
        if isinstance(c, TypeConstraint):
            op_idx_covered_by_ori_ty_cs.update(c.op_poss)
    for c in ty_cs_from_type_part:
        if c.op_pos not in op_idx_covered_by_ori_ty_cs:
            ori_ty_cs.append(c)
