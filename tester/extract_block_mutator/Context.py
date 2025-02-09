from typing import List, Optional
from WasmInfoCfg import globalValMut
from WasmInfoCfg import ElemSecAttr
from extract_block_mutator.get_data_shell import get_data_attr, get_elemseg_attr, get_global_attr, get_table_attr
from .funcType import funcType
from .funcTypeFactory import funcTypeFactory


class ContextVariables:
    def __init__(self,
                 local_types: List[str],
                 func_type_ids: List[int],
                 types: List[funcType],
                 cur_func_ty: funcType,
                 defined_globals:list,
                 defined_memory_datas:list,
                 data_sec_datas: list,
                 elem_sec_datas: list,
                 defined_table_datas: list,
                 func_idxs_in_elem: Optional[List[int]] = None,
                 import_func_num = 0
                 ) -> None:
        # assert 0
        self.local_types = local_types
        self.func_type_ids = func_type_ids
        self.types = types
        self.cur_func_ty = cur_func_ty
        self.defined_globals:list = defined_globals
        self.defined_memory_datas:list = defined_memory_datas
        self.data_sec_datas: list = data_sec_datas
        self.elem_sec_datas: list = elem_sec_datas
        self.defined_table_datas:list = defined_table_datas
        self._type_check()
        if func_idxs_in_elem is None:
            func_idxs_in_elem = []
        self.func_idxs_in_elem: list[int] = func_idxs_in_elem
        self.import_func_num = import_func_num

    def copy(self):
        return ContextVariables(
            local_types=self.local_types.copy(),
            func_type_ids=self.func_type_ids.copy(),
            types=[ty.copy() for ty in self.types],
            cur_func_ty=self.cur_func_ty.copy(),
            defined_globals=self.defined_globals.copy(),
            defined_memory_datas=self.defined_memory_datas.copy(),
            data_sec_datas=self.data_sec_datas.copy(),
            elem_sec_datas=self.elem_sec_datas.copy(),
            defined_table_datas = self.defined_table_datas.copy(),
            func_idxs_in_elem=self.func_idxs_in_elem.copy() if self.func_idxs_in_elem is not None else None,
            import_func_num = self.import_func_num
        )

    def _type_check(self):
        for local_type in self.local_types:
            assert isinstance(local_type, str)
        for func_type_id in self.func_type_ids:
            assert isinstance(func_type_id, int)
        for func_type in self.types:
            assert isinstance(func_type, funcType)
        assert isinstance(self.cur_func_ty, funcType)
        for _val in self.defined_globals:
            global_mut = get_global_attr(_val, 'mut')
            if not isinstance(global_mut, globalValMut):
                raise TypeError(f'Expect global_mut to be globalValMut, but got {type(global_mut)}')
            # assert isinstance(global_mut, globalValMut)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ContextVariables):
            return False
        return self.local_types == __value.local_types \
            and self.func_type_ids == __value.func_type_ids \
            and self.types == __value.types \
            and self.cur_func_ty == __value.cur_func_ty  \
            and self.defined_globals == __value.defined_globals \
            and self.import_func_num == __value.import_func_num


class Context:
    def __init__(self,
                 context_variables:ContextVariables,
                 label_types: Optional[List[list[str]]] = None
                 ) -> None:
        self.context_variables = context_variables
        self.label_types = label_types

    @classmethod
    def from_sep_paras(cls,
                 local_types: List[str],
                 func_type_ids: List[int],
                 types: List[funcType],
                 cur_func_ty: funcType,
                 defined_globals:list,
                 defined_memory_datas:list,
                 data_sec_datas: list,
                 elem_sec_datas: list,
                 defined_table_datas: list,
                 label_types: Optional[List[list[str]]] = None,
                 func_idxs_in_elem: Optional[List[int]] = None,
                 import_func_num = 0
                 ):
        context_variables = ContextVariables(
            local_types=local_types,
            func_type_ids=func_type_ids,
            types=types,
            cur_func_ty=cur_func_ty,
            defined_globals=defined_globals,
            defined_memory_datas=defined_memory_datas,
            data_sec_datas=data_sec_datas,
            elem_sec_datas=elem_sec_datas,
            defined_table_datas=defined_table_datas,
            func_idxs_in_elem=func_idxs_in_elem,
            import_func_num=import_func_num
        )
        return cls(context_variables, label_types)

    @property
    def local_types(self):# -> Any:
        return self.context_variables.local_types
    @local_types.setter
    def local_types(self, local_types):
        self.context_variables.local_types = local_types
    @property
    def func_type_ids(self):
        return self.context_variables.func_type_ids
    @func_type_ids.setter
    def func_type_ids(self, func_type_ids):
        self.context_variables.func_type_ids = func_type_ids
    @property
    def types(self):
        return self.context_variables.types
    @types.setter
    def types(self, types):
        self.context_variables.types = types
    @property
    def cur_func_ty(self):
        return self.context_variables.cur_func_ty
    @cur_func_ty.setter
    def cur_func_ty(self, cur_func_ty):
        self.context_variables.cur_func_ty = cur_func_ty

    @property
    def defined_globals(self):
        return self.context_variables.defined_globals
    @defined_globals.setter
    def defined_globals(self, defined_globals):
        self.context_variables.defined_globals = defined_globals
    @property
    def defined_memory_datas(self):
        return self.context_variables.defined_memory_datas
    @defined_memory_datas.setter
    def defined_memory_datas(self, defined_memory_datas):
        self.context_variables.defined_memory_datas = defined_memory_datas
    @property
    def data_sec_datas(self):
        return self.context_variables.data_sec_datas
    @data_sec_datas.setter
    def data_sec_datas(self, data_sec_datas):
        self.context_variables.data_sec_datas = data_sec_datas
    @property
    def elem_sec_datas(self):
        return self.context_variables.elem_sec_datas
    @elem_sec_datas.setter
    def elem_sec_datas(self, elem_sec_datas):
        self.context_variables.elem_sec_datas = elem_sec_datas
    @property
    def defined_table_datas(self):
        return self.context_variables.defined_table_datas
    @defined_table_datas.setter
    def defined_table_datas(self, defined_table_datas):
        self.context_variables.defined_table_datas = defined_table_datas
    @property
    def func_idxs_in_elem(self):
        return self.context_variables.func_idxs_in_elem
    @func_idxs_in_elem.setter
    def func_idxs_in_elem(self, func_idxs_in_elem):
        self.context_variables.func_idxs_in_elem = func_idxs_in_elem
    @property
    def import_func_num(self):
        return self.context_variables.import_func_num
    @import_func_num.setter
    def import_func_num(self, import_func_num):
        self.context_variables.import_func_num = import_func_num

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
        return [get_elemseg_attr(elem_sec, 'attr_name')  for elem_sec in self.elem_sec_datas]

    @property
    def elem_attrs(self):
        return [get_elemseg_attr(elem_sec, 'attr') for elem_sec in self.elem_sec_datas]



    @classmethod
    def empty_context(cls):
        p_func_type = funcTypeFactory.generate_one_func_type_default(param_type=[], result_type=[])
        return cls.from_sep_paras(
            local_types=[],
            func_type_ids=[],
            types=[],
            cur_func_ty=p_func_type,
            defined_globals=[],
            defined_memory_datas=[],
            data_sec_datas=[],
            elem_sec_datas=[],
            defined_table_datas=[],
            label_types=[],
            import_func_num=0
            )

    def copy(self):
        # assert 0
        return Context(
            self.context_variables.copy(),
            label_types=self.label_types.copy() if self.label_types is not None else None
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

    @property
    def table_num(self):
        return len(self.defined_table_datas)

    @property
    def local_num(self):
        return len(self.local_types)
    @property
    def func_num(self):
        return len(self.func_type_ids)
    @property
    def global_num(self):
        return len(self.defined_globals)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(local_types={self.local_types},\nfunc_type_ids={self.func_type_ids},\ntypes={self.types},\ncur_func_ty={self.cur_func_ty},\nlabel_type={self.label_types}\ntable_datas={self.defined_table_datas}\nmemory_datas={self.defined_memory_datas})'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Context):
            return False
        return self.context_variables == __value.context_variables \
            and self.label_types == __value.label_types 

    def use_same_variables(self, context: 'Context') -> bool:
        # print(f'Debugdd, see two repre {id(self.context_variables)} and {id(context.context_variables)}')
        return self.context_variables is context.context_variables



def generate_context_by_insert_label_reuse_data(context: Context, label:list[str]):
    assert context.label_types is not None
    label_types = context.label_types.copy()
    # print('Inserted label:', label)
    label_types.insert(0, label)
    return Context(context.context_variables, label_types)


def generate_context_by_out_layers_reuse_data(context: Context, out_layers:List[list[str]]):
    assert context.label_types is not None
    label_types = out_layers + context.label_types
    return Context(context.context_variables, label_types)
