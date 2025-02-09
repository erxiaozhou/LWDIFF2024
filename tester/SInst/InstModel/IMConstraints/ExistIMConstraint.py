import re
from typing import List

from WasmInfoCfg import ContextValAttr

from ..ContextScopeVal import paramSpecialIdxsScope
from ..ExprConstraintFactory import ExprConstraintFactory
from ..Expr import Expr

from ..ScopeValConstraint import ExprInContextScope
from ..specialContextConstVal import specialContextConstVal

from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory

from .IMConstraintResult import IMConstraintResult
from ..SpecialOperand import ConstVal
from ..InstValRelation import InstValRelation
from ..EmptyValConstraint import EmptyValConstraint
from ..Expr import get_expr_from_str

from .IMConstraint import IMConstraint


class ExistIMConstraint(IMConstraint):
    imm_p = re.compile(r'\[(.*?)\]')
    def __init__(self, 
                 context_val:specialContextConstVal, 
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
        if self.context_val.can_get_scope() and self.context_val.context_val_type == ContextValAttr.OneFuncRef:
        # if  Faise:
            # print('DSFSDFSFSDQWE   self.context_val', self.context_val)
            # 
            # considered_context_val = specialContextConstVal(
            #     self.context_val.
            # )
            # # 
            scope: paramSpecialIdxsScope = self.context_val.get_candi_set_by_one_param()
            # print('DSFSDFSFSDQWE scope', scope)
            func_c = SelectFuncConstraintFactory.context_scope_exist_func(scope)
            expr_ = get_expr_from_str(self.context_val.idx_repr, ph_env)
            assert isinstance(expr_, Expr)
            val_c = ExprInContextScope(expr_, scope, self.exists)
            # print('ZZZZZDDDDD', 'val_c', val_c)
            result = IMConstraintResult(val_c, func_c)
        else: 
            # 
            assert self.context_val.has_parent_size()
            self.parent_size = self.context_val.get_parent_size_val()
            assert not self.parent_size.has_parent_size()  # ，，，parentparent
            # 
            relation = InstValRelation.LT
            if not self.exists:
                relation = relation.neg()
            if ConstVal.is_const_val(self.context_val.idx_repr):
                assert self.context_val.idx_repr is not None
                l_const = ConstVal.from_str(self.context_val.idx_repr).n
                r_context_val_attr = self.parent_size

                c = SelectFuncConstraintFactory.compared_with_context_size_func(
                    l_const, 
                    r_context_val_attr, 
                    relation)
                result = IMConstraintResult(EmptyValConstraint(), c)
            else:
                v1 = ph_env.get_ph(self.context_val.idx_repr)
                c = ExprConstraintFactory.from_exprs(v1, self.parent_size,relation)
                gt0_c = SelectFuncConstraintFactory.compared_with_context_size_func(
                    0, 
                    self.parent_size, 
                    relation)
                result = IMConstraintResult(c, gt0_c)
        
        # if self.context_val.has_parent_size():
        #     self.parent_size = self.context_val.get_parent_size_val()
        #     assert not self.parent_size.has_parent_size()  # ，，，parentparent
        #     relation = InstValRelation.LSConst
        #     raise NotImplementedError 
        return [result]

    @classmethod
    def from_dict(cls, d: dict):
        # check d pattern
        assert cls.is_valid_dict(d)
        VariableName = d['VariableName']
        
        context_variable = specialContextConstVal.from_str(VariableName)
        if isinstance(d['Exist'], bool):
            exists = d['Exist']
        else:
            raise NotImplementedError
        assert exists
        return cls(context_variable, exists)
    