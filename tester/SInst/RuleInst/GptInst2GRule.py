from itertools import product
from pathlib import Path
from typing import Callable, List, Mapping, Optional, Tuple, Union

from util.util import FailedParsingException
from ..InstModel.IMConstraints.EmptyIMConstraint import EmptyIMConstraint
from config_inst_info import gpt_data_v2_dir
from ..InstModel.SpecialOperand import base_type2SpecialVal
from ..InstModel.set_unconstrained_imm_util import set_cs_for_unc_imm
from config_inst_info import control_inst_names
from ..InstModel.IMConstraints.ConstraintFactory import ConstraintFactory
from ..InstModel.IMConstraints import IMConstraint
from ..InstModel.IMConstraints.AssignedIMConstraint import AssignedIMConstraint
from ..InstModel.ValConstraint import ValConstraint
from extract_LLM_spec.extract_data_from_GPT_response import GptResponseData
from ..InstModel.TypeConstraint import OpTypeSolution, TypeConstraint, TypeEqConstConstraint, TypeScopeConstraint, combine_type_solution, naiveOpTypeSolution
from ..InstModel.ImSolveInfo import ImSolveInfo
from ..InstModel.InstValRelation import InstValRelation
from ..InstModel.OnePhConstraint import generate_OpEqConst
from ..InstModel.PlaceHolder import ImmPH, ImmPHFactory, OperandPH, OperandPHFactory
from ..InstModel.PHEnv import PHEnv
from ..InstModel.solver import ValConstraintSolver
from file_util import save_json
from config_inst_info import all_inst_names
from ..RuleInst.RuleV2 import CSSatisfiable, RuleV2
from WasmInfoCfg import val_type_strs
from .ValidationData import ValidationData
from .ValidRulesG import ValidInstGenerator
from .process_rule_util import one_rule_is_unsatisfiable


def _get_support_ops(support_ops):
    if support_ops is None:
        support_ops = (all_inst_names | {'select_1C~t'}) - control_inst_names - {'else', 'end'}
    else:
        support_ops = set(support_ops)
    # assert 0, print('len(support_ops)', len(support_ops))
    return support_ops


class ExtractedInfo:
    def __init__(self,
                 inst_info: GptResponseData,
                 raw_inst_name: Optional[str]=None,
                 op: Optional[str]=None,
                 valid_context_func: Optional[Callable]=None,
                 valid_inst_generator: Optional[ValidInstGenerator]=None,
                 rules: Optional[List[RuleV2]]=None,
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

    def has_no_base_info(self):
        not_initialized = False
        consided_attrs = [
            self._valid_context_func,
            self._valid_inst_generator,
            self._rules
        ]
        not_initialized = any([_ is None for _ in consided_attrs])
        if not_initialized:
            if not self.base_info_all_un_initialized():
                raise ValueError('Some of the base info is initialized. It is unexpected. There may be a logic bug.')
        return not_initialized

    def base_info_all_un_initialized(self):
        if self._valid_context_func is None:
            if self._valid_inst_generator is None:
                if self._rules is None:
                    return True
        return False

    def init_infos_by_gpt_info(self):
        assert self.has_no_base_info()
        inst_info = self.inst_info
        valid_ty_cs, valid_im_cs = _get_valid_validation_info(inst_info)
        imm_ph_dict =_get_imm_ph_dict(inst_info.inner_type_part) 
        valid_ph_envs = _determine_valid_ph_env(valid_ty_cs, imm_ph_dict)
        validation_data = ValidationData(valid_ty_cs, valid_im_cs, valid_ph_envs)
        to_solve_validation_combinations = _determine_validation_constraints(
                        valid_ty_cs, valid_im_cs, valid_ph_envs, imm_ph_dict
                    )
        exec_cs_and_trap_list = _determine_spec_exec_comstraints(inst_info.execution_part)
        to_solve_final_infos: list[ImSolveInfo] = get_to_solve_final_infos(
            to_solve_validation_combinations,
            exec_cs_and_trap_list
        )
        rules = [RuleV2(raw_op_name=inst_info.raw_inst_name, op=inst_info.op, raw_solve_info=info) for info in to_solve_final_infos]
        # 
        context_can_apply_func = validation_data.context_can_apply_func
        valid_inst_generator = ValidInstGenerator.from_op_name_and_validation_data(
            inst_info.raw_inst_name, 
            inst_info.op, 
            validation_data
        )
        # 
        self._valid_context_func = context_can_apply_func
        self._valid_inst_generator = valid_inst_generator
        self._rules = rules

    def polish_rules(self)->None:
        if self._rules is None:
            raise ValueError('rules should not be None')
        polished_rules = _remove_unsatisfiable_constraints(self._rules)
        for rule in polished_rules:
            set_cs_for_unc_imm(rule)
            rule.use_naive_solver_info = ValConstraintSolver.get_naive_solve_pre_info(rule)
            if rule.val_constraints is not None:
                rule.can_use_solution_cache = ValConstraintSolver.init_can_use_solution_cache(rule)
            if rule.context_condition_func is None:
                raise ValueError(f'context_condition_func is None: op:{self.op}, rule:{rule}')
        self._rules = polished_rules


def extract_from_one_response(
    p: Path,
    initialize_base_info: bool = True,
    polish_rules: bool = False
):
    assert isinstance(p, Path)
    suffix = p.suffix
    if suffix == '.json':
        inst_info:GptResponseData = GptResponseData.from_json(p)
    elif suffix == '.txt':
        inst_info:GptResponseData = GptResponseData.from_raw_response_file(p)
    else:
        raise ValueError(f"The response file's suffix should be .json or .txt, but got {suffix}")
    # if 'select' in inst_info.ra
    extracted_info = ExtractedInfo(inst_info)
    if initialize_base_info:
        extracted_info.init_infos_by_gpt_info()
    if polish_rules:
        extracted_info.polish_rules()
    return extracted_info

def extract_and_parse(p):
    assert isinstance(p, Path)
    suffix = p.suffix
    if suffix == '.json':
        inst_info:GptResponseData = GptResponseData.from_json(p)
    elif suffix == '.txt':
        inst_info:GptResponseData = GptResponseData.from_raw_response_file(p)
    exception_information = []
    # auto check
    try:
        extracted_info = ExtractedInfo(inst_info)
        extracted_info.init_infos_by_gpt_info()
    except FailedParsingException as e:
        exception_information.append(f'{e}')
    # manual check
    # check single part
    # format part
    exception_information.extend(check_format_part(inst_info))
    exception_information.extend(check_full_part_type(inst_info))
    if len(exception_information):
        raise FailedParsingException(f'Failed to parse the response file {p}. The following exceptions are found:\n{exception_information}')
    return extracted_info


def check_format_part(inst_info:GptResponseData):
    expected_op_types = {'i32', 'i64', 'f32', 'f64', 'v128', 'funcref', 'externref', 'any'}
    expected_imm_types = {'i32', 'i64', 'f32', 'f64', 'funcref', 'externref', 'v128', 'local_idx', 'align', 'offset', 'lane_idx', 'table_idx', 'data_idx', 'elem_idx', 'func_idx', 'global_idx'}
    inner_type_part = inst_info.inner_type_part
    exception_info = []
    for k, vs in inner_type_part.items():
        
        if not isinstance(vs, list):
            vs=  [vs]
        # for
        if k.startswith('op_'):
            for v in vs:
                if v not in expected_op_types:
                    exception_info.append(f'Unexpected operand type representation: {v}. Pleaze replace {v} with one of {expected_op_types}')
            # if v not in expected_op_types:
        if k.startswith('imm_'):
            for v in vs:
                if v not in expected_imm_types:
                    exception_info.append(f'Unexpected immediate argument type representation: {v}. Pleaze replace {v} with one of {expected_imm_types}')
    return exception_info
            # expected


def check_full_part_type(inst_info:GptResponseData):
    full_type_part = inst_info.full_type_part
    exception_info = []
    assert full_type_part is not None
    for candi_type in full_type_part:
        if not isinstance(candi_type, dict):
            exception_info.append(f'The type of the instruction should be a list of mapping with keys `param` and `result`, but got {candi_type}')
            continue
        if set(candi_type.keys()) != {'param', 'result'}:
            exception_info.append(f'The keys of the type mapping should be `param` and `result`, but got {set(candi_type.keys())}')
            continue
        params = candi_type['param']
        results = candi_type['result']
        for ty in params:
            info_ = check_one_val_type_repr(ty)
            if info_ is not None:
                exception_info.extend(info_)
        for ty in results:
            info_ = check_one_val_type_repr(ty)
            if info_ is not None:
                exception_info.extend(info_)
    return exception_info


def check_one_val_type_repr(val_repr):
    if val_repr in {'i32', 'i64', 'f32', 'f64', 'v128', 'funcref', 'externref'}:
        return None
    if val_repr == 'any':
        return ['Pleace carefully consider whether `any` is the best choice and try to replace it with a more specific type']
    vals = []
    if not val_repr.endswith('.type'):
        vals.append(f'Please consider adding `.type` to the end of the val type representation: {val_repr}')
    if 'imm_' not in val_repr and 'op_' not in val_repr:
        v =  f'Please consider use the <imm_xxx> or <op_xxx> to represent a type, rather than {val_repr}'
        vals.append(v)
    return vals
  

class GptInstKM:
    _raw_inst_name2op_name: dict[str, str] = {}
    _raw_op_name2rules: dict[str, list[RuleV2]] = {}
    raw_inst_name2valid_context_func:dict[str, Callable] = {}
    raw_inst_name2ValidInstGenerator:dict[str, ValidInstGenerator] = {}
    polished = False
    _has_init_naive_solver_info = False
    _has_init_gpt_specs = False

    def __init__(self, 
                 support_ops=None, 
                 json_spec_base_dir = gpt_data_v2_dir,
                 just_valid_part:bool = False,
                 ):
        self.support_ops:set[str] = _get_support_ops(support_ops)
        # print('@#VVFDD self.support_ops', len(self.support_ops), self.support_ops)
        # 
        all_extracted_infos = {}
        for p in Path(json_spec_base_dir).iterdir():
            if not (p.name.endswith('.json') or p.name.endswith('_response.txt')):
                continue
            extracted_info: ExtractedInfo = extract_from_one_response(p, initialize_base_info=False, polish_rules=False)
            raw_inst_name = extracted_info.raw_inst_name
            if raw_inst_name in self.support_ops:
                all_extracted_infos[raw_inst_name] = extracted_info
        # for extracted_info in all_extracted_infos.values():
        #     extracted_info.init_infos_by_gpt_info()
        # if not just_valid_part:
                # print('XXXXXXXXXXX p: ', p, raw_inst_name)
                extracted_info.init_infos_by_gpt_info()
        if not just_valid_part:
            for extracted_info in all_extracted_infos.values():
                extracted_info.polish_rules()
        # 
        # print('len(all_extracted_infos)', len(all_extracted_infos))
        for raw_inst_name, extracted_info in all_extracted_infos.items():
            # if 'select' in raw_inst_name:
            #     print('Is select!', raw_inst_name)
            self._raw_inst_name2op_name[raw_inst_name] = extracted_info.op
            self._raw_op_name2rules[raw_inst_name] = extracted_info.rules
            self.raw_inst_name2valid_context_func[raw_inst_name] = extracted_info.valid_context_func
            self.raw_inst_name2ValidInstGenerator[raw_inst_name] = extracted_info.valid_inst_generator

    @staticmethod
    def get_op(raw_op_name):
        return GptInstKM._raw_inst_name2op_name[raw_op_name]

    def get_rules_by_op(self, op):
        return GptInstKM._raw_op_name2rules[op]


def _remove_unsatisfiable_constraints(rules: List[RuleV2])->List[RuleV2]:
    # ! heavy?  ValConstraintSolver.is_satisfiable 
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

def _get_imm_ph_dict(inner_type_part:dict):
    imm_ph_dict = {}
    for ph_name, ph_type in inner_type_part.items():
        if ph_name.startswith('imm'):
            idx_repr=  ph_name[4:]
            if not idx_repr.isdigit():
                raise FailedParsingException(f"The representation for immediate arguments {ph_name} is ill-formatted")
            idx = int(ph_name.split('_')[-1])
            try:
                imm_ph = ImmPHFactory.get_ph_by_attr(idx, ph_type)
            except Exception:
                raise FailedParsingException(f"The representation for immediate arguments {ph_name}'s type {ph_type} is ill-formatted")
            imm_ph_dict[ph_name] = imm_ph
    return imm_ph_dict 


def get_to_solve_final_infos(
        to_solve_validation_combinations,
        exec_cs_and_trap_list
    ) -> list[ImSolveInfo]:
    to_solve_final_infos: List[ImSolveInfo] = []
    for solve_info in to_solve_validation_combinations:
        if solve_info.is_valid:
            for exec_constraints, trap_ in exec_cs_and_trap_list:
                im_cs = solve_info.im_constraints + exec_constraints
                cur_all_cs = solve_info.all_constraints + exec_constraints
                # print('ZXZXSSC', im_cs)
                to_solve_final_infos.append(ImSolveInfo(solve_info.ph_env, im_cs, cur_all_cs, True, trap_))
            if len(solve_info.ph_env.get_operand_types()):
                common_cs = get_common_constraints_by_type_core_by_ph_env(solve_info.ph_env)
                for common_c in common_cs:
                    im_cs = solve_info.im_constraints + [common_c]
                    cur_all_cs = solve_info.all_constraints + [common_c]
                    # print('ZXZXSSC', im_cs)
                    to_solve_final_infos.append(ImSolveInfo(solve_info.ph_env, im_cs, cur_all_cs, True, trap_))
        else:
            to_solve_final_infos.append(solve_info)
    return to_solve_final_infos


def get_common_constraints_by_type_core_by_ph_env(ph_env:PHEnv)->List[AssignedIMConstraint]:
    operand_types = ph_env.get_operand_types()
    val_cs_list = get_common_constraints_by_type_core(operand_types)
    assigned_im_cs = []
    for val_cs in val_cs_list:
        assigned_im_cs.append(AssignedIMConstraint.from_val_constraints(val_cs))
    return assigned_im_cs


def get_common_constraints_by_type_core(operand_types:List[str])->List[List[ValConstraint]]:
    operand_phs = [OperandPHFactory.get_operand_ph(
        ty, i) for i, ty in enumerate(operand_types)]
    special_vals = [base_type2SpecialVal[ty] for ty in operand_types]

    all_one_op_constraints = []
    for ph, vals in zip(operand_phs, special_vals):
        one_op_constraints = [(ph, val) for val in vals]
        all_one_op_constraints.append(one_op_constraints)

    all_op_val_combinations = [list(_) for _ in list(product(*all_one_op_constraints))]
    # remove to skip
    processed_operand_constraints = []
    for one_op_val_combination in all_op_val_combinations:
        # cur_combs = []
        cur_cs = []
        for _ph, _val in one_op_val_combination:
            if not _val.can_skip():
                c = generate_OpEqConst(_ph, _val)
                cur_cs.append(c)
        processed_operand_constraints.append(cur_cs)
        
    return processed_operand_constraints



def _determine_spec_exec_comstraints(raw_exec_dicts:List[dict])->List[Tuple[List[IMConstraint], bool]]:
    # !  table.init， ‘ContextConstraint’，  ‘InputConstraint’;  ‘InputConstraint’ cs，cs，
    ori_im_single_cs = []
    ori_ds = []
    trap_ = False  # ! TODO ，
    for raw_d in raw_exec_dicts:
        input_cs_dicts = raw_d['InputConstraint']
        # context_cs_dict = raw_d['ContextConstraint']
        whether_trap  = raw_d['WhetherTrap']
        # assert len(context_cs_dict) == 0
        for input_cs_dict in input_cs_dicts:
            if one_input_c_ill_formatted(input_cs_dict):
                continue
            ori_ds.append(input_cs_dict)
    # remove duplicated
    ds = _remove_duplicated_exec_input_ds(ori_ds)
    # assert 0, print(ds)
    for ori_d in ds:
        
        # assert 0, print(cur_im_c)
        cur_im_c = ConstraintFactory.determine_exec_im_constraint(ori_d)
        if isinstance(cur_im_c, EmptyIMConstraint):
            continue
        ori_im_single_cs.append(cur_im_c)

    im_c_combs = _determine_exec_cs_core(ori_im_single_cs)
    final_cs_combs = []
    # print('FDSHGRTHRTHDSHRSHHRT len(im_c_combs)', len(im_c_combs))
    # print('im_c_combs XXXXXXXXXXXXXXXXXXXXXXXXXX\n', im_c_combs, '\n============================================')
    for cs in im_c_combs:
        final_cs_combs.append((cs, trap_))
    # print('XXXXXXXXXXX', final_cs_combs)
    return final_cs_combs


def _determine_exec_cs_core(ori_cs:List[IMConstraint])->List[List[IMConstraint]]:
    # TODO 
    rs = []
    each_comb_and_neg:List[List[IMConstraint]] = []
    for c in ori_cs:
        cur_cs = _get_covered_cs_for_a_imc(c)
        each_comb_and_neg.append(cur_cs)
    exec_im_c_combinarions = list(product(*each_comb_and_neg))
    for combination in exec_im_c_combinarions:
        rs.append(list(combination))
    return rs


def _get_covered_cs_for_a_imc(c:IMConstraint):
    cs = [c]
    if c.can_neg():
        cs.append(c.as_neg_constraint())
    return cs


def _remove_duplicated_exec_input_ds(ori_ds):
    def _two_ds_same(d1, d2):
        return d1['v1'] == d2['v1'] and d1['v2'] == d2['v2'] and d1['relation'] == d2['relation']
    def _two_ds_neg(d1, d2):
        if d1['v1'] == d2['v1'] and d1['v2'] == d2['v2']:
            if InstValRelation.is_valid_str(d1['relation']) and InstValRelation.is_valid_str(d2['relation']):
                if InstValRelation.from_str(d1['relation']).neg() == InstValRelation.from_str(d2['relation']):
                    return True
        return False
    def _same(d1, d2):
        return _two_ds_same(d1, d2) or _two_ds_neg(d1, d2)
    saved_ds = []
    for d in ori_ds:
        if not any([_same(d, sd) for sd in saved_ds]):
            saved_ds.append(d)
    return saved_ds


def get_ty_validation_cs_from_type_part_dict(inner_type_part:dict[str,str]):
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
            if ph_type == 'funcref or externref':  # TODO ，
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
        
        # raise NotImplementedError(inner_type_part)
    return ty_cs


def combine_ty_eq_const_constraints(ori_ty_cs:List[TypeConstraint], ty_cs_from_type_part:List[TypeEqConstConstraint]):
    op_idx_covered_by_ori_ty_cs = set()
    for c in ori_ty_cs:
        if isinstance(c, TypeConstraint):
            op_idx_covered_by_ori_ty_cs.update(c.op_poss)
    # print('JUYRJYURJRYUJRJ', 'op_idx_covered_by_ori_ty_cs', op_idx_covered_by_ori_ty_cs)
    for c in ty_cs_from_type_part:
        if c.op_pos not in op_idx_covered_by_ori_ty_cs:
            ori_ty_cs.append(c)


def _determine_validation_constraints(valid_ty_cs, valid_im_cs, valid_ph_envs, imm_ph_dict)->list[ImSolveInfo]:
    
    all_valid_cs = list(valid_ty_cs) + list(valid_im_cs) 
    valid_ones = []
    for ph_env in valid_ph_envs:
        valid_ones.append(ImSolveInfo(ph_env, valid_im_cs, all_valid_cs, True))
    # invalid one
    invalid_ones = _get_invalid_validition_info(imm_ph_dict, all_valid_cs, len(valid_ty_cs), valid_ph_envs)
    all_v_im_solve_infos = valid_ones + invalid_ones
    return all_v_im_solve_infos

def _get_valid_validation_info(inst_info:GptResponseData):
    all_cs_ds = inst_info.raw_validate_input_constraints + inst_info.raw_validate_context_constraints
    # print('XXXXXXXXXXXXX all_cs_ds', all_cs_ds)
    valid_ty_cs, valid_im_cs = ConstraintFactory.determine_valid_constraint_group(all_cs_ds)
    # combine valid_ty_constraints 
    validation_cs_from_type_part_dict = get_ty_validation_cs_from_type_part_dict(inst_info.inner_type_part)
    combine_ty_eq_const_constraints(valid_ty_cs, validation_cs_from_type_part_dict)
    # 
    valid_im_cs = valid_im_cs
    return valid_ty_cs,valid_im_cs

def _get_invalid_validition_info(imm_ph_dict, all_valid_cs, ty_cs_num, valid_ph_envs)->list[ImSolveInfo]:
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
            invalid_ph_envs = [PHEnv(imm_ph_dict, cur_ty_cs)]
            for ph_env in invalid_ph_envs:
                # print('invalid_ph_envs', invalid_ph_envs)
                ty_invalid_ones.append(ImSolveInfo(ph_env, cur_im_cs , cur_to_solve_cs, False))
        else:
            for ph_env in valid_ph_envs:
                other_invalid_ones.append(ImSolveInfo(ph_env, cur_im_cs, cur_to_solve_cs, False))
    return ty_invalid_ones + other_invalid_ones


def _determine_valid_ph_env(type_constraints:List[TypeConstraint], imm_ph_dict:dict[str, ImmPH])->List[PHEnv]:
    type_solutions:List[List[OpTypeSolution]] = []
    for c in type_constraints:
        type_solutions.append(c.get_valid_candis())
    final_solutions = _summary_type_slution(type_solutions)
    envs = []
    for fs in final_solutions:
        _op_ph_dicts = _get_op_ph_dicts_from_ty_solution(fs)
        for op_ph_dict in _op_ph_dicts:
            ph_dict = {**op_ph_dict, **imm_ph_dict}
            env = PHEnv(ph_dict)
            envs.append(env)
    return envs


def _summary_type_slution(type_solutions:List[List[OpTypeSolution]])->List[OpTypeSolution]:
    # type_solutions
    all_combes = product(*type_solutions)
    final_solutions = []
    for comb in all_combes:
        final_solution = combine_type_solution(comb)
        final_solutions.append(final_solution)
    return final_solutions
        
    
def _get_op_ph_dicts_from_ty_solution(ty_solution:OpTypeSolution)->List[dict[str, OperandPH]]:
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

def repr_val(val):
    if isinstance(val, (dict, list)):
        return val
    return str(val)

def one_input_c_ill_formatted(cur_input_c):
    assert isinstance(cur_input_c, dict)
    # is_illformatted = False
    # is_illformatted = len(cur_input_c) != 3
    invalid_tokens = {'undefined', 'invalid_vector'}
    is_illformatted = None
    if len(cur_input_c) == 4:
        if set(cur_input_c.keys()) == {'v1', 'v2', 'relation', 'full_attrs'}:
            is_illformatted = False
    elif len(cur_input_c) == 3:
        if set(cur_input_c.keys()) != {'v1', 'v2', 'relation'}:
            raise FailedParsingException(f'Invalid constraint representation: {cur_input_c}. Specifically, the keys should be either {{"v1", "v2", "relation"}} or {{"v1", "v2", "relation", "full_attrs"}}. Rather than {set(cur_input_c.keys())}')
        v1 = repr_val(cur_input_c['v1'])
        v2 = repr_val(cur_input_c['v2'])
        relation = repr_val(cur_input_c['relation'])
        # print('v1', type(v1), repr_val(v1))
        # print('v2', type(v2), repr_val(v2))
        # print('relation', type(relation), repr_val(relation))
        if isinstance(v1, str) and isinstance(v2, str) and isinstance(relation, str):
            if set([v1, v2]).intersection(invalid_tokens):
                is_illformatted = True
            else:
                is_illformatted = False
        
        if isinstance(v1, str) and isinstance(v2, list) and isinstance(relation, str):
            if set([v1, *v2]).intersection(invalid_tokens):
                is_illformatted = True
            else:
                is_illformatted = False
    if len(cur_input_c) == 2:
        raise FailedParsingException(f'Invalid constraint representation: {cur_input_c}')
    if is_illformatted is None:
        raise FailedParsingException(f'Invalid constraint representation: {cur_input_c}')
    # if is_illformatted:
    #     print('SADASDXCVBYT ill formated', cur_input_c)
    return is_illformatted
    