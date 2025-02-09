from .RuleV2 import CSSatisfiable, RuleV2
from ..InstModel.Exceptions import RequireContextException
from ..InstModel.solver import ValConstraintSolver


def one_rule_is_unsatisfiable(rule: RuleV2)->CSSatisfiable:
    try:
        r = ValConstraintSolver.is_satisfiable(rule, ph_env=rule.ph_env)
        if r:
            result = CSSatisfiable.SATISFIABLE
        else:
            result = CSSatisfiable.UNSATISFIABLE
    except RequireContextException:
        result = CSSatisfiable.UNKNOWN
        # raise NotImplementedError
    return result
