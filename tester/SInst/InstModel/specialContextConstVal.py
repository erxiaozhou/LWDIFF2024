from enum import Enum, auto
from typing import Any, List, Optional, Set, Tuple, Union

from WasmInfoCfg import ContextValAttr
from ..InstModel.PlaceHolder import is_valid_imm_name
from .ContextScopeVal import paramSpecialIdxsScope, specialIdxsType
from WasmInfoCfg import globalValMut
from WasmInfoCfg import DataSegAttr
from WasmInfoCfg import ElemSecAttr
from WasmInfoCfg import val_type_strs
from extract_block_mutator.specialConst import specialContextConst
import re


class OneContextValAttr(Enum):
    size = auto()
    max = auto()
    val_type = auto()
    data_seg_attr = auto()
    elem_seg_attr = auto()
    mutable = auto()


class specialContextConstVal:
    _one_mem_p = re.compile(r'context.mems?\[(\d+)\].length')
    def __init__(self, 
                 context_val_type:ContextValAttr, 
                 idx_repr:Optional[str]=None,
                 val_attr:Optional[OneContextValAttr]=None
                 ) -> None:
        self.context_val_type = context_val_type
        # idxexpe，
        self.idx_repr = idx_repr
        self.val_attr = val_attr

    def __repr__(self) -> str:
        return f'specialContextConstVal({self.context_val_type}, {self.idx_repr}, {self.val_attr})'

    def __hash__(self) -> int:
        return hash((self.context_val_type, self.idx_repr))

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, specialContextConstVal)
        return self.context_val_type == __value.context_val_type and self.idx_repr == __value.idx_repr


    def _get_all_attr_candis(self):
        if self.val_attr is None:
            raise  ValueError(f'val_attr is None')
        if self.val_attr == OneContextValAttr.size:
            raise ValueError(f'val_attr is size')
        if self.val_attr == OneContextValAttr.max:
            raise ValueError(f'val_attr is max')
        if self.val_attr == OneContextValAttr.val_type:
            if self.context_val_type == ContextValAttr.OneLocal:
                return set(val_type_strs)
            if self.context_val_type == ContextValAttr.OneGlobal:
                return set(val_type_strs)
            if self.context_val_type == ContextValAttr.OneElemSeg:
                return {'funcref', 'externref'}
            if self.context_val_type == ContextValAttr.OneTable:
                return {'funcref', 'externref'}
            raise NotImplementedError(f'get_all_attr_candis not implemented for {self}: {self.context_val_type}')
        if self.val_attr == OneContextValAttr.data_seg_attr:
            return set(DataSegAttr)
        if self.val_attr == OneContextValAttr.elem_seg_attr:
            return set(ElemSecAttr)
        if self.val_attr == OneContextValAttr.mutable:
            return set(globalValMut)
        raise NotImplementedError(f'get_all_attr_candis not implemented for {self}')
    @classmethod
    def from_context_val_attr(cls, context_val_attr:ContextValAttr):
        return cls(context_val_attr, None)


    @classmethod
    def from_str(cls, s:str):
        s = s.lower()
        val_attr = _determine_val_attr(s)
        context_val_type = _determine_type(s)
        idx_repr = _determine_idx_repr(s)
        return cls(context_val_type, idx_repr, val_attr)
        # raise NotImplementedError(f'from_str not implemented: {s}')

    @staticmethod
    def is_valid_str(s:str)->bool:
        try:
            specialContextConstVal.from_str(s)
            return True
        except:
            return False
    
    def has_parent_size(self):
        has_ = self.context_val_type in {
            ContextValAttr.OneMem,
            ContextValAttr.OneTable,
            ContextValAttr.OneElemSeg,
            ContextValAttr.OneDataSeg,
            ContextValAttr.OneLocal,
            ContextValAttr.OneGlobal,
            ContextValAttr.OneFunc
        }
        return has_

    def get_parent_size_val(self):
        assert self.has_parent_size()
        # assert 
        if self.context_val_type == ContextValAttr.OneMem:
            new_context_val_type = ContextValAttr.MemSec
        elif self.context_val_type == ContextValAttr.OneTable:
            new_context_val_type = ContextValAttr.TableSec
        elif self.context_val_type == ContextValAttr.OneElemSeg:
            new_context_val_type = ContextValAttr.ElemSec
        elif self.context_val_type == ContextValAttr.OneDataSeg:
            new_context_val_type = ContextValAttr.DataSec
        elif self.context_val_type == ContextValAttr.OneLocal:
            new_context_val_type = ContextValAttr.Locals
        elif self.context_val_type == ContextValAttr.OneGlobal:
            new_context_val_type = ContextValAttr.Globals
        elif self.context_val_type == ContextValAttr.OneFunc:
            new_context_val_type = ContextValAttr.Funcs
        else:
            raise NotImplementedError(f'get_parent_val not implemented for {self}')
        # idx_repr = self.idx_repr
        idx_repr = None
        val_attr = OneContextValAttr.size
        return specialContextConstVal(new_context_val_type, idx_repr, val_attr)


    def is_may_zero_size(self):
        return self.val_attr == OneContextValAttr.size

    def get_zero_idx_val(self):
        assert self.is_may_zero_size()
        if self.context_val_type == ContextValAttr.MemSec:
            new_context_val_type = ContextValAttr.OneMem
        elif self.context_val_type == ContextValAttr.TableSec:
            new_context_val_type = ContextValAttr.OneTable
        elif self.context_val_type == ContextValAttr.ElemSec:
            new_context_val_type = ContextValAttr.OneElemSeg
        elif self.context_val_type == ContextValAttr.DataSec:
            new_context_val_type = ContextValAttr.OneDataSeg
        elif self.context_val_type == ContextValAttr.Locals:
            new_context_val_type = ContextValAttr.OneLocal
        elif self.context_val_type == ContextValAttr.Globals:
            new_context_val_type = ContextValAttr.OneGlobal
        elif self.context_val_type == ContextValAttr.Funcs:
            new_context_val_type = ContextValAttr.OneFunc
        else:
            raise NotImplementedError(f'get_zero_idx_val not implemented for {self}')
        idx_repr = '0'
        val_attr = None
        return specialContextConstVal(new_context_val_type, idx_repr, val_attr)
        



    def can_get_scope(self):
        if self.val_attr in {OneContextValAttr.val_type, 
                             OneContextValAttr.data_seg_attr, 
                             OneContextValAttr.elem_seg_attr,
                             OneContextValAttr.mutable
                        }:
            return True
        if self.context_val_type == ContextValAttr.OneFuncRef:
            return True
        return False

    def get_candi_set_by_one_param(self, vals:Optional[Union[set, int]]=None):
        assert vals is None or  isinstance(vals, (set, int))
        para_d = {
            'name_repr': self.idx_repr,
            'local_types': vals,
            'global_types': vals,
            'global_muts': vals,
            'table_types': vals,
            'data_active': vals,
            'elem_attrs': vals,
            'elem_seg_ref_type': vals,
            'min_length': vals
        }
        # print('||||!!!! para_d', para_d)
        return self._get_candi_set_core(**para_d)

    def _get_candi_set_core(self,
        name_repr,
        *,
        local_types: Optional[Set[str]]=None,
        global_types: Optional[Set[str]]=None,
        global_muts: Optional[Set[globalValMut]]=None,
        table_types: Optional[Set[str]]=None,
        data_active: Optional[Set[DataSegAttr]]=None,
        elem_attrs: Optional[Set[ElemSecAttr]]=None,
        elem_seg_ref_type: Optional[Set[str]]=None,
        min_length:Optional[int]=None,
        **kwds
    )->paramSpecialIdxsScope:
        # ! candisindex
        if self.val_attr == OneContextValAttr.size:
            if self.context_val_type == ContextValAttr.OneTable:
                assert min_length is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.OneTableSize,
                    name_repr=name_repr,
                    min_length = min_length
                )
            if self.context_val_type == ContextValAttr.OneElemSeg:
                assert min_length is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.OneElemSize,
                    name_repr=name_repr,
                    min_length = min_length
                )
            if self.context_val_type == ContextValAttr.OneDataSeg:
                assert min_length is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.OneDataSize,
                    name_repr=name_repr,
                    min_length = min_length
                )
        if self.context_val_type == ContextValAttr.OneLocal:
            assert local_types is not None
            assert self.val_attr == OneContextValAttr.val_type
            return paramSpecialIdxsScope(
                special_idxs_type = specialIdxsType.LocalWithAttr,
                    name_repr=name_repr,
                local_types = local_types
            )
        if self.context_val_type == ContextValAttr.OneGlobal:
            if self.val_attr == OneContextValAttr.val_type:
                assert global_types is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.GlobalWithType,
                    name_repr=name_repr,
                    global_types = global_types
                )
        if self.context_val_type == ContextValAttr.OneGlobal:
            if self.val_attr == OneContextValAttr.mutable:
                assert global_muts is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.GlobalWithMut,
                    name_repr=name_repr,
                    global_muts = global_muts
                )
        if self.context_val_type == ContextValAttr.OneTable:
            if self.val_attr == OneContextValAttr.val_type:
                assert table_types is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.TableWithAttr,
                    name_repr=name_repr,
                    table_types = table_types
                )
        if self.context_val_type == ContextValAttr.OneElemSeg:
            if self.val_attr == OneContextValAttr.elem_seg_attr:
                assert elem_attrs is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.ElemWithAttr,
                    name_repr=name_repr,
                    elem_attrs = elem_attrs
                )
        if self.context_val_type == ContextValAttr.OneElemSeg:
            if self.val_attr == OneContextValAttr.val_type:
                assert elem_seg_ref_type is not None
                return paramSpecialIdxsScope(
                    special_idxs_type = specialIdxsType.ElemWithRefType,
                    name_repr=name_repr,
                    elem_seg_ref_type = elem_seg_ref_type
                )
        if self.context_val_type == ContextValAttr.OneDataSeg:
            if self.val_attr == OneContextValAttr.data_seg_attr:
                assert data_active is not None
                return paramSpecialIdxsScope(
                    name_repr=name_repr,
                    special_idxs_type = specialIdxsType.DataWithAttr,
                    data_active = data_active
                )
        if self.context_val_type == ContextValAttr.OneFuncRef:
            return paramSpecialIdxsScope(
                    name_repr=name_repr,
                special_idxs_type = specialIdxsType.RefedFuncIdx
            )
        raise NotImplementedError(f'get_cnadi_set not implemented for {self}')
        

    def can_generate_val(self):
        if self.val_attr == OneContextValAttr.size:
            return True
        if self.val_attr == OneContextValAttr.max:
            return True
        return False


    def _is_unsolved_length_symbol(self):
        if self.val_attr == OneContextValAttr.size:
            if self.context_val_type in [ContextValAttr.OneMem, ContextValAttr.OneTable, ContextValAttr.OneElemSeg, ContextValAttr.OneDataSeg]:
                assert self.idx_repr is not None
                if is_valid_imm_name(self.idx_repr):
                    return True
        return False


    def get_concrete_value(self, 
                            context,
                            ):
        assert self.val_attr is not None
        if self.val_attr == OneContextValAttr.size:
            if self.context_val_type == ContextValAttr.OneMem:
                assert self.idx_repr is not None
                mem_idx = int(self.idx_repr)
                return specialContextConst.OneMemCurSize.get_concrete_value(context=context, memory_idx=mem_idx)
            elif self.context_val_type == ContextValAttr.Locals:
                return specialContextConst.LocalNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.Globals:
                return specialContextConst.GlobalNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.MemSec:
                return specialContextConst.CurMemNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.Funcs:
                return specialContextConst.FuncNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.TableSec:
                return specialContextConst.TableNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.DataSec:
                return specialContextConst.DataSegNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.ElemSec:
                return specialContextConst.ElemSegNum.get_concrete_value(context=context)
            elif self.context_val_type == ContextValAttr.OneTable:
                assert self.idx_repr is not None
                table_idx = int(self.idx_repr)
                return specialContextConst.OneTableLen.get_concrete_value(context=context, table_idx=table_idx)
            elif self.context_val_type == ContextValAttr.OneElemSeg:
                assert self.idx_repr is not None
                elem_idx = int(self.idx_repr)
                return specialContextConst.OneElemSegLen.get_concrete_value(context=context, elem_idx=elem_idx)
            elif self.context_val_type == ContextValAttr.OneDataSeg:
                assert self.idx_repr is not None
                data_idx = int(self.idx_repr)
                return specialContextConst.OneDataSegLen.get_concrete_value(context=context, data_idx=data_idx)
            raise NotImplementedError(f'get_concrete_value not implemented for {self}')
        elif self.val_attr == OneContextValAttr.max:
            if self.context_val_type == ContextValAttr.OneMem:
                assert self.idx_repr is not None
                mem_idx = int(self.idx_repr)
                return specialContextConst.OneMemMax.get_concrete_value(context=context, memory_idx=mem_idx)
        raise NotImplementedError(f'get_concrete_value not implemented for {self}')


def _determine_val_attr(s:str)->Optional[OneContextValAttr]:
    s = s.lower()
    if s.endswith('.length'):
        return OneContextValAttr.size
    if s.endswith('.max'):
        return OneContextValAttr.max
    if s.endswith('.maximum'):
        return OneContextValAttr.max
        
    if s.endswith('.type'):
        return OneContextValAttr.val_type
    if s.endswith('.mut'):
        return OneContextValAttr.mutable
    if s.endswith(']'):
        return None
    raise NotImplementedError(f'_determine_val_attr not implemented: {s}')

def _determine_type(s:str)->ContextValAttr:
    s = s.strip().lower()
    if s.endswith('.length'):
        s = s[:-7]
    if s.endswith('.max'):
        s = s[:-4]
    if s.endswith('.type'):
        s = s[:-5]
    if s.endswith('.mut'):
        s = s[:-4]
    if s.startswith('c.'):
        s = s.replace('c.', 'context.')
    if s == 'context.locals':
        return ContextValAttr.Locals
    if 'context.locals[' in s:
        return ContextValAttr.OneLocal
    if s == 'context.globals':
        return ContextValAttr.Globals
    if 'context.globals[' in s:
        return ContextValAttr.OneGlobal
    if ('context.mem[' in s) or ('context.mems[' in s):
        return ContextValAttr.OneMem
    if s == 'context.mems' or s == 'context.mem':
        return ContextValAttr.MemSec
    if s == 'context.datas' or s == 'context.data':
        return ContextValAttr.DataSec
    if s == 'context.elems' or s == 'context.elem' or s == 'context.elemsegs' or s == 'context.elements':
        return ContextValAttr.ElemSec
    if 'context.table[' in s or  'context.tables[' in s:
        return ContextValAttr.OneTable
    # if 'context.tables' in s and '[' not in s:
    if s == 'context.funcs' or s == 'context.func':
        return ContextValAttr.Funcs
    if s == 'context.tables' or s == 'context.table':
        return ContextValAttr.TableSec
    if 'context.elem[' in s or 'context.elems[' in s or 'context.elements[' in s or 'context.elemsegs[' in s:
        return ContextValAttr.OneElemSeg
    if 'context.data[' in s or  'context.datas[' in s:
        return ContextValAttr.OneDataSeg
    if 'context.cfuncs[' in s:
        return ContextValAttr.OneFunc
    if 'context.crefs[' in s:
        return ContextValAttr.OneFuncRef
    if 'context.refs[' in s:
        return ContextValAttr.OneFuncRef
    if s == 'context.refs':
        return ContextValAttr.FuncRefs
        
    raise NotImplementedError(f'_determine_type not implemented: {s}')

def _determine_idx_repr(s:str)->Optional[str]:
    if '[' not in s:
        assert ']' not in s
        return None
    else:
        assert s.count('[') == s.count(']') == 1
    lb_idx = s.index('[')
    rb_idx = s.index(']')
    return s[lb_idx+1:rb_idx]
