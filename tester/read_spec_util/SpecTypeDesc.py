import traceback
from typing import Callable, List, Optional
from extract_block_mutator.Context import Context
from extract_block_mutator.InstUtil.Inst import Inst
from extract_block_mutator.InstUtil.SpecialImm import UnconstrainedGlobalIdx
from extract_block_mutator.funcType import funcType
from extract_block_mutator.funcTypeFactory import funcTypeFactory
from WasmInfoCfg import naive_types


class SpecTypeRepr:
    def __init__(self, type_repr):
        self._type_repr = type_repr

    @property
    def type_repr(self):
        return self._type_repr

    @type_repr.setter
    def type_repr(self, *args, **kwds):
        raise Exception('Cannot set type_repr')

    def _determined_by_type_repr(self) -> bool:
        raise NotImplementedError('_determined_by_type_repr')

    def _related_to_context(self) -> bool:
        raise NotImplementedError('_related_to_context')

    def get_concrete_type(self, inst: Optional[Inst], context_info: Optional[Context] = None, cur_params: Optional[List[str]] = None) -> str:
        raise NotImplementedError(f'{self}: get_concrete_type')

    def get_concrete_type_func(self):
        raise NotImplementedError(f'{self}: get_concrete_type_func')

    def __eq__(self, __value) -> bool:
        assert isinstance(__value, SpecTypeRepr)
        return self.type_repr == __value.type_repr

    def __hash__(self) -> int:
        return hash(self.type_repr)


class NaiveSpecTypeRepr(SpecTypeRepr):
    def _determined_by_type_repr(self) -> bool:
        return True

    def _related_to_context(self) -> bool:
        return False

    def get_concrete_type(self, inst: Optional[Inst], context_info: Optional[Context] = None, cur_params: Optional[List[str]] = None) -> str:
        # print('P6 : ', self.type_repr)
        # if cur_params is None:
        #     return self.type_repr
        # else:
        return self.type_repr

    def get_concrete_type_func(self):
        return self.get_concrete_type


class DirectImmSpecTypeRepr(SpecTypeRepr):
    def _determined_by_type_repr(self) -> bool:
        # assert 0
        return False

    def _related_to_context(self) -> bool:
        return False

    def get_concrete_type(self, inst: Inst, context_info: Optional[Context] = None, cur_params: Optional[List[str]] = None) -> str:
        result = inst.get_imm_by_ph(self.type_repr)
        if isinstance(result, list):
            assert len(result) == 1
            return result[0]
        else:
            return result

    def get_concrete_type_func(self):
        return self.get_concrete_type
        # !  return self.get_concrete_type ，



class GlobalTypeRepr(SpecTypeRepr):
    @staticmethod
    def _is_expected_repr(type_repr: str) -> bool:
        type_repr = type_repr.lower()
        # use fome features to identify whether it is a global type repr
        if '.type' in type_repr and 'globals' in type_repr:
            if 'global_idx' in type_repr or 'imm_0' in type_repr:
                return True
        return False

    def _determined_by_type_repr(self) -> bool:
        return False

    def _related_to_context(self) -> bool:
        return True

    def get_concrete_type_func(self):
        return self.get_concrete_type

    def get_concrete_type(self,
                          inst: Inst,
                          context_info: Optional[Context] = None,
                          cur_params: Optional[List[str]] = None) -> Optional[str]:
        if isinstance(inst.imm_part, UnconstrainedGlobalIdx):
            return inst.imm_part.type_
        # if inst.imm_part
        if context_info is None:
            return None
        inferred_idx =inst.get_imm_by_ph(self.type_repr)
        if inferred_idx >= len(context_info.global_val_types):
            return None
            raise Exception(f'Required global idx: {inferred_idx};; \n {len(context_info.global_val_types)};;\nglobal_types: {context_info.global_val_types}')
        return context_info.global_val_types[inferred_idx]



class LocalTypeRepr(SpecTypeRepr):
    @staticmethod
    def _is_expected_repr(type_repr: str) -> bool:
        type_repr = type_repr.lower()
        # use fome features to identify whether it is a global type repr
        if '.type' in type_repr and 'locals' in type_repr:
            if 'local_idx' in type_repr or 'imm_0' in type_repr:
                return True
        return False

    def _determined_by_type_repr(self) -> bool:
        return False

    def _related_to_context(self) -> bool:
        return True

    def get_concrete_type_func(self):
        return self.get_concrete_type

    def get_concrete_type(self,
                          inst: Inst,
                          context_info: Optional[Context] = None,
                          cur_params: Optional[List[str]] = None) -> Optional[str]:
        if context_info is None:
            return None
        inferred_idx =inst.get_imm_by_ph(self.type_repr)
        if inferred_idx >= len(context_info.local_types):
            return None
            raise Exception(f'Required local idx: {inferred_idx};; \n {len(context_info.local_types)};;\nlocal_types: {context_info.local_types}')
        return context_info.local_types[inferred_idx]


class TableTypeRepr(SpecTypeRepr):
    @staticmethod
    def _is_expected_repr(type_repr: str) -> bool:
        type_repr = type_repr.lower()
        # use fome features to identify whether it is a global type repr
        if '.type' in type_repr and 'tables' in type_repr:
            if 'table_idx' in type_repr or 'imm_0' in type_repr:
                return True
        return False

    def _determined_by_type_repr(self) -> bool:
        return False

    def _related_to_context(self) -> bool:
        return True

    def get_concrete_type_func(self):
        return self.get_concrete_type

    def get_concrete_type(self,
                          inst: Inst,
                          context_info: Optional[Context] = None,
                          cur_params: Optional[List[str]] = None) -> Optional[str]:
        if context_info is None:
            return None
        idx_text = _identify_idx_in_bracket(self.type_repr)
        if idx_text is None:
            raise Exception('Cannot identify table idx. The original type_repr is: ', self.type_repr)
        if idx_text == 'table_idx' or idx_text == 'tableidx':
            idx_text = 'imm_0'
        # else:
        inferred_idx =inst.get_imm_by_ph(idx_text)
        if inferred_idx >= len(context_info.table_types):
            return None
            raise Exception(f'Required table idx: {inferred_idx};; \n {len(context_info.table_types)};;\ntable_types: {context_info.table_types}')
        return context_info.table_types[inferred_idx]


def _identify_idx_in_bracket(s: str) -> Optional[str]:
    if '[' in s and ']' in s:
        return s[s.index('[')+1:s.index(']')]
    return None

def _init_naive_types():
    _naive_ones = {}
    for type_repr in naive_types:
        _naive_ones[type_repr] = NaiveSpecTypeRepr(type_repr)
    return _naive_ones


def _init_direct_imm_types():
    _direct_imm_ones = {}
    prepare_range = range(5)
    for i in prepare_range:
        ph_name = f'imm_{i}'
        _direct_imm_ones[ph_name] = DirectImmSpecTypeRepr(ph_name)
    return _direct_imm_ones


class SpecTypeReprF:
    _naive_ones = _init_naive_types()
    _direct_imm_ones = _init_direct_imm_types()

    @staticmethod
    def generate_spec_type_repr(type_repr: str) -> SpecTypeRepr:
        if type_repr in naive_types:
            return SpecTypeReprF._naive_ones[type_repr]
        if type_repr.startswith('imm_'):
            if type_repr in SpecTypeReprF._direct_imm_ones:
                return SpecTypeReprF._direct_imm_ones[type_repr]
            else:
                return DirectImmSpecTypeRepr(type_repr)
        if GlobalTypeRepr._is_expected_repr(type_repr):
            return GlobalTypeRepr(type_repr)
        if LocalTypeRepr._is_expected_repr(type_repr):
            return LocalTypeRepr(type_repr)
        if TableTypeRepr._is_expected_repr(type_repr):
            return TableTypeRepr(type_repr)
        raise NotImplementedError(f'generate_spec_type_repr: {type_repr}')


class OneFuncTypeDesc:
    def __init__(self, param: List[SpecTypeRepr], result: List[SpecTypeRepr]):
        self.param = param
        self.result = result

    @property
    def return_num(self) -> int:
        # print('P8 : ', len(self.result), self.result)
        return len(self.result)

    @property
    def related_to_context(self) -> bool:
        for t in self.param:
            if t._related_to_context():
                return True
        for t in self.result:
            if t._related_to_context():
                return True
        return False

    @property
    def determined_by_type_repr(self) -> bool:
        for t in self.param:
            if not t._determined_by_type_repr():
                return False
        for t in self.result:
            if not t._determined_by_type_repr():
                return False
        return True

    def get_concrete_type(self, inst: Optional[Inst]=None, context: Optional[Context] = None, cur_params: Optional[List[str]] = None) -> funcType:
        param = [t.get_concrete_type(inst, context, cur_params) for t in self.param]
        result = [t.get_concrete_type(inst, context, cur_params) for t in self.result]
        return funcTypeFactory.generate_one_func_type_default(param, result)

    def get_concrete_type_func(self) -> Callable[[Inst, Optional[Context], Optional[List[str]]], Optional[funcType]]:
        def fun_1(inst: Inst, context: Optional[Context] = None, cur_params: Optional[List[str]] = None) -> Optional[funcType]:
            params = [t.get_concrete_type(inst, context, cur_params) for t in self.param]
            if any([x is None for x in params]):
                return None
            results = [t.get_concrete_type(inst, context, cur_params) for t in self.result]
            if any([x is None for x in results]):
                return None
            func_type = funcTypeFactory.generate_one_func_type_default(params, results)
            if cur_params is None:
                return func_type
            else:
                mock_ty = funcTypeFactory.generate_one_func_type_default([], cur_params)
                result = func_type
                try:
                    # print('P7 : xxxxxxxxxxxxxxxxxx')
                    mock_ty + func_type
                except Exception as e:
                    result = None
                return result
            # return funcTypeFactory.generate_one_func_type_default(params, results)
        return fun_1
        raise NotImplementedError('get_concrete_type_func')

    @classmethod
    def from_dict(cls, d: dict) -> 'OneFuncTypeDesc':
        param = [SpecTypeReprF.generate_spec_type_repr(t) for t in d['param']]
        result = [SpecTypeReprF.generate_spec_type_repr(t) for t in d['result']]
        return cls(param, result)

    def __eq__(self, __value) -> bool:
        assert isinstance(__value, OneFuncTypeDesc)
        return self.param == __value.param and self.result == __value.result

    def __hash__(self) -> int:
        return hash((tuple(self.param), tuple(self.result)))


class OneInstFuncTypeDesc:
    def __init__(self, func_type_descs: List[OneFuncTypeDesc]):
        self.func_type_descs = func_type_descs

    def determined_result_num(self) -> Optional[int]:
        nums = [x.return_num for x in self.func_type_descs]
        unique_elems = set(nums)
        if len(unique_elems) == 1:
            # print('XXX nums[0]', nums[0])
            return nums[0]
        return None
        

    def is_single_type(self) -> bool:
        return len(self.func_type_descs) == 1

    @property
    def related_to_context(self) -> bool:
        for _desc in self.func_type_descs:
            if _desc.related_to_context:
                return True
        return False

    @property
    def determined_by_type_repr(self) -> bool:
        for _desc in self.func_type_descs:
            if not _desc.determined_by_type_repr:
                return False
        return True

    def get_inst_type(self, inst: Optional[Inst]=None, context: Optional[Context] = None, cur_params: Optional[List[str]] = None)->List[funcType]:
        return [x.get_concrete_type(inst, context, cur_params) for x in self.func_type_descs]


    def get_inst_type_func(self) -> Callable[[Inst, Optional[Context], Optional[List[str]]], Optional[funcType]]:
        # assert len(self.func_type_descs) == 1
        if len(self.func_type_descs) > 1:
            return _wrap_to_return_not_None([x.get_concrete_type_func() for x in self.func_type_descs])
            raise NotImplementedError('get_inst_type_func')
        else:
            func_type_desc = self.func_type_descs[0]
            return func_type_desc.get_concrete_type_func()

def _wrap_to_return_not_None(funcs: List[Callable[[Inst, Optional[Context], Optional[List[str]]], Optional[funcType]]]) -> Callable[[Inst, Optional[Context], Optional[List[str]]], Optional[funcType]]:
    def _wrap(inst: Inst, context: Optional[Context] = None, cur_params: Optional[List[str]] = None) -> Optional[funcType]:
        for f in funcs:
            result = f(inst, context, cur_params)
            # print('P5 : ', result)
            if result is not None:
                return result
        return None
    return _wrap


def get_spec_type_desc_practical(d:dict)->Optional[OneFuncTypeDesc]:
    result = None
    try:
        result = OneFuncTypeDesc.from_dict(d)
    except Exception as e:
        print(traceback.format_exc())
        print('------------------------')
    return result


def desc_one_inst_full_type_part_practical(full_type_part: list[dict])->Optional[OneInstFuncTypeDesc]:
    result = []
    for d in full_type_part:
        possible_one = get_spec_type_desc_practical(d)
        result.append(possible_one)
        # if possible_one is not None:
        #     result.append(possible_one)
        # else:
        #     return None
    if any([x is None for x in result]):
        return None 
    one_inst_func_type_desc = OneInstFuncTypeDesc(result)
    return one_inst_func_type_desc
