import re
from WasmInfoCfg import ExportType, ImportType
from .get_data_shell import get_export_attr, get_func_idxs, get_global_attr, get_impotr_attr

from extract_block_mutator.encode.NGDataPayload import  DataPayloadwithName
from .encode.byte_define.SectionPart import  section_decoder

from .InstUtil.get_early_exit_pos import get_early_exit_position
from .inst_pose_selector import get_support_pos_candis_from_insts

from .blockParser.tool import get_block_from_insts

from .insert_post_process_nan_func import insert_post_process_nan_func_by_easy_sound_strategy
from .InstUtil.Inst import Inst
from file_util import path_read, path_write, print_ba
from .funcType import funcType
from .watFunc import watFunc
from typing import List, Optional, Tuple
from util.prepare_template import prepare_sec_name2all_ba, id_name_dict

class WasmParser:
    def __init__(self, 
                types=None,
                 imports=None,
                # 
                defined_func_ty_ids=None, #!  
                # 
                defined_table_datas=None,
                defined_memory_datas=None,
                defined_globals=None,
                 exports=None,
                elem_sec_datas=None,
                defined_funcs=None,
                data_sec_datas=None,
                start_sec_data=None, 
                data_count_sec_data=None,
                customs=None
                 ) -> None:
        if types is None:
            types = []
        if imports is None:
            imports = []
        if defined_func_ty_ids is None:
            defined_func_ty_ids = []
        if defined_table_datas is None:
            defined_table_datas = []
        if defined_memory_datas is None:
            defined_memory_datas = []
        if defined_globals is None:
            defined_globals = []
        if exports is None:
            exports = []
        if elem_sec_datas is None:
            elem_sec_datas = []
        if defined_funcs is None:
            defined_funcs = []
        if data_sec_datas is None:
            data_sec_datas = []
        if customs is None:
            customs = []
        self.types:List[funcType] = types
        self.imports:List[DataPayloadwithName] = imports
        self.defined_func_ty_ids:List[int] = defined_func_ty_ids
        self.defined_table_datas:List[DataPayloadwithName] = defined_table_datas
        self.defined_memory_datas:List[DataPayloadwithName] = defined_memory_datas
        self.defined_globals:List[DataPayloadwithName] = defined_globals
        self.exports:List[DataPayloadwithName] = exports
        self.start_sec_data:Optional[int] = start_sec_data
        self.elem_sec_datas: List[DataPayloadwithName] = elem_sec_datas
        self.defined_funcs:List[watFunc] = defined_funcs
        self.data_sec_datas:List[DataPayloadwithName] = data_sec_datas
        self.data_count_sec_data:Optional[int] = data_count_sec_data
        self.customs:List[DataPayloadwithName] = customs
        
        
        self.import_func_num = 0
        self.import_mem_num = 0
        # 
        self.import_func_ty_ids:List[int] = []
        for import_desc in self.imports:
            import_desc_type = get_impotr_attr(import_desc, 'type')
            if import_desc_type == ImportType.func:
                import_attr = get_impotr_attr(import_desc, 'import_attr')
                idx = import_attr.data['typeidx'] # type: ignore
                assert isinstance(idx, int)
                self.import_func_ty_ids.append(idx)
                self.import_func_num += 1
            elif import_desc_type == ImportType.mem:
                self.import_mem_num += 1
                
            
        self.func_ty_idxs =  self.import_func_ty_ids + self.defined_func_ty_ids
        assert len(self.func_ty_idxs) == len(self.defined_funcs) + self.import_func_num
        for defined_func_idx, defined_func in zip(self.defined_func_ty_ids, self.defined_funcs):
            cur_func_type = self.types[defined_func_idx]
            if defined_func is not None:
                defined_func.func_ty = cur_func_type
        # defined func 0 location
        # TODO export func
        if len(self.defined_funcs):
            self.func0 = self.defined_funcs[0]
        else:
            self.func0 = None
        self._func0_block = None
        # self.inst0_infos = None  # TODO  early return inst0_infos
        self._insts0_early_return_pos = None
        self._sop_pos_candis = None
    @property
    def type_num(self):
        return len(self.types)
    @property
    def mem_num(self):
        return len(self.defined_memory_datas) + self.import_mem_num

    @property
    def func_num(self):
        return len(self.defined_funcs) + self.import_func_num

    @property
    def sop_pos_candis(self):
        if self._sop_pos_candis is None:
            insts = self.func0_insts
            preturn = self.insts0_early_return_pos
            self._sop_pos_candis = get_support_pos_candis_from_insts(insts, preturn)
        return self._sop_pos_candis

    def copy(self):
        parser = WasmParser(
            types = [_.copy() for _ in self.types],
            imports= [_.copy() for _ in self.imports],
            defined_func_ty_ids = self.defined_func_ty_ids.copy(),
            defined_table_datas = [_.copy() for _ in self.defined_table_datas],
            defined_memory_datas = [_.copy() for _ in self.defined_memory_datas],
            defined_globals = [_.copy() for _ in self.defined_globals],
            start_sec_data = None if self.start_sec_data is None else self.start_sec_data,
            exports= [_.copy() for _ in self.exports],
            elem_sec_datas = [_.copy() for _ in self.elem_sec_datas],
            defined_funcs = [_.copy() for _ in self.defined_funcs],
            data_sec_datas = [_.copy() for _ in self.data_sec_datas],
            data_count_sec_data = None if self.data_count_sec_data is None else self.data_count_sec_data,
        )
        if self._func0_block is not None:
            parser._func0_block = self._func0_block.copy()
        if self._sop_pos_candis is not None:
            parser._sop_pos_candis = self._sop_pos_candis.copy()
        return parser

    @property
    def global_types(self):
        return [get_global_attr(d, 'global_val_type') for d in self.defined_globals]
    @property
    def global_muts(self):
        return [get_global_attr(d, 'mut') for d in self.defined_globals]

    @property
    def func0_insts(self)->List[Inst]:
        assert self.func0 is not None
        return self.func0.insts

    @func0_insts.setter
    def func0_insts(self, insts):
        assert self.func0 is not None
        self.func0.insts = insts
        self._func0_block = None
        self._insts0_early_return_pos = None

    def clean_pre_info(self):
        self._func0_block = None
        self._insts0_early_return_pos = None

    @property
    def func0_block(self):
        if self._func0_block is None:
            self._func0_block = get_block_from_insts(self.func0_insts, types=self.types)
        return self._func0_block
    @property
    def insts0_early_return_pos(self):
        if self._insts0_early_return_pos is None:
            self._insts0_early_return_pos = get_early_exit_position(self.func0_insts, 1)
        return self._insts0_early_return_pos


    @property
    def func_idxs_in_elem(self):
        func_idxs = []
        for elem_desc in self.elem_sec_datas:
            cur_func_idxs = get_func_idxs(elem_desc)
            func_idxs.extend(cur_func_idxs)
        # func_idxs = [x for x in func_idxs if x is not None]
        return list(set(func_idxs))

    def insert_post_process_nan_func_by_easy_sound_strategy(self):
        insert_post_process_nan_func_by_easy_sound_strategy(self.func0_insts)


    def get_to_test_func_idx(self) -> Optional[int]:
        for _export in self.exports:
            if get_export_attr(_export, 'attr') == ExportType.func:
                if get_export_attr(_export, 'name') == 'to_test':
                    return get_export_attr(_export, 'idx')  # type: ignore
        return None

    @classmethod
    def from_wasm_path(cls, wasm_path):
        return get_parser_from_wasm_path(wasm_path)

    @property
    def defined_memory_num(self):
        return len(self.defined_memory_datas)

# sec_name2decoder = {
#     'custom': custom_sec_decoder
# }

def get_parser_from_wasm_path(wasm_path):
    types = None
    imports = None
    defined_func_ty_ids = None
    defined_table_datas = None
    defined_memory_datas = None
    defined_globals = None
    exports= None
    start_sec_data = None
    elem_sec_datas = None
    defined_funcs = None
    data_sec_datas = None
    data_count_sec_data = None
    customs = []
    
    sec_name2all_ba = prepare_sec_name2all_ba(wasm_path)
    for sec_name, sec_ba in sec_name2all_ba.items():
        # print(f'Processing {sec_name}')
        if sec_name == 'type':
            # print_ba(sec_ba)
            types = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'import':
            imports = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'function':
            defined_func_ty_ids = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'table':
            defined_table_datas = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'memory':
            defined_memory_datas = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'global':
            defined_globals = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'export':
            exports = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'start':
            start_sec_data = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'element':
            elem_sec_datas = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'code':
            defined_funcs = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'data':
            data_sec_datas = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'data_count':
            data_count_sec_data = section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0]
        elif sec_name == 'custom':
            customs.append(section_decoder.byte_decode_and_generate(memoryview(sec_ba))[0])
    return WasmParser(
        types = types,
        imports= imports,
        defined_func_ty_ids = defined_func_ty_ids,
        defined_table_datas = defined_table_datas,
        defined_memory_datas = defined_memory_datas,
        defined_globals = defined_globals,
        exports= exports,
        start_sec_data = start_sec_data,
        elem_sec_datas = elem_sec_datas,
        defined_funcs = defined_funcs,
        data_sec_datas = data_sec_datas,
        data_count_sec_data = data_count_sec_data,
        customs=customs
    )
