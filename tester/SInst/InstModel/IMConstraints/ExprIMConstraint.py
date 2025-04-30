from typing import List

from SInst.InstModel.SelectFuncConstraintFactory import SelectFuncConstraintFactory

from .ReleaseExistConstraintsUtil import release_exist_cs_from_expr

from ..SpecialContextConstVal.SpecialContextConstValFactory import SpecialContextConstValFactory
from ..ExprConstraintFactory import ExprConstraintFactory

from .IMConstraintResult import IMConstraintResult, get_imconstraint_result_practical

from ..InstValRelation import InstValRelation
from ..Expr.tool import get_expr_from_str
from ..Expr.tool import is_expr_str
from .IMConstraint import IMConstraint
from ..InstValRelationHelper import InstValRelationHelper


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
        if len(d) == 3 and set(d.keys()) == {'v1', 'v2', 'relation'}:
            if not isinstance(d['v1'], str) or not isinstance(d['v2'], str) or not isinstance(d['relation'], str):
                return False
            if is_expr_str(d['v1']) and is_expr_str(d['v2']) and InstValRelationHelper.is_valid_str(d['relation']):
                if not ( SpecialContextConstValFactory.is_valid_str(d['v1']) and SpecialContextConstValFactory.is_valid_str(d['v2'])):
                    return True
        return False
    
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        relation_ = InstValRelationHelper.from_str(d['relation'])
        assert relation_ is not None
        return cls(d['v1'], d['v2'], relation_)


    def release_both_constraints(self, ph_env)->List[IMConstraintResult]:
        expr1 = get_expr_from_str(self.v1, ph_env)
        expr2 = get_expr_from_str(self.v2, ph_env)
        val_cs = []
        func_cs = []
        _val_cs, _func_cs = release_exist_cs_from_expr(expr1, ph_env)
        val_cs.extend(_val_cs)
        func_cs.extend(_func_cs)
        _val_cs, _func_cs = release_exist_cs_from_expr(expr2, ph_env)
        val_cs.extend(_val_cs)
        func_cs.extend(_func_cs)

        expr_val_cs, expr_func_cs = ExprConstraintFactory.from_exprs_practically(expr1, expr2, self.relation)
        val_cs.extend(expr_val_cs)
        func_cs.extend(expr_func_cs)
        

        result = get_imconstraint_result_practical(
            val_constraint=val_cs,
            func_constraint=func_cs
        )
        return [result]
    
    def can_neg(self) -> bool:
        return True
