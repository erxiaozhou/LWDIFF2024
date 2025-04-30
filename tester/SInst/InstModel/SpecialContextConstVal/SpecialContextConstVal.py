from typing import Any, List, Optional, Tuple, Union

from SInst.InstModel.Exceptions import RequireContextException
from WasmInfoCfg import ContextSection2One, ContextValAttr
from WasmInfoCfg import ContextOne2Section
from ..ContextScopeVal import paramSpecialIdxsScope, specialIdxsType
from WasmInfoCfg import globalValMut
from WasmInfoCfg import DataSegAttr
from WasmInfoCfg import ElemSecAttr
from WasmInfoCfg import val_type_strs
from ..SymbolValue import SymbolValue
from z3 import BitVec, And, Or
from ..PHEnv import PHEnv
from extract_block_mutator.Context import Context
from .util import OneContextValAttr
from .util import one_def_attr2size_val, sec_attr2size_val
from .util import get_sec_size_concrete_val


def get_expr_from_str(expr_repr:str, ph_env:PHEnv):
    from ..Expr.tool import get_expr_from_str as _get_expr_from_str
    return _get_expr_from_str(expr_repr, ph_env)



def context_val_has_parent_size(context_val_type:ContextValAttr)->bool:
    return context_val_type in ContextOne2Section



class SpecialContextConstVal(SymbolValue):
    def __init__(self, 
                 context_val_type:ContextValAttr, 
                 idx_repr:Optional[str]=None,
                 val_attr:Optional[OneContextValAttr]=None
                 ) -> None:
        self.context_val_type = context_val_type
        self.idx_repr = idx_repr
        self.val_attr = val_attr
    

    def has_parent_size(self):
        return context_val_has_parent_size(self.context_val_type)

    
    def is_size(self):
        return self.val_attr == OneContextValAttr.size
    
    def is_scope(self):
        return sccv_is_scope(self.val_attr, self.context_val_type)
    
    def is_one_val(self):
        if self.val_attr == OneContextValAttr.size:
            return True
        if self.val_attr == OneContextValAttr.max:
            return True
        return False
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.context_val_type}, {self.idx_repr}, {self.val_attr})'

    def __hash__(self) -> int:
        return hash((self.context_val_type, self.idx_repr))

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, SpecialContextConstVal)
        return self.context_val_type == __value.context_val_type \
            and self.idx_repr == __value.idx_repr

def sccv_is_scope(val_attr:Optional[OneContextValAttr], context_val_type:ContextValAttr)->bool:
    if (val_attr is not None) and val_attr.can_get_scope():
        return True
    if context_val_type == ContextValAttr.OneFuncRef:
        return True
    if context_val_type == ContextValAttr.FuncRefs:
        return True
    return False


class SpecialContextOneVal(SpecialContextConstVal):
    def __init__(self, 
                 context_val_type:ContextValAttr, 
                 idx_repr:Optional[str]=None,
                 val_attr:Optional[OneContextValAttr]=None
                 ) -> None:
        super().__init__(context_val_type, idx_repr, val_attr)
        assert self.is_one_val()
        assert not self.is_scope()
        
    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> Tuple[Any, List]:
        raise NotImplementedError(f'get_symbol_and_constraints not implemented for {self}')


    def get_size_concrete_val(self, context:Context):
        raise NotImplementedError(f'get_size_concrete_val not implemented for {self}')


class SpecialContextOneDef(SpecialContextConstVal): pass

class SpecialContextSizeVal(SpecialContextConstVal):
    def __init__(self, context_val_type: ContextValAttr, idx_repr: Optional[str] = None, val_attr: Optional[OneContextValAttr] = None) -> None:
        assert val_attr == OneContextValAttr.size or val_attr == OneContextValAttr.max
        super().__init__(context_val_type, idx_repr, val_attr)

class SpecialContextOneDefSize(SpecialContextOneDef, SpecialContextSizeVal):
    
        
    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> Tuple[Any, List]:
        if context is None:
            raise RequireContextException('The constraint requires a context')
        assert ph_env is not None
        return self._get_symbol_for_one_def_length(context=context, ph_env=ph_env)


    def _get_symbol_for_one_def_length(self, context: Context, ph_env: PHEnv) -> Tuple[Any, List]:
        assert( self.context_val_type, self.val_attr) in one_def_attr2size_val
        assert self.idx_repr is not None
        assert self.val_attr == OneContextValAttr.size or self.val_attr == OneContextValAttr.max
        symbol = BitVec(f'inter_{self.idx_repr}', 32)
        idx_expr = get_expr_from_str(self.idx_repr, ph_env)
        idx_symbol_expr, inner_cs = idx_expr.get_symbol_and_constraints(context=context, ph_env=ph_env)
        each_idx_exprs = []
        concrete_parent_size = get_parent_size_val(self).get_size_concrete_val(context)

        idx_ge0 = symbol >= 0
        for possible_idx in range(concrete_parent_size):
            idx_eq_c = idx_symbol_expr == possible_idx
            if idx_eq_c is not False:
                cur_val_ = SpecialContextOneDefSize(
                    self.context_val_type,
                    str(possible_idx),
                    OneContextValAttr.size
                )
                concrete_cur_val = cur_val_.get_size_concrete_val(context)
                eq_length_c = symbol == concrete_cur_val
                each_idx_exprs.append(eq_length_c)
        idx_c = Or(each_idx_exprs)
        return symbol, inner_cs + [idx_ge0, idx_c]

    def get_size_concrete_val(self, context:Context):
        if (self.context_val_type, self.val_attr) in one_def_attr2size_val:
            assert self.val_attr is not None
            assert self.idx_repr is not None
            cval =one_def_attr2size_val[(self.context_val_type, self.val_attr)].get_concrete_value(context=context, idx=int(self.idx_repr))
            return cval
        raise NotImplementedError(f'get_concrete_value not implemented for {self}')
    

class SpecialContextOneSec(SpecialContextOneVal): pass
class SpecialContextOneSecSize(SpecialContextOneSec, SpecialContextSizeVal):
    
    def __init__(self, context_val_type: ContextValAttr, idx_repr: Optional[str] = None, val_attr: Optional[OneContextValAttr] = None) -> None:
        assert val_attr == OneContextValAttr.size
        super().__init__(context_val_type, idx_repr, val_attr)
    
    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> Tuple[Any, List]:
        assert self.val_attr == OneContextValAttr.size
        if context is None:
            raise RequireContextException('The constraint requires a context')
        val = self.get_size_concrete_val(context)
        return val, []
        

    def get_size_concrete_val(self, context:Context):
        assert self.val_attr is OneContextValAttr.size
        return get_sec_size_concrete_val(self.context_val_type, context)


def get_parent_size_val(val:SpecialContextConstVal):
    context_val_type = val.context_val_type
    assert context_val_type in ContextOne2Section
    new_context_val_type = ContextOne2Section[context_val_type]
    idx_repr = None
    val_attr = OneContextValAttr.size
    return SpecialContextOneSecSize(new_context_val_type, idx_repr, val_attr)

def get_one_def0_val(val:SpecialContextOneSec):
    context_val_type = val.context_val_type
    assert context_val_type in ContextSection2One
    new_context_val_type = ContextSection2One[context_val_type]
    idx_repr = '0'
    val_attr = None
    return SpecialContextOneDef(new_context_val_type, idx_repr, val_attr)
    
class SpecialContextScopeVal(SpecialContextConstVal):
        
    def __init__(self, 
                 context_val_type:ContextValAttr, 
                 idx_repr:Optional[str]=None,
                 val_attr:Optional[OneContextValAttr]=None
                 ) -> None:
        super().__init__(context_val_type, idx_repr, val_attr)
    
    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> Tuple[Any, List]:
        raise Exception('There should be no case that the val can get scope')
    

    def get_candi_set_by_one_param(self, vals:Optional[Union[set, int]]=None):
        assert vals is None or  isinstance(vals, (set, int))
        assert self.val_attr is not None or self.context_val_type == ContextValAttr.OneFuncRef or self.context_val_type == ContextValAttr.FuncRefs
        return get_candi_set_core(
            context_val_type=self.context_val_type,
            val_attr=self.val_attr,
            attribute=vals
        )

    def _get_all_attr_candis(self):
        if self.val_attr is None:
            raise ValueError(f'val_attr is None')
        
        val_type_mappings = {
            ContextValAttr.OneLocal: set(val_type_strs),
            ContextValAttr.OneGlobal: set(val_type_strs),
            ContextValAttr.OneElemSeg: {'funcref', 'externref'},
            ContextValAttr.OneTable: {'funcref', 'externref'},
        }

        other_attr_mappings = {
            OneContextValAttr.data_seg_attr: set(DataSegAttr),
            OneContextValAttr.elem_seg_attr: set(ElemSecAttr),
            OneContextValAttr.mutable: set(globalValMut),
        }

        if self.val_attr == OneContextValAttr.val_type:
            if self.context_val_type in val_type_mappings:
                return val_type_mappings[self.context_val_type]
            else:
                raise ValueError(f'get_all_attr_candis not implemented for {self}: {self.context_val_type}')

        if self.val_attr in other_attr_mappings:
            return other_attr_mappings[self.val_attr]

        raise ValueError(f'val_attr is {self.val_attr}, which is not supported')


def get_candi_set_core(
    context_val_type: ContextValAttr,
    val_attr: OneContextValAttr,
    *,
    attribute:Optional[Any] = None,
    **kwds
) -> paramSpecialIdxsScope:
    if val_attr == OneContextValAttr.size:
        assert attribute is not None
        if context_val_type == ContextValAttr.OneTable:
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.OneTableSize,
                min_length=attribute
            )
        if context_val_type == ContextValAttr.OneElemSeg:
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.OneElemSize,
                min_length=attribute
            )
        if context_val_type == ContextValAttr.OneDataSeg:
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.OneDataSize,
                min_length=attribute
            )
    if context_val_type == ContextValAttr.OneLocal:
        assert attribute is not None
        assert val_attr == OneContextValAttr.val_type
        return paramSpecialIdxsScope(
            special_idxs_type=specialIdxsType.LocalWithAttr,
            local_types=attribute
        )
    if context_val_type == ContextValAttr.OneGlobal:
        if val_attr == OneContextValAttr.val_type:
            assert attribute is not None
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.GlobalWithType,
                global_types=attribute
            )
    if context_val_type == ContextValAttr.OneGlobal:
        if val_attr == OneContextValAttr.mutable:
            assert attribute is not None
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.GlobalWithMut,
                global_muts=attribute
            )
    if context_val_type == ContextValAttr.OneTable:
        if val_attr == OneContextValAttr.val_type:
            assert attribute is not None
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.TableWithAttr,
                table_types=attribute
            )
    if context_val_type == ContextValAttr.OneElemSeg:
        if val_attr == OneContextValAttr.elem_seg_attr:
            assert attribute is not None
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.ElemWithAttr,
                elem_attrs=attribute
            )
    if context_val_type == ContextValAttr.OneElemSeg:
        if val_attr == OneContextValAttr.val_type:
            assert attribute is not None
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.ElemWithRefType,
                elem_seg_ref_type=attribute
            )
    if context_val_type == ContextValAttr.OneDataSeg:
        if val_attr == OneContextValAttr.data_seg_attr:
            assert attribute is not None
            return paramSpecialIdxsScope(
                special_idxs_type=specialIdxsType.DataWithAttr,
                data_active=attribute
            )
    if context_val_type == ContextValAttr.OneFuncRef\
        or context_val_type == ContextValAttr.FuncRefs:
        return paramSpecialIdxsScope(
            special_idxs_type=specialIdxsType.RefedFuncIdx
        )
    raise NotImplementedError(f'get_candi_set not implemented for context_val_type: {context_val_type}, val_attr: {val_attr}')
