from math import log2
import re

from util.util import FailedParsingException
from .ImEqOpTypeIMConstraint import ImEqOpTypeIMConstraint
from .NaiveImmScope import NaiveImmScope
from .ContextValAttrConstraint import OpContextValAttrConstraint, TwoContextValAttrEqConstraint, ValAttrEqConstConstraint
from ..ValConstraint import ValConstraint
from ..TypeConstraint import OpTypeEqOpTypeConstraint, TypeEqConstConstraint, TypeScopeConstraint, TypeConstraint, immTypeEqConstraint
from .IMConstraint import IMConstraint
from .EmptyIMConstraint import EmptyIMConstraint
from .ExistIMConstraint import ExistIMConstraint
from .ExprIMConstraint import ExprIMConstraint
from typing import List, Optional, Tuple
from WasmInfoCfg import val_type_strs


_align_imm_p = re.compile(r'2\^(imm_\d+)')


def _get_align_imm_idx(imm_name:str)->Optional[str]:
    r = _align_imm_p.findall(imm_name)
    if r:
        return r[0]
    return None

def _preprocess_d_for_alignment_immx(d):
    v1_text = d.get('v1')
    if v1_text is None:
        return d
    possible_imm_name = _get_align_imm_idx(v1_text)
    if possible_imm_name is None:
        return d
    d['v1'] = possible_imm_name
    return d


def _preprocess_d_for_alignment_imm(d):
    v1_text = d.get('v1')
    if v1_text is None:
        return d
    possible_imm_name = _get_align_imm_idx(v1_text)
    if possible_imm_name is None:
        return d
    if 'v2' not in d:
        raise NotImplementedError(f"Unexpected : v2 is not in the dict: {d}")
    d['v1'] = possible_imm_name
    # process v2
    if d['v2'] == '0':  # ! trans it to a always true constraint
        if 'relation' in d:
            d['relation'] = 'ge'
        else:
            raise NotImplementedError(f"Unexpected : relation is not in the dict: {d}")
    elif isinstance(d['v2'], str):
        ori_val = eval(d['v2'])
        # print('KKKKKK v2', d['v2'])
        d['v2'] = str(int(log2(ori_val)))
    elif isinstance(d['v2'], list):
        ori_vals = [eval(x) for x in d['v2']]
        d['v2'] = [str(int(log2(e))) for e in ori_vals]
    # if isinstance(d.get('v2'), 
    # print('new d', d)
    return d


class ConstraintFactory:
    @staticmethod
    def is_type_constraint_dict(d: dict) -> bool:
        if TypeEqConstConstraint.is_valid_dict(d):
            return True
        if TypeScopeConstraint.is_valid_dict(d):
            return True
        if immTypeEqConstraint.is_valid_dict(d):
            return True
        if OpTypeEqOpTypeConstraint.is_valid_dict(d):
            return True
        return False

    @staticmethod
    def determine_type_constraint(d: dict) -> Tuple[List[TypeConstraint], List[IMConstraint]]:
        if TypeEqConstConstraint.is_valid_dict(d):
            return [TypeEqConstConstraint.from_d(d)], []
        if TypeScopeConstraint.is_valid_dict(d):
            return [TypeScopeConstraint.from_d(d)], []
        if immTypeEqConstraint.is_valid_dict(d):
            return [immTypeEqConstraint.from_d(d)], []
        if OpTypeEqOpTypeConstraint.is_valid_dict(d):
            return [OpTypeEqOpTypeConstraint.from_d(d)], []
        raise FailedParsingException(f"The description of the type constraint is ill-formatted: {d}")

    @staticmethod
    def determine_value_constraint(d: dict) -> IMConstraint:
        # ! just for alignment immediate argument
        try:
            d = _preprocess_d_for_alignment_imm(d)
        except AttributeError as e:
            raise e
        # possible_alignment_imm_name = _get_align_imm_idx
     
        if ExprIMConstraint.is_valid_dict(d):
            return ExprIMConstraint.from_dict(d)
        if OpContextValAttrConstraint.is_valid_dict(d):
            return OpContextValAttrConstraint.from_dict(d)
        if ValAttrEqConstConstraint.is_valid_dict(d):
            return ValAttrEqConstConstraint.from_dict(d)
        if ImEqOpTypeIMConstraint.is_valid_dict(d):
            return ImEqOpTypeIMConstraint.from_dict(d)
        if NaiveImmScope.is_valid_dict(d):
            return NaiveImmScope.from_dict(d)
        
        if ExistIMConstraint.is_valid_dict(d):
            return ExistIMConstraint.from_dict(d)
        elif TwoContextValAttrEqConstraint.is_valid_dict(d):
            return TwoContextValAttrEqConstraint.from_dict(d)
        info = f"The description of the constraint is ill-formatted: {d}"
        indication_info = _get_fine_exception_info(d)
        if indication_info:
            info = f'{info}. {indication_info}'
        raise FailedParsingException(info)

    @staticmethod
    def determine_valid_constraint_group(ds: List[dict]) -> Tuple[List[TypeConstraint], List[IMConstraint]]:
        # print('||||||||||||||||||',ds)
        type_cs:List[TypeConstraint] = []
        im_cs:List[IMConstraint] = []
        for d in ds:
            if ConstraintFactory.is_type_constraint_dict(d):
                cur_ty_cs, cur_val_cs = ConstraintFactory.determine_type_constraint(d)
                type_cs.extend(cur_ty_cs)
                im_cs.extend(cur_val_cs)
            else:
                im_cs.append(ConstraintFactory.determine_value_constraint(d))
        return type_cs, im_cs

    @staticmethod
    def determine_exec_im_constraint(d: dict) ->IMConstraint:
        assert isinstance(d, dict)
        if EmptyIMConstraint.is_valid_dict(d):
            return EmptyIMConstraint.from_dict(d)
        if ExprIMConstraint.is_valid_dict(d):
            return ExprIMConstraint.from_dict(d)
        if ValAttrEqConstConstraint.is_valid_dict(d):
            return ValAttrEqConstConstraint.from_dict(d)
        if NaiveImmScope.is_valid_dict(d):
            return NaiveImmScope.from_dict(d)
        raise FailedParsingException(f"The description of the constraint of the execution behavior is ill-formatted: {d}")
    @staticmethod
    def get_empty_im_constraint() -> IMConstraint:
        return EmptyIMConstraint()
    @staticmethod
    def generate_empty_im_constraint() -> IMConstraint:
        return EmptyIMConstraint()


def _get_fine_exception_info(d: dict):
    debug_info = []
    if 'v2' in d and _vals_are_types(d['v2']) and ('v1' in d) and (not d['v1'].endswith('.type')):
        debug_info.append(f"Since the value of 'v1' is a valid value type, consider use `.type` (e.g., <xxx>.type) to represent a type instead of {d['v1']}.")
    if _vals_are_types(d.get('v2'))  and 'eq' in d.get('relation', ''):
        debug_info.append(f"Please consdier using the `eq` relation instead of {d['relation']} and keep the constraint has the correct semantics.") 
    if len(debug_info) == 0:
        return f'{d}'
    else:
        return '\n'.join(debug_info)

def _vals_are_types(v):
    if isinstance(v, str):
        return v in val_type_strs
    if isinstance(v, list):
        return all(_vals_are_types(e) for e in v)
