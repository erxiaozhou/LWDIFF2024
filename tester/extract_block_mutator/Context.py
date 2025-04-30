from typing import List, Optional, Protocol, TYPE_CHECKING
from WasmInfoCfg import globalValMut
from extract_block_mutator.get_data_shell import get_data_attr, get_elemseg_attr, get_global_attr, get_table_attr
from .funcType import funcType
from .funcTypeFactory import funcTypeFactory
from .InfoLoader import InfoLoader


class ContextVariables(InfoLoader):
    _EQ_ATTRIBUTES = [
        'local_types',
        'func_type_idxs',
        'types',
        'cur_func_ty',
        'defined_globals',
        'defined_memory_datas',
        'data_sec_datas',
        'elem_sec_datas',
        'defined_table_datas',
        'import_func_num',
        'import_global_num',
        'import_table_num',
        'import_memory_num'
    ]

    def __init__(self,
                 local_types: List[str],
                 func_type_idxs: List[int],
                 types: List[funcType],
                 cur_func_ty: funcType,
                 defined_globals: list,
                 defined_memory_datas: list,
                 data_sec_datas: list,
                 elem_sec_datas: list,
                 defined_table_datas: list,
                 import_func_num=0,
                 import_global_num=0,
                 import_table_num=0,
                 import_memory_num=0
                 ) -> None:
        self.local_types = local_types
        self._func_type_idxs = func_type_idxs
        self.types = types
        self.cur_func_ty = cur_func_ty
        self.defined_globals: list = defined_globals
        self.defined_memory_datas: list = defined_memory_datas
        self.data_sec_datas: list = data_sec_datas
        self.elem_sec_datas: list = elem_sec_datas
        self.defined_table_datas: list = defined_table_datas
        self._type_check()

        self.import_func_num = import_func_num
        self.import_global_num = import_global_num
        self.import_table_num = import_table_num
        self.import_memory_num = import_memory_num

    @property
    def imports(self):
        raise AttributeError

    @property
    def exports(self):
        raise AttributeError

    @property
    def customs(self):
        raise AttributeError

    @property
    def func_type_idxs(self):
        return self._func_type_idxs

    def copy(self):
        return ContextVariables(
            local_types=self.local_types.copy(),
            func_type_idxs=self.func_type_idxs,
            types=[ty.copy() for ty in self.types],
            cur_func_ty=self.cur_func_ty.copy(),
            defined_globals=self.defined_globals.copy(),
            defined_memory_datas=self.defined_memory_datas.copy(),
            data_sec_datas=self.data_sec_datas.copy(),
            elem_sec_datas=self.elem_sec_datas.copy(),
            defined_table_datas=self.defined_table_datas.copy(),
            import_func_num=self.import_func_num,
            import_global_num=self.import_global_num,
            import_table_num=self.import_table_num,
            import_memory_num=self.import_memory_num
        )

    def _type_check(self):
        for local_type in self.local_types:
            assert isinstance(local_type, str)
        for func_type_id in self.func_type_idxs:
            assert isinstance(func_type_id, int)
        for func_type in self.types:
            assert isinstance(func_type, funcType)
        assert isinstance(self.cur_func_ty, funcType)
        for _val in self.defined_globals:
            global_mut = get_global_attr(_val, 'mut')
            if not isinstance(global_mut, globalValMut):
                raise TypeError(
                    f'Expect global_mut to be globalValMut, but got {type(global_mut)}')

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ContextVariables):
            return False
        return all(getattr(self, attr) == getattr(__value, attr) for attr in self._EQ_ATTRIBUTES)


class Context(InfoLoader):
    _DELEGATED_PROPS = [
        'local_types',
        'types',
        'cur_func_ty',
        'defined_globals',
        'defined_memory_datas',
        'data_sec_datas',
        'elem_sec_datas',
        'defined_table_datas',

        'import_func_num',
        'import_global_num',
        'import_table_num',
        'import_memory_num'
    ]

    def __init__(self,
                 context_variables: ContextVariables,
                 label_types: Optional[List[list[str]]] = None
                 ) -> None:
        self.context_variables = context_variables
        self.label_types = label_types

    @classmethod
    def from_sep_paras(cls,
                       local_types: List[str],
                       func_type_idxs: List[int],
                       types: List[funcType],
                       cur_func_ty: funcType,
                       defined_globals: list,
                       defined_memory_datas: list,
                       data_sec_datas: list,
                       elem_sec_datas: list,
                       defined_table_datas: list,
                       import_func_num: int,
                       import_global_num: int,
                       import_table_num: int,
                       import_memory_num: int,
                       label_types: Optional[List[list[str]]] = None
                       ):
        context_variables = ContextVariables(
            local_types=local_types,
            func_type_idxs=func_type_idxs,
            types=types,
            cur_func_ty=cur_func_ty,
            defined_globals=defined_globals,
            defined_memory_datas=defined_memory_datas,
            data_sec_datas=data_sec_datas,
            elem_sec_datas=elem_sec_datas,
            defined_table_datas=defined_table_datas,
            import_func_num=import_func_num,
            import_global_num=import_global_num,
            import_table_num=import_table_num,
            import_memory_num=import_memory_num
        )
        return cls(context_variables, label_types)

    def __getattr__(self, item):
        if item in self._DELEGATED_PROPS:
            return getattr(self.context_variables, item)
        raise AttributeError(
            f"{item} is not an attribute of {self.__class__.__name__}")

    def __setattr__(self, key, value):
        if key in self._DELEGATED_PROPS:
            return setattr(self.context_variables, key, value)
        else:
            super().__setattr__(key, value)

    @property
    def func_type_idxs(self):
        return self.context_variables.func_type_idxs

    @property
    def global_val_types(self):
        return [get_global_attr(global_val, 'global_val_type') for global_val in self.defined_globals]

    @property
    def global_muts(self):
        return [get_global_attr(global_val, 'mut') for global_val in self.defined_globals]

    @property
    def table_types(self):
        return [get_table_attr(table, 'val_type') for table in self.defined_table_datas]

    @property
    def data_activable(self):
        return [get_data_attr(data_sec, 'attr') for data_sec in self.data_sec_datas]

    @property
    def elem_ref_types(self):
        return [get_elemseg_attr(elem_sec, 'attr_name') for elem_sec in self.elem_sec_datas]

    @property
    def elem_attrs(self):
        return [get_elemseg_attr(elem_sec, 'attr') for elem_sec in self.elem_sec_datas]

    @classmethod
    def empty_context(cls):
        p_func_type = funcTypeFactory.generate_one_func_type_default(
            param_type=[], result_type=[])
        return cls.from_sep_paras(
            local_types=[],
            func_type_idxs=[],
            types=[],
            cur_func_ty=p_func_type,
            defined_globals=[],
            defined_memory_datas=[],
            data_sec_datas=[],
            elem_sec_datas=[],
            defined_table_datas=[],
            label_types=[],
            import_func_num=0,
            import_global_num=0,
            import_table_num=0,
            import_memory_num=0
        )

    def copy(self):
        return Context(
            self.context_variables.copy(),
            label_types=[inner_list.copy(
            ) for inner_list in self.label_types] if self.label_types is not None else None
        )

    @property
    def defined_memory_num(self):
        return len(self.defined_memory_datas)

    @property
    def data_sec_num(self):
        return len(self.data_sec_datas)

    @property
    def elem_sec_num(self):
        return len(self.elem_sec_datas)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(local_types={self.local_types},\nfunc_type_idxs={self.func_type_idxs},\ntypes={self.types},\ncur_func_ty={self.cur_func_ty},\nlabel_type={self.label_types}\ntable_datas={self.defined_table_datas}\nmemory_datas={self.defined_memory_datas})'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Context):
            return False
        return self.context_variables == __value.context_variables \
            and self.label_types == __value.label_types

    def use_same_variables(self, context: 'Context') -> bool:
        return self.context_variables is context.context_variables


def generate_context_by_insert_label_reuse_data(context: Context, label: list[str]):
    assert context.label_types is not None
    label_types = context.label_types.copy()

    label_types.insert(0, label)
    return Context(context.context_variables, label_types)


def generate_context_by_out_layers_reuse_data(context: Context, out_layers: List[list[str]]):
    assert context.label_types is not None
    label_types = out_layers + context.label_types
    return Context(context.context_variables, label_types)
