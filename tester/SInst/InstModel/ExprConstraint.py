from typing import Optional, Union
from .get_symbol_util import get_val_symbol_for_expr
from extract_block_mutator.Context import Context
from .Expr import OneValExpr, BinExpr
from .InstValRelation import InstValRelation
from .ValConstraint import ValConstraint
from .PHEnv import PHEnv
from z3 import And


class ExprConstraint(ValConstraint):
    def __init__(self, 
                 expr1:Union[OneValExpr, BinExpr], 
                 expr2:Union[OneValExpr, BinExpr], 
                 relation:InstValRelation):
        
        self.expr1 = expr1
        self.expr2 = expr2
        self.relation = relation
        related_imms = self._get_related_imms()
        related_ops = self._get_related_ops()
        super().__init__(related_imms, related_ops)

    def __eq__(self, other):
        if not isinstance(other, ExprConstraint):
            return False
        return self.expr1 == other.expr1 and self.expr2 == other.expr2 and self.relation == other.relation


    def __repr__(self):
        return f"ExprConstraint({self.expr1}, {self.expr2}, {self.relation})"

    def as_neg_constraint(self):
        return ExprConstraint(self.expr1, self.expr2, self.relation.neg())

    def can_neg(self):
        return True

    def get_symbol_constraint(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None):
        expr1_symbol, expr1_cs = get_val_symbol_for_expr(self.expr1, context=context, ph_env=ph_env)
        expr2_symbol, expr2_cs = get_val_symbol_for_expr(self.expr2, context=context, ph_env=ph_env)

        if self.relation == InstValRelation.EQ:
            cur_c = expr1_symbol == expr2_symbol
        elif self.relation == InstValRelation.NE:
            cur_c = expr1_symbol != expr2_symbol
        elif self.relation == InstValRelation.LE:
            cur_c = expr1_symbol <= expr2_symbol
        elif self.relation == InstValRelation.LT:
            cur_c = expr1_symbol < expr2_symbol
        elif self.relation == InstValRelation.GT:
            cur_c = expr1_symbol > expr2_symbol
        elif self.relation == InstValRelation.GE:
            cur_c = expr1_symbol >= expr2_symbol
        else:
            raise ValueError(f"Unsupported relation: {self.relation}")
        return And(cur_c, *expr1_cs, *expr2_cs)

        
    @property
    def contained_context_vals(self):
        vals = set()
        vals.update(self.expr1.contained_context_vals)
        vals.update(self.expr2.contained_context_vals)
        return vals
    # @property
    def _get_related_imms(self):
        imms = set()
        imms.update(self.expr1.related_imms)
        imms.update(self.expr2.related_imms)
        return imms
    # @property
    def _get_related_ops(self):
        ops = set()
        ops.update(self.expr1.related_ops)
        ops.update(self.expr2.related_ops)
        return ops
