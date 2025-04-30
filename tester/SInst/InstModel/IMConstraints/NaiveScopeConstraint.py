from typing import List

from SInst.InstModel.ContextScopeVal import paramSpecialIdxsScope
from SInst.InstModel.SpecialContextConstVal.SpecialContextConstVal import SpecialContextScopeVal, get_expr_from_str
from SInst.InstModel.SpecialContextConstVal.SpecialContextConstValFactory import SpecialContextConstValFactory
from SInst.InstModel.ValConstraint.ScopeValConstraint import ExprInContextScope
from WasmInfoCfg import ContextValAttr

from ..CPlaceHolder import is_default_imm_ph_name_or_op_ph_name
from ..CombinedConstraint import CombinedOrConstraint
from ..ExprConstraintFactory import ExprConstraintFactory
from ..InstValRelation import InstValRelation
from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory
from ..ConstVal import ConstVal
from ..SpecialOperand import HeapTypeVal
from .IMConstraintResult import IMConstraintResult, get_imconstraint_result_practical
from .IMConstraint import IMConstraint


class NaiveScopeConstraint(IMConstraint):
    def __init__(self, ph_repr:str, attrs:set, is_inclusive:bool):
        self.ph_repr = ph_repr
        self.attrs = attrs
        self.is_inclusive = is_inclusive
        assert is_inclusive 
    def can_neg(self) -> bool:
        return False
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.ph_repr}, {self.attrs}, {self.is_inclusive})'
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3 and set(d.keys()) == {'v1', 'v2', 'relation'}:
            if d['relation'] == 'in':
                if isinstance(d['v1'], str) \
                    and is_default_imm_ph_name_or_op_ph_name(d['v1']):
                    if isinstance(d['v2'], list):
                        return True
        return False
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        imm_name = d['v1']
        attrs = [_get_attr_from_str(s) for s in d['v2']]
        return cls(imm_name, set(attrs), d['relation'] == 'in')

    def release_both_constraints(self, ph_env,*args, **kwds)->List[IMConstraintResult]:
        v1 = ph_env.get_ph(self.ph_repr)
        cs = []
        for target_v in self.attrs:
            val_c = ExprConstraintFactory.from_exprs_directly(v1, target_v,InstValRelation.EQ)
            cs.append(val_c)
        final_val_c = CombinedOrConstraint(cs)
        result = get_imconstraint_result_practical(
            val_constraint=final_val_c,
        )
        return [result]



def _get_attr_from_str(s:str):
    if HeapTypeVal.is_valid_str(s):
        return HeapTypeVal.from_str(s)
    if s.isdigit():
        return ConstVal.from_str(s)
    raise NotImplementedError(f'_get_attr_from_str not implemented for {s}')


class NaiveContextScopeConstraint(IMConstraint):
    def __init__(self, ph_repr:str, context_scope:SpecialContextScopeVal, is_inclusive:bool):
        self.ph_repr = ph_repr
        self.context_scope = context_scope
        self.is_inclusive = is_inclusive
        assert is_inclusive 
    def can_neg(self) -> bool:
        return False
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.ph_repr}, {self.context_scope}, {self.is_inclusive})'
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3 and set(d.keys()) == {'v1', 'v2', 'relation'}:
            if d['relation'] == 'in':
                if isinstance(d['v1'], str) \
                    and is_default_imm_ph_name_or_op_ph_name(d['v1']):
                    if SpecialContextConstValFactory.is_valid_scope_str(d['v2']):
                        return True
        return False
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        imm_name = d['v1']
        context_scope = SpecialContextConstValFactory.from_str(d['v2'])
        return cls(imm_name, context_scope, d['relation'] == 'in')  # type: ignore

    def release_both_constraints(self, ph_env,*args, **kwds)->List[IMConstraintResult]:
        v1 = get_expr_from_str(self.ph_repr, ph_env)
        assert self.context_scope.context_val_type == ContextValAttr.OneFuncRef or self.context_scope.context_val_type == ContextValAttr.FuncRefs
        scope: paramSpecialIdxsScope = self.context_scope.get_candi_set_by_one_param()
        func_c = SelectFuncConstraintFactory.context_scope_exist_func(scope)
        val_c = ExprInContextScope(v1, scope, self.is_inclusive)
        result = get_imconstraint_result_practical(
            val_constraint=val_c, 
            func_constraint=func_c
        )
        return [result]

