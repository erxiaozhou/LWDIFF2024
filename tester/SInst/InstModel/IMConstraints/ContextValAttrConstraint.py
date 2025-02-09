from random import choice
from typing import List, Tuple, Union

from WasmInfoCfg import AttrConst, globalValMut
from WasmInfoCfg import ElemSecAttr
from WasmInfoCfg import DataSegAttr
from ..Expr import Expr
from ..Expr import get_expr_from_str
from ..PHEnv import PHEnv
from ..PlaceHolder import OperandPH
from ..ScopeValConstraint import ExprInContextScope
from ..SelectFuncConstraint import SelectFuncConstraintFactoryAnd, SelectFuncConstraintFactoryOr
from .IMConstraintResult import IMConstraintResult
from ..SelectFuncConstraintFactory import SelectFuncConstraintFactory
from ..specialContextConstVal import OneContextValAttr, specialContextConstVal
from ..CombinedConstraint import CombinedAndConstraint, CombinedOrConstraint
from .IMConstraint import IMConstraint
from .ExistIMConstraint import ExistIMConstraint
from WasmInfoCfg import val_type_strs

class OpContextValAttrConstraint(IMConstraint):
    def __init__(self, op_attr_repr:str, context_val:specialContextConstVal, eq:bool) -> None:
        self.op_attr_repr = op_attr_repr
        assert context_val.can_get_scope()
        self.context_val = context_val
        self.eq = eq


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.op_attr_repr}, {self.context_val}, {self.eq})'

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        # TODO currently, just enum all possible cases
        if set(d.keys()) != {'v1', 'v2', 'relation'}:
            return False
        if not (d['v1'].startswith('op_') and d['v1'].endswith('.type')):
            return False
        if not specialContextConstVal.is_valid_str(d['v2']):
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
        context_val = specialContextConstVal.from_str(context_attr_repr)
        return cls(op_attr_repr, context_val, eq)

    def _get_exist_im_cs(self, ph_env:PHEnv, *args, **kwds)->List[ExistIMConstraint]:
        raise NotImplementedError
        
    def release_both_constraints(self, ph_env:PHEnv)->List[IMConstraintResult]:
        if '.type' in self.op_attr_repr:
            op_name = self.op_attr_repr.replace('.type', '')
            # print('RTHFHFSFVXCX ph_env', ph_env)
            op_ph = ph_env.get_ph(op_name)
            assert isinstance(op_ph, OperandPH)
            op_type = op_ph.ty
            assert op_type in val_type_strs
            assert self.context_val.val_attr == OneContextValAttr.val_type  # 
            # scope = paramSpecialIdxsScope
            assert isinstance(op_type, str)
            if self.eq:
                vals = {op_type}
            else:
                vals = val_type_strs - {op_type}
            scope = self.context_val.get_candi_set_by_one_param(vals)

            expr_ = get_expr_from_str(self.context_val.idx_repr, ph_env)
            assert isinstance(expr_, Expr)
            results = [
                IMConstraintResult(
                    ExprInContextScope(expr_, scope, True),
                    SelectFuncConstraintFactory.context_scope_exist_func(scope)
                )
            ]
            return results
        
        
        raise NotImplementedError(f"release_both_constraints not implemented {self}")
    
    def can_neg(self) -> bool:
        return True

    def as_neg_constraint(self):
        # raise NotImplementedError
        return self.__class__(self.op_attr_repr, self.context_val, not self.eq)


class TwoContextValAttrEqConstraint(IMConstraint):
    def __init__(self, context_val1:specialContextConstVal, context_val2:specialContextConstVal, eq:bool) -> None:
        assert context_val1.can_get_scope()
        assert context_val2.can_get_scope()
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
        # TODO currently, just enum all possible cases
        if set(d.keys()) != {'v1', 'v2', 'relation'}:
            return False
        if not specialContextConstVal.is_valid_str(d['v1']):
            return False
        if not specialContextConstVal.is_valid_str(d['v2']):
            return False
        return True

    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        eq = d['relation'] == 'eq'
        context_attr_repr1 = d['v1']
        context_val1 = specialContextConstVal.from_str(context_attr_repr1)
        context_attr_repr2 = d['v2']
        context_val2 = specialContextConstVal.from_str(context_attr_repr2)
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
            scope1 = self.context_val1.get_candi_set_by_one_param(attr1_set)
            scope2 = self.context_val2.get_candi_set_by_one_param(attr2_set)
            expr1 = get_expr_from_str(self.context_val1.idx_repr, ph_env)
            expr2 = get_expr_from_str(self.context_val2.idx_repr, ph_env)
            assert isinstance(expr1, Expr)
            assert isinstance(expr2, Expr)
            part_val_cs.append(ExprInContextScope(expr1, scope1, True))
            part_val_cs.append(ExprInContextScope(expr2, scope2, True))
            part_func_cs.append(SelectFuncConstraintFactory.context_scope_exist_func(scope1))
            part_func_cs.append(SelectFuncConstraintFactory.context_scope_exist_func(scope2))
            val_c = CombinedAndConstraint(part_val_cs)
            func_c = SelectFuncConstraintFactoryAnd.generate_a_combined_func_from_SelectFuncConstraints(part_func_cs)
            # print('func_c ;;;;;', func_c)
            val_cs.append(val_c)
            func_cs.append(func_c)
        val_c = CombinedOrConstraint(val_cs)
        func_c = SelectFuncConstraintFactoryOr.generate_a_combined_func_from_SelectFuncConstraints(func_cs)
        results = [
            IMConstraintResult(val_c, func_c)
        ]
        return results

    
class ValAttrEqConstConstraint(IMConstraint):
    def __init__(self, 
                 required_attrs:set[AttrConst], 
                 context_val:specialContextConstVal, 
                 eq:bool,
                    full_attrs:set[AttrConst]
                 ) -> None:
        self.required_attrs = required_attrs
        assert context_val.can_get_scope()
        self.context_val = context_val
        self.eq = eq
        self.full_attrs = full_attrs
        # assert 0

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.required_attrs}, {self.context_val}, {self.eq})'

    def as_neg_constraint(self):
        return self.__class__(self.required_attrs, self.context_val, not self.eq, self.full_attrs)

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if ValAttrEqConstConstraint._is_valid_d_p1(d):
            return True
        if ValAttrEqConstConstraint._is_valid_d_p2(d):
            return True
        if ValAttrEqConstConstraint._is_valid_d_p3(d):
            return True
        return False
            
    @staticmethod
    def _is_valid_d_p1(d:dict)->bool:
        # pq
        # TODO currently, just enum all possible cases
        if set(d.keys()) == {'VariableName', 'Value'}:
            try:
                if _is_valid_val_attr_from_str(d['Value']):
                    if specialContextConstVal.is_valid_str(d['VariableName']):
                        return True
            except:
                pass
        return False

    @staticmethod
    def _is_valid_d_p2(d:dict)->bool:
        if set(d.keys()) == {'v1', 'v2', 'relation', 'full_attrs'}:
            if specialContextConstVal.is_valid_str(d['v1']) :
                if isinstance(d['v2'], list):
                    if all([_is_valid_val_attr_from_str(x) for x in d['v2']]):
                        if d['relation'] == 'in':
                            return True
                else:
                    if _is_valid_val_attr_from_str(d['v2']):
                        if d['relation'] == 'eq':
                            return True
                    # elif d['relation'] == 'eq' and len(d['v2']) == 1:
                    #     return True
        return False

    @staticmethod
    def _is_valid_d_p3(d:dict)->bool:
        if set(d.keys()) == {'v1', 'v2', 'relation'}:
            if specialContextConstVal.is_valid_str(d['v1']) :
                # print('xxxx')
                if not isinstance(d['v2'], list):
                    if _is_valid_val_attr_from_str(d['v2']):
                        # print('123')
                        if d['relation'] == 'eq':
                            return True
        return False
    
    @classmethod
    def from_dict(cls, d: dict):
        assert cls.is_valid_dict(d)
        if cls._is_valid_d_p1(d):
            const_attr = _get_val_attr_from_str(d['Value'])
            context_attr_repr = d['VariableName']
            context_val = specialContextConstVal.from_str(context_attr_repr)
            # assert 0
            return cls({const_attr}, context_val, True, _get_full_attrs(const_attr))
        if cls._is_valid_d_p2(d):
            eq = True
            context_attr_repr = d['v1']
            context_val = specialContextConstVal.from_str(context_attr_repr)
            if isinstance(d['v2'], list):
                required_attrs = {_get_val_attr_from_str(x) for x in d['v2']}
            else:
                required_attrs = {_get_val_attr_from_str(d['v2'])}
            full_attrs = {_get_val_attr_from_str(x) for x in d['full_attrs']}
            # required_attrs = {_get_val_attr_from_str(x) for x in d['v2']}
            # print(required_attrs, 'PPPPPPPPPPPPPPPPPPPPPPPPP')
            return cls(required_attrs, context_val, eq, full_attrs)
        if cls._is_valid_d_p3(d):
            eq = d['relation'] == 'eq'
            context_attr_repr = d['v1']
            context_val = specialContextConstVal.from_str(context_attr_repr)
            const_attr =_get_val_attr_from_str(d['v2'])
            return cls({const_attr}, context_val, eq, _get_full_attrs(const_attr))
        raise ValueError(f'Invalid dict: {d}')


    def _get_exist_im_cs(self, ph_env:PHEnv, *args, **kwds)->List[ExistIMConstraint]:
        raise NotImplementedError
        
    def release_both_constraints(self, ph_env:PHEnv)->List[IMConstraintResult]:
        if self.eq:
            target_attrs = self.required_attrs
        else:
            target_attrs = self._get_neg_attrs()

        scope = self.context_val.get_candi_set_by_one_param(target_attrs)
        expr_ = get_expr_from_str(self.context_val.idx_repr, ph_env)
        assert isinstance(expr_, Expr)
        results = [
            IMConstraintResult(
                ExprInContextScope(expr_, scope, True),
                SelectFuncConstraintFactory.context_scope_exist_func(scope)
            )
        ]
        return results

    def can_neg(self) -> bool:
        
        neg_attrs = self.full_attrs - self.required_attrs
        if len(neg_attrs) > 0:
            return True
        return False
    def _get_neg_attrs(self):
        return self.full_attrs - self.required_attrs


def _get_full_attrs(target_attr:AttrConst)->set[AttrConst]:
    if target_attr in ElemSecAttr:
        return set(iter(ElemSecAttr))  # type: ignore
    if target_attr in DataSegAttr:
        return set(iter(DataSegAttr)) # type: ignore
    if target_attr in globalValMut:
        return set(iter(globalValMut))  # type: ignore
    raise NotImplementedError(f'Invalid target_attr: target_attrs')


def _get_neg_attrs(target_attrs:set[AttrConst])->Union[set[str], set[ElemSecAttr], set[DataSegAttr], set[globalValMut]]:
    target_attr_asmple = list(target_attrs)[0]
    # print('OOOOOOOOOOOOOOOOOOOOOO', target_attr_asmple)
    if target_attr_asmple in val_type_strs:
        # raise NotImplementedError
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
    # if s == 'elemattr.passive'
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

def _is_valid_val_attr_from_str(s:str)->bool:
    try:
        _get_val_attr_from_str(s)
        return True
    except:
        return False
