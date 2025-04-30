from ..Exceptions import RequireContextException
from extract_block_mutator.Context import Context
from ..PHEnv import PHEnv
from .ValConstraint import ValConstraint
from ..Expr.Expr import Expr
from ..ContextScopeVal import paramSpecialIdxsScope
from z3 import Or, And, Not


class ExprInContextScope(ValConstraint):
    def __init__(self, expr:Expr, scope:paramSpecialIdxsScope, hold_true:bool):
        self.expr = expr
        self.scope = scope
        self.hold_true = hold_true

        related_imms = self.expr.related_imms
        related_ops = self.expr.related_ops
        assert isinstance(related_imms, set)
        assert isinstance(related_ops, set)
        super().__init__(related_imms, related_ops)
        
    def __repr__(self):
        return f'ExprInContextScope({self.expr}, {self.scope}, {self.hold_true})'
    
    def get_symbol_constraint(self,context:Context, ph_env:PHEnv, *args, **kwds):
        if context is None:
            raise RequireContextException
        concrete_value_set = self.scope.get_concrete_valset_from_context(context)
        lsymbol, expr_inner_cs = self.expr.get_symbol_and_constraints(context=context, ph_env=ph_env)
        val_set_cs = []
        for val in concrete_value_set:
            val_set_cs.append(lsymbol == val)
        
        if len(val_set_cs) == 0:
            return False
        elif len(val_set_cs) > 1:
            val_set_c = Or(val_set_cs)
        else:
            val_set_c = val_set_cs[0]
       
        
        if not self.hold_true:
            val_set_c = Not(val_set_c)
        if len (expr_inner_cs) == 0:
            final_c = val_set_c
        else:
            final_c = And(val_set_c, *expr_inner_cs)
        return final_c

