from typing import List
from ..Expr.Expr import Expr

from ..SelectFuncConstraint import SelectFuncConstraint
from ..PHEnv import PHEnv
from ..ValConstraint import ValConstraint
from .ExistIMConstraint import ExistIMConstraint


def release_exist_cs_from_expr(expr:Expr, ph_env:PHEnv)->tuple[List[ValConstraint], List[SelectFuncConstraint]]:
    context_vals = expr.contained_context_vals
    val_cs_ = []
    func_cs_ = []
    for context_val in context_vals:
        if context_val.has_parent_size():
            exist_im_c = ExistIMConstraint(context_val, True)
            sub_imcrs = exist_im_c.release_both_constraints(ph_env)
            val_cs_.extend([_c.val_constraint for _c in sub_imcrs])
            func_cs_.extend([_c.select_func_constraint for _c in sub_imcrs])
    return val_cs_, func_cs_