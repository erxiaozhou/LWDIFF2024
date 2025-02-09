from util.util import FailedParsingException
from ..InstModel.InstValRelation import InstValRelation
from ..InstModel.OnePhConstraint import OnePhConstraint
from .PlaceHolder import ImmPH
from .ValConstraint import ValConstraint
from .SpecialOperand import ConstVal, ExternSpecialOpVal, FuncNullSpecialOpVal, TypeImmSpecialVal, AlignmentImmVal, OffsetImmVal, RefTypeImmVal, V128SpecialVal
from .SpecialOperand import I32SpecialVal, I64SpecialVal
from .SpecialOperand import F32SpecialVal, F64SpecialVal


_imm_attr2_special_val = {
    'i32': I32SpecialVal.Rdm,
    'i64': I64SpecialVal.Rdm,
    'f32': F32SpecialVal.Rdm,
    'f64': F64SpecialVal.Rdm,
    'v128': V128SpecialVal.Rdm,
    'offset': OffsetImmVal.Valid,
    'align': AlignmentImmVal.One,
    'valtype': TypeImmSpecialVal.Rdm,
    'funcref': FuncNullSpecialOpVal.FuncNull,
    'externref': ExternSpecialOpVal.ExternNull,
}


def set_cs_for_unc_imm(rule):
    return set_cs_for_unc_imm_core(rule, _imm_attr2_special_val)


# ======== rg part =================
imm_attr2_special_val_rg = {
    'i32': I32SpecialVal.PRdm,
    'i64': I64SpecialVal.PRdm,
    'f32': F32SpecialVal.Rdm,
    'f64': F64SpecialVal.Rdm,
    'v128': V128SpecialVal.Rdm,
    'offset': OffsetImmVal.PValid,
    'align': AlignmentImmVal.One,
    'valtype': TypeImmSpecialVal.Rdm,
    'funcref': FuncNullSpecialOpVal.FuncNull,
    'externref': ExternSpecialOpVal.ExternNull,
}


def set_cs_for_unc_imm_rg(rule) -> None:
    return set_cs_for_unc_imm_core(rule, imm_attr2_special_val_rg)


# ========== core part ================
def set_cs_for_unc_imm_core(rule, imm_attr2_special_val) -> None:
    unconstrained_imm_idxs = [idx for idx, x in enumerate(
        rule.imm_idx2constraint_idx) if len(x) == 0]
    # return all_constrained
    imm_cs = []
    for idx in unconstrained_imm_idxs:
        imm_ph = rule.ph_env.get_ph(f'imm_{idx}')
        assert isinstance(imm_ph, ImmPH)
        imm_cs.append(generate_val_constraint_for_one_imm(
            imm_ph, imm_attr2_special_val))
    rule.val_constraints.extend(imm_cs)


def generate_val_constraint_for_one_imm(imm_ph: ImmPH, imm_attr2_special_val) -> ValConstraint:

    imm_attr = imm_ph.attr
    if imm_attr not in imm_attr2_special_val:
        print('VVVVVVVVVVVVVVVV imm_attr2_special_val', imm_attr2_special_val)
        raise Exception(
            f'Unexpected type attributute  {imm_attr}')
        raise FailedParsingException(
            f'Unexpected  type attributute {imm_attr}')
    special_val = imm_attr2_special_val[imm_attr]
    # concrete_val = special_val.concrete_val()
    return OnePhConstraint(imm_ph, special_val, InstValRelation.EQ)
