from typing import List

from ..specialContextConstVal import specialContextConstVal
from ..ExprConstraintFactory import ExprConstraintFactory

from ..IMConstraints.IMConstraintResult import IMConstraintResult

from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory

from ..SelectFuncConstraint import SelectFuncConstraintFactoryAnd
from ..PHEnv import PHEnv
from ..InstValRelation import InstValRelation
from ..CombinedConstraint import CombinedAndConstraint
from ..ValConstraint import ValConstraint
from ..Expr import get_expr_from_str
from ..Expr import is_expr_str
from .IMConstraint import IMConstraint
from .ExistIMConstraint import ExistIMConstraint


class ExprIMConstraint(IMConstraint):
    def __init__(self, v1:str, v2:str, relation:InstValRelation) -> None:
        self.v1 = str(v1)
        self.v2 = str(v2)
        self.relation = relation

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.v1}, {self.v2}, {self.relation})'

    def as_neg_constraint(self):
        return ExprIMConstraint(self.v1, self.v2, self.relation.neg())

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        # print('!CSDCDVCDVVFV', d)
        
        if len(d) == 3 and set(d.keys()) == {'v1', 'v2', 'relation'}:
            # print('XXXXXXXXXXXXXX', d['v1'], is_expr_str(d['v1']))
            # print('XXXXXXXXXXXXXX', d['v2'], is_expr_str(d['v2']))
            if is_expr_str(d['v1']) and is_expr_str(d['v2']) and InstValRelation.is_valid_str(d['relation']):
                if not ( specialContextConstVal.is_valid_str(d['v1']) and specialContextConstVal.is_valid_str(d['v2'])):
                    return True
        return False
    
    @classmethod
    def from_dict(cls, d: dict):
        # print('||| in ExprIMConstraint.from_dict', d)
        assert cls.is_valid_dict(d)
        relation_ = InstValRelation.from_str(d['relation'])
        assert relation_ is not None
        # if 
        return cls(d['v1'], d['v2'], relation_)

    def _release_constraints(self, ph_env:PHEnv)->List[ValConstraint]:
        expr1 = get_expr_from_str(self.v1, ph_env)
        expr2 = get_expr_from_str(self.v2, ph_env)
        c = ExprConstraintFactory.from_exprs(expr1, expr2, self.relation)
        
        return [c]



    def _get_exist_cs(self, ph_env:PHEnv, *args, **kwds):
        expr1 = get_expr_from_str(self.v1, ph_env)
        expr2 = get_expr_from_str(self.v2, ph_env)
        context_vals:set[specialContextConstVal] = set()
        context_vals.update(expr1.contained_context_vals)

        context_vals.update(expr2.contained_context_vals)
        exist_im_cs:List[ExistIMConstraint] = []
        for context_val in context_vals:
            # for sub val
            if context_val.has_parent_size():
                exist_im_c = ExistIMConstraint(context_val, True)
                exist_im_cs.append(exist_im_c)

        val_cs_ = []
        func_cs_ = []
        for c in exist_im_cs:
            sub_imcrs = c.release_both_constraints(ph_env)
            val_cs_.extend([_c.val_constraint for _c in sub_imcrs])
            func_cs_.extend([_c.select_func_constraint for _c in sub_imcrs])
        
        for context_val in context_vals:
            if context_val.is_may_zero_size() and self.relation == InstValRelation.LT:
                # print('EEEEEE context_val', context_val)
                idx_repr = context_val.idx_repr
                if idx_repr is None or idx_repr.isdigit():
                    c = SelectFuncConstraintFactory.compared_with_context_size_func(
                        0, 
                        context_val, 
                        InstValRelation.LT)
                else:
                    c = SelectFuncConstraintFactory.context_scope_exist_func(
                        context_val.get_candi_set_by_one_param(0)
                )

                func_cs_.append(c)
    
        # assert 0, print(exist_im_cs)
        return val_cs_, func_cs_
        
    
    def release_both_constraints(self, ph_env)->List[IMConstraintResult]:
        val_cs = self._release_constraints(ph_env=ph_env)
        # func_cs = []
        # exist_im_cs = self._get_exist_im_cs(ph_env=ph_env)
        # print('exist_im_cs', exist_im_cs)
        # for c in exist_im_cs:
        #     sub_imcrs = c.release_both_constraints(ph_env)
        #     val_cs_ = [_c.val_constraint for _c in sub_imcrs]
        #     func_cs_ = [_c.select_func_constraint for _c in sub_imcrs]
        #     val_cs.extend(val_cs_)
        #     func_cs.extend(func_cs_)
        _val_cs, func_cs = self._get_exist_cs(ph_env=ph_env)
        val_cs.extend(_val_cs)
        if len(func_cs) == 0:
            func_cs.append(SelectFuncConstraintFactory.get_default_func_constraint())

        if len(val_cs) == 1:
            final_val_c = val_cs[0]
        else:
            final_val_c = CombinedAndConstraint(val_cs)
        if len(func_cs) == 1:
            final_func_c = func_cs[0]
        else:
            final_func_c = SelectFuncConstraintFactoryAnd.generate_a_combined_func_from_SelectFuncConstraints(func_cs)
        result = IMConstraintResult(final_val_c, final_func_c)
        # print('$$$$$$$$$$$$$$$$$$$$$', result)
        return [result]
    
    def can_neg(self) -> bool:
        return True

