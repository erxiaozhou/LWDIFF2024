import re
from typing import List

from SInst.InstModel.SpecialContextConstVal.SpecialContextConstVal import SpecialContextScopeVal
from WasmInfoCfg import ContextValAttr

from ..ContextScopeVal import paramSpecialIdxsScope
from ..ExprConstraintFactory import ExprConstraintFactory
from ..Expr import Expr

from ..ValConstraint.ScopeValConstraint import ExprInContextScope
from ..SpecialContextConstVal.SpecialContextConstVal import SpecialContextConstVal, SpecialContextOneSec, get_one_def0_val, get_parent_size_val
from ..SpecialContextConstVal.SpecialContextConstValFactory import SpecialContextConstValFactory

from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory

from .IMConstraintResult import IMConstraintResult, get_imconstraint_result_practical
from ..ConstVal import ConstVal
from ..InstValRelation import InstValRelation
from ..Expr.tool import get_expr_from_str, is_expr_str

from .IMConstraint import IMConstraint


class ExistIMConstraint(IMConstraint):
    imm_p = re.compile(r'\[(.*?)\]')
    def __init__(self, 
                 context_val:SpecialContextConstVal, 
                 exists:bool) -> None:
        self.context_val = context_val
        self.exists = exists
        
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.context_val}, {self.exists})'
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 2 and set(d.keys()) == {'VariableName', 'Exist'}:
            return True
        return False
    def can_neg(self) -> bool:
        return True
        
    def as_neg_constraint(self):
        return ExistIMConstraint(self.context_val, not self.exists)

    def release_both_constraints(self, ph_env)->List[IMConstraintResult]:
        func_c = None
        val_c = None
        if self.context_val.is_scope():
            assert self.context_val.context_val_type == ContextValAttr.OneFuncRef  # 
            assert isinstance(self.context_val, SpecialContextScopeVal)
            scope: paramSpecialIdxsScope = self.context_val.get_candi_set_by_one_param()
            func_c = SelectFuncConstraintFactory.context_scope_exist_func(scope)
            assert self.context_val.idx_repr is not None, print('self.context_val.idx_repr is None')
            expr_ = get_expr_from_str(self.context_val.idx_repr, ph_env)
            val_c = ExprInContextScope(expr_, scope, self.exists)
        else: 
            if self.context_val.has_parent_size():
                existing_context_val = self.context_val
            else:
                assert isinstance(self.context_val, SpecialContextOneSec)  # to ignore the type warning
                existing_context_val = get_one_def0_val(self.context_val)
            
            self.parent_size = get_parent_size_val(existing_context_val)
            if self.exists:  # ，  else ，，parent，， 
                relation = InstValRelation.LT
            else:
                relation = InstValRelation.GT
            assert existing_context_val.idx_repr is not None
            if ConstVal.is_valid_str(existing_context_val.idx_repr):
                l_const = ConstVal.from_str(existing_context_val.idx_repr).n
                r_context_val_attr = self.parent_size

                func_c = SelectFuncConstraintFactory.compared_with_context_size_func(
                    l_const, 
                    r_context_val_attr, 
                    relation)
            else:
                assert is_expr_str(existing_context_val.idx_repr)
                expr_ = get_expr_from_str(existing_context_val.idx_repr, ph_env)
                val_c = ExprConstraintFactory.from_exprs_directly(expr_, self.parent_size,relation)
                func_c = []
        result = get_imconstraint_result_practical(
            val_constraint=val_c,
            func_constraint=func_c
        )
        return [result]

    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        VariableName = d['VariableName']
        
        context_variable = SpecialContextConstValFactory.from_str(VariableName)
        if isinstance(d['Exist'], bool):
            exists = d['Exist']
        else:
            raise NotImplementedError
        assert exists
        return cls(context_variable, exists)
    