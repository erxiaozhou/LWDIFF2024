from random import choice
from typing import List, Tuple, Union

from WasmInfoCfg import AttrConst, globalValMut
from WasmInfoCfg import ElemSecAttr
from WasmInfoCfg import DataSegAttr
from ..Expr import Expr
from ..Expr.tool import get_expr_from_str
from ..PHEnv import PHEnv
from ..CPlaceHolder import OperandPH
from ..ValConstraint.ScopeValConstraint import ExprInContextScope
from ..SelectFuncConstraint import SelectFuncConstraintFactoryAnd, SelectFuncConstraintFactoryOr
from .IMConstraintResult import IMConstraintResult, get_imconstraint_result_practical
from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory
from ..SpecialContextConstVal.SpecialContextConstVal import SpecialContextConstVal, SpecialContextScopeVal
from ..SpecialContextConstVal.util import OneContextValAttr
from ..SpecialContextConstVal.SpecialContextConstValFactory import SpecialContextConstValFactory
from ..CombinedConstraint import CombinedAndConstraint, CombinedOrConstraint
from .IMConstraint import IMConstraint
from .ExistIMConstraint import ExistIMConstraint
from WasmInfoCfg import val_type_strs


class OpContextValAttrConstraint(IMConstraint):
    def __init__(self, op_attr_repr:str, context_val:SpecialContextConstVal, eq:bool) -> None:
        self.op_attr_repr = op_attr_repr
        assert context_val.is_scope()
        self.context_val = context_val
        self.eq = eq


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.op_attr_repr}, {self.context_val}, {self.eq})'

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if set(d.keys()) != {'v1', 'v2', 'relation'}:
            return False
        if not (d['v1'].startswith('op_') and d['v1'].endswith('.type')):
            return False
        if not SpecialContextConstValFactory.is_valid_str(d['v2']):
            return False
        if not (d['relation'] in {'eq', 'ne'}):
            return False
        return True
    
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        eq = d['relation'] == 'eq'
        op_attr_repr = d['v1']
        context_attr_repr = d['v2']
        context_val = SpecialContextConstValFactory.from_str(context_attr_repr)
        return cls(op_attr_repr, context_val, eq)
        
    def release_both_constraints(self, ph_env:PHEnv)->List[IMConstraintResult]:
        if '.type' in self.op_attr_repr:
            op_name = self.op_attr_repr.replace('.type', '')
            op_ph = ph_env.get_ph(op_name)
            assert isinstance(op_ph, OperandPH)
            op_type = op_ph.ty
            assert op_type in val_type_strs
            assert self.context_val.val_attr == OneContextValAttr.val_type  
            assert isinstance(op_type, str)
            if self.eq:
                vals = {op_type}
            else:
                vals = val_type_strs - {op_type}
            scope = self.context_val.get_candi_set_by_one_param(vals)
            assert self.context_val.idx_repr is not None, print('self.context_val.idx_repr is None')
            expr_ = get_expr_from_str(self.context_val.idx_repr, ph_env)
            assert isinstance(expr_, Expr)
            results = [
                get_imconstraint_result_practical(
                    ExprInContextScope(expr_, scope, True),
                    SelectFuncConstraintFactory.context_scope_exist_func(scope)
                )
            ]
            return results
        
        
        raise NotImplementedError(f"release_both_constraints not implemented {self}")
    
    def can_neg(self) -> bool:
        return True

    def as_neg_constraint(self):
        return self.__class__(self.op_attr_repr, self.context_val, not self.eq)


class TwoContextValAttrEqConstraint(IMConstraint):
    def __init__(self, context_val1:SpecialContextConstVal, context_val2:SpecialContextConstVal, eq:bool) -> None:
        assert context_val1.is_scope()
        assert context_val2.is_scope()
        self.context_val1 = context_val1
        self.context_val2 = context_val2
        self.eq = eq
        
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.context_val1}, {self.context_val2}, {self.eq})'
    
    def as_neg_constraint(self):
        return self.__class__(self.context_val1, self.context_val2, not self.eq)
    def can_neg(self) -> bool:
        return True

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if set(d.keys()) != {'v1', 'v2', 'relation'}:
            return False
        if not SpecialContextConstValFactory.is_valid_str(d['v1']):
            return False
        if not SpecialContextConstValFactory.is_valid_str(d['v2']):
            return False
        return True

    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        eq = d['relation'] == 'eq'
        context_attr_repr1 = d['v1']
        context_val1 = SpecialContextConstValFactory.from_str(context_attr_repr1)
        context_attr_repr2 = d['v2']
        context_val2 = SpecialContextConstValFactory.from_str(context_attr_repr2)
        return cls(context_val1, context_val2, eq)
    
    def release_both_constraints(self, ph_env:PHEnv)->List[IMConstraintResult]:
        val_cs = []
        func_cs = []
        taregt_attr = self.context_val1.val_attr
        assert taregt_attr is not None
        assert self.context_val2.val_attr == taregt_attr
        attrs = self.context_val1._get_all_attr_candis()
        for candi_attr in attrs:
            part_val_cs = []
            part_func_cs = []
            if self.eq:
                attr1_set = {candi_attr}
                attr2_set = {candi_attr}
            else:
                attr1_set = {candi_attr}
                attr2_set = _get_neg_attrs({candi_attr})
            assert isinstance(self.context_val1, SpecialContextScopeVal)
            assert isinstance(self.context_val2, SpecialContextScopeVal)
            scope1 = self.context_val1.get_candi_set_by_one_param(attr1_set)
            scope2 = self.context_val2.get_candi_set_by_one_param(attr2_set)
            assert self.context_val1.idx_repr is not None, print('self.context_val1.idx_repr is None')
            expr1 = get_expr_from_str(self.context_val1.idx_repr, ph_env)
            assert self.context_val2.idx_repr is not None, print('self.context_val2.idx_repr is None')
            expr2 = get_expr_from_str(self.context_val2.idx_repr, ph_env)
            assert isinstance(expr1, Expr)
            assert isinstance(expr2, Expr)
            part_val_cs.append(ExprInContextScope(expr1, scope1, True))
            part_val_cs.append(ExprInContextScope(expr2, scope2, True))
            part_func_cs.append(SelectFuncConstraintFactory.context_scope_exist_func(scope1))
            part_func_cs.append(SelectFuncConstraintFactory.context_scope_exist_func(scope2))
            val_c = CombinedAndConstraint(part_val_cs)
            func_c = SelectFuncConstraintFactoryAnd.generate_a_combined_func_from_SelectFuncConstraints(part_func_cs)
            val_cs.append(val_c)
            func_cs.append(func_c)
        val_c = CombinedOrConstraint(val_cs)
        func_c = SelectFuncConstraintFactoryOr.generate_a_combined_func_from_SelectFuncConstraints(func_cs)
        results = [
            get_imconstraint_result_practical(
                val_constraint=val_c,
                func_constraint=func_c
            )
        ]
        return results

    
class ValAttrEqConstConstraint(IMConstraint):
    def __init__(self, 
                 required_attrs:set[AttrConst], 
                 context_val:SpecialContextConstVal, 
                 eq:bool,
                    full_attrs:set[AttrConst]
                 ) -> None:
        self.required_attrs = required_attrs
        assert context_val.is_scope()
        self.context_val = context_val
        self.eq = eq
        self.full_attrs = full_attrs


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.required_attrs}, {self.context_val}, {self.eq})'

    def as_neg_constraint(self):
        return self.__class__(self.required_attrs, self.context_val, not self.eq, self.full_attrs)

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if ValAttrEqConstConstraint._is_valid_d_p2(d):
            return True
        return False

    @staticmethod
    def _is_valid_d_p2(d:dict)->bool:
        if {'v1', 'v2', 'relation'}.issubset(d.keys()):
            if SpecialContextConstValFactory.is_valid_str(d['v1']) :
                if isinstance(d['v2'], list):
                    if all([_is_valid_val_attr_from_str(x) for x in d['v2']]):
                        if d['relation'] == 'in':
                            return True
                else:
                    if _is_valid_val_attr_from_str(d['v2']):
                        if d['relation'] == 'eq':
                            return True
        return False

    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        if cls._is_valid_d_p2(d):
            eq = True
            context_attr_repr = d['v1']
            context_val = SpecialContextConstValFactory.from_str(context_attr_repr)
            if isinstance(d['v2'], list):
                required_attrs = {_get_val_attr_from_str(x) for x in d['v2']}
            else:
                required_attrs = {_get_val_attr_from_str(d['v2'])}
            if d['relation'] == 'in':
                assert isinstance(d['v2'], list)
                raw_full_attrs =d.get('full_attrs', d['v2'])
            else:
                assert isinstance(d['v2'], str)
                raw_full_attrs = [d['v2']]
            full_attrs = {_get_val_attr_from_str(x) for x in raw_full_attrs}
            return cls(required_attrs, context_val, eq, full_attrs)
        raise ValueError(f'Invalid dict: {d}')

        
    def release_both_constraints(self, ph_env:PHEnv)->List[IMConstraintResult]:
        if self.eq:
            target_attrs = self.required_attrs
        else:
            target_attrs = self._get_neg_attrs()
        assert isinstance(self.context_val, SpecialContextScopeVal)
        scope = self.context_val.get_candi_set_by_one_param(target_attrs)
        assert self.context_val.idx_repr is not None, print('self.context_val.idx_repr is None')
        expr_ = get_expr_from_str(self.context_val.idx_repr, ph_env)
        assert isinstance(expr_, Expr)
        results = [
            get_imconstraint_result_practical(
                val_constraint=ExprInContextScope(expr_, scope, True),
                func_constraint=SelectFuncConstraintFactory.context_scope_exist_func(scope)
            )
        ]
        return results

    def can_neg(self) -> bool:
        neg_attrs = self.full_attrs - self.required_attrs
        if len(neg_attrs) > 0:
            return True
        return False
    
    def _get_neg_attrs(self):
        assert 0
        return self.full_attrs - self.required_attrs


def _get_neg_attrs(target_attrs:set[AttrConst])->Union[set[str], set[ElemSecAttr], set[DataSegAttr], set[globalValMut]]:
    target_attr_asmple = list(target_attrs)[0]
    if target_attr_asmple in val_type_strs:
        return val_type_strs - target_attrs  # type: ignore
    if target_attr_asmple in ElemSecAttr:
        return set(iter(ElemSecAttr)) -target_attrs  # type: ignore
    if target_attr_asmple in DataSegAttr:
        return set(iter(DataSegAttr)) -target_attrs # type: ignore
    if target_attr_asmple in globalValMut:
        return set(iter(globalValMut)) - target_attrs  # type: ignore
    raise ValueError(f'Invalid target_attr: target_attrs')


def _get_val_attr_from_str(s:str)->AttrConst:
    if s in val_type_strs:
        return s
    s = s.lower()
    if s  == 'var':
        return globalValMut.Mut
    if s == 'mut':
        return globalValMut.Mut
    if s == 'const':
        return globalValMut.Const
    if ElemSecAttr.is_valid_str(s):
        return ElemSecAttr.from_str(s)
    if DataSegAttr.is_valid_str(s):
        return DataSegAttr.from_str(s)
    raise NotImplementedError(f'invalid AttrConst str: {s}')

def _is_valid_val_attr_from_str(s:str)->bool:
    try:
        _get_val_attr_from_str(s)
        return True
    except:
        return False
