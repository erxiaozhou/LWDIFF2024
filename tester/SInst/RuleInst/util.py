
from typing import Union

from ..InstModel.CombinedConstraint import CombinedAndConstraint

from ..InstModel.PlaceHolder import ImmPH, OperandPH
from ..InstModel.ValConstraint import ValConstraint
from itertools import chain

def get_ph_constraint_idx(ph_num, constraints:list[ValConstraint], for_imm):
    ph_idx2constraint_idx = [[] for _ in range(ph_num)]    
    for cidx, c in enumerate(constraints):
        if for_imm:
            ph_idxs = c.related_imm_idxs
        else:
            ph_idxs = c.related_op_idxs
        for ph_idx in ph_idxs:
            ph_idx2constraint_idx[ph_idx].append(cidx)
    return ph_idx2constraint_idx


def ph2constraint_idxs(constraints:list[ValConstraint])->dict[Union[ImmPH, OperandPH], list[int]]:
    result:dict[Union[ImmPH, OperandPH], list[int]] = {}
    for cidx, c in enumerate(constraints):
        for ph in chain(c.related_imms, c.related_ops):
            result.setdefault(ph, []).append(cidx)
    return result


def get_unique_cs_and_process_and(cal_constraints)->list[ValConstraint]:
    unique_val_constraints = []

    for v in cal_constraints:
        if not isinstance(v, CombinedAndConstraint):
            if v not in unique_val_constraints:
                unique_val_constraints.append(v)
        else:
            unique_cs_in_and = get_unique_cs_and_process_and(v.constraints)
            for u in unique_cs_in_and:
                if u not in unique_val_constraints:
                    unique_val_constraints.append(u)
    return unique_val_constraints
