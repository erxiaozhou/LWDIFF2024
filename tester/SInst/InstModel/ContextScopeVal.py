from enum import Enum, auto

from WasmInfoCfg import globalValMut
from WasmInfoCfg import DataSegAttr
from WasmInfoCfg import ElemSecAttr
from extract_block_mutator.get_data_shell import get_data_attr, get_elemseg_attr, get_func_idxs, get_table_attr
from .Exceptions import ContextIsNoneException
from extract_block_mutator.Context import Context
from typing import List, Optional, Tuple, Union, Set

# valid_querys = {}

# class


class specialIdxsType(Enum):
    LocalWithAttr = auto()
    GlobalWithType = auto()
    GlobalWithMut = auto()
    TableWithAttr = auto()
    DataWithAttr = auto()
    ElemWithAttr = auto()
    ElemWithRefType = auto()
    AllFuncIdx = auto()
    RefedFuncIdx = auto()
    # 
    OneTableSize = auto()
    OneElemSize = auto()
    OneDataSize = auto()
    

    def get_concrete_valset_from_context(
        self,
        context: Context,
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
    ) -> Set[int]:
        if context is None:
            raise ContextIsNoneException(f'context is None: {self}')
        if self == specialIdxsType.OneTableSize:
            assert min_length is not None
            candis = set()
            for table_idx, table_data in enumerate(context.defined_table_datas):
                table_min = get_table_attr(table_data, 'min')
                if table_min >= min_length:
                    candis.add(table_idx)
            return candis
        if self == specialIdxsType.OneElemSize:
            assert min_length is not None
            candis = set()
            for elem_idx, elem_data in enumerate(context.elem_sec_datas):
        
                if get_elemseg_attr(elem_data, 'elem_len') >= min_length: # type: ignore
                    candis.add(elem_idx)
            return candis
        if self == specialIdxsType.OneDataSize:
            assert min_length is not None
            candis = set()
            for data_idx, data_data in enumerate(context.data_sec_datas):
                if get_data_attr(data_data, 'data_len') >= min_length:  # type: ignore
                    candis.add(data_idx)
            return candis
        if self == specialIdxsType.LocalWithAttr:
            candis = set()
            assert local_types is not None
            for local_idx, local_type in enumerate(context.local_types):
                if local_type in local_types:
                    candis.add(local_idx)
            return candis
        if self == specialIdxsType.GlobalWithType:
            candis = set()
            assert global_types is not None
            for global_idx, global_type in enumerate(context.global_val_types):
                if global_type in global_types:
                    candis.add(global_idx)
            return candis
        if self == specialIdxsType.GlobalWithMut:
            candis = set()
            assert global_muts is not None
            for global_idx, global_mut in enumerate(context.global_muts):
                if global_mut in global_muts:
                    candis.add(global_idx)
            return candis
        if self == specialIdxsType.TableWithAttr:
            candis = set()
            assert table_types is not None
            for table_idx, table_type in enumerate(context.table_types):
                if table_type in table_types:
                    candis.add(table_idx)
            return candis
        if self == specialIdxsType.DataWithAttr:
            candis = set()
            assert data_active is not None
            for data_idx, data_act in enumerate(context.data_activable):
                if data_act in data_active:
                    candis.add(data_idx)
            return candis
        if self == specialIdxsType.ElemWithAttr:
            assert elem_attrs is not None
            candis = set()
            for elem_idx, elem_attr in enumerate(context.elem_attrs):
                if elem_attr in elem_attrs:
                    candis.add(elem_idx)
            return candis
        if self == specialIdxsType.ElemWithRefType:
            assert elem_seg_ref_type is not None
            candis = set()
            for elem_idx, elem_ref_type in enumerate(context.elem_ref_types):
                if elem_ref_type in elem_seg_ref_type:
                    candis.add(elem_idx)
            return candis
            
        if self == specialIdxsType.AllFuncIdx:
            return set(range(context.func_num))
        if self == specialIdxsType.RefedFuncIdx:
            idxs_ = set()
            for elem_sec in context.elem_sec_datas:
                func_idxs = get_func_idxs(elem_sec)
                idxs_.update(func_idxs)
            return idxs_ 

        raise NotImplementedError(f'self is {self}')


class paramSpecialIdxsScope:
    def __init__(self, special_idxs_type:specialIdxsType, name_repr, *_,  **param_dict):
        self.param = param_dict
        self.special_idxs_type = special_idxs_type
        self.name_repr = name_repr

    def __repr__(self) -> str:
        return f'paramSpecialIdxsScope({self.special_idxs_type}, {self.name_repr}, {self.param})'

    def get_concrete_valset_from_context(
        self,
        context: Context,
    ) -> Set[int]:
        return self.special_idxs_type.get_concrete_valset_from_context(context, **self.param)

    def __eq__(self, other):
        if not isinstance(other, paramSpecialIdxsScope):
            return False
        if self.special_idxs_type != other.special_idxs_type:
            return False
        if self.param != other.param:
            return False
        return True
    # def 
    def __hash__(self):
        # print(hash(frozenset({1,2,3})))
        param = {k:tuple(v) if isinstance(v, set) else v for k, v in self.param.items()}
        param = frozenset(param.items())
        return hash((self.special_idxs_type, param))
