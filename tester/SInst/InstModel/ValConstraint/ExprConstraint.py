from typing import Optional, Union
from extract_block_mutator.Context import Context
from ..Expr.Expr import Expr
from ..InstValRelation import InstValRelation
from .ValConstraint import ValConstraint
from ..PHEnv import PHEnv
from z3 import And, UGE, UGT, ULE, ULT


class ExprConstraint(ValConstraint):
    def __init__(self, 
                 expr1:Expr, 
                 expr2:Expr, 
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
        if self.expr1 == other.expr1 \
            and self.expr2 == other.expr2 \
            and self.relation == other.relation:
            return True
        elif self.expr1 == other.expr2 \
            and self.expr2 == other.expr1 \
            and self.relation == other.relation.reverse():
            return True
        else:
            return False


    def __repr__(self):
        return f"ExprConstraint({self.expr1}, {self.expr2}, {self.relation})"

    def as_neg_constraint(self):
        return ExprConstraint(self.expr1, self.expr2, self.relation.neg())

    def can_neg(self):
        return True

    def get_symbol_constraint(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None):
        expr1_symbol, expr1_cs = self.expr1.get_symbol_and_constraints(context=context, ph_env=ph_env)
        expr2_symbol, expr2_cs = self.expr2.get_symbol_and_constraints(context=context, ph_env=ph_env)

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
        elif self.relation == InstValRelation.UGE:
            cur_c = UGE(expr1_symbol, expr2_symbol)
        elif self.relation == InstValRelation.UGT:
            cur_c = UGT(expr1_symbol, expr2_symbol)
        elif self.relation == InstValRelation.ULE:
            cur_c = ULE(expr1_symbol, expr2_symbol)
        elif self.relation == InstValRelation.ULT:
            cur_c = ULT(expr1_symbol, expr2_symbol)
            
        else:
            raise ValueError(f"Unsupported relation: {self.relation}")
        return And(cur_c, *expr1_cs, *expr2_cs)

        
    @property
    def contained_context_vals(self):
        vals = set()
        vals.update(self.expr1.contained_context_vals)
        vals.update(self.expr2.contained_context_vals)
        return vals
    
    def _get_related_imms(self):
        imms = set()
        imms.update(self.expr1.related_imms)
        imms.update(self.expr2.related_imms)
        return imms
    
    def _get_related_ops(self):
        ops = set()
        ops.update(self.expr1.related_ops)
        ops.update(self.expr2.related_ops)
        return ops
