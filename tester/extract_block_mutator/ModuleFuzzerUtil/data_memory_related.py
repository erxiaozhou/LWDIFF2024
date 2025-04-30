from typing import Optional
from WasmInfoCfg import DataSegAttr
from extract_block_mutator.get_data_shell import get_memory_attr
from ..WasmParser import WasmParser
from random import choice, randint, random
from .DefGenerator import activeDataSegmentGenerator, passiveDataSegmentGenerator, memDescGenerator
from ..SpecialConst import SpecialDefConst

def memory_exist(wasm_parser: WasmParser) -> bool:
    return len(wasm_parser.defined_memory_datas) > 0


def can_insert_memory(wasm_parser: WasmParser) -> bool:
    return len(wasm_parser.defined_memory_datas) < SpecialDefConst.MaxMemNum.get_concrete_value()

def insert_memory(wasm_parser: WasmParser) -> None:
    wasm_parser.defined_memory_datas.append(memDescGenerator.generate_valid_one(wasm_parser.defined_memory_num))


def reset_random_memory(wasm_parser: WasmParser) -> None:
    mem_idx = randint(0, len(wasm_parser.defined_memory_datas) - 1)
    ori_mem_desc_cur_len = get_memory_attr(wasm_parser.defined_memory_datas[mem_idx], 'min')
    wasm_parser.defined_memory_datas[mem_idx] = memDescGenerator.generate_valid_one(ori_mem_desc_cur_len)

def can_insert_passive_data(wasm_parser: WasmParser) -> bool:
    return passiveDataSegmentGenerator.can_insert()


def insert_passive_data(wasm_parser: WasmParser) -> None:
    new_data_sec = passiveDataSegmentGenerator.generate_valid_one()
    wasm_parser.data_sec_datas.append(new_data_sec)


def can_insert_active_data(wasm_parser: WasmParser) -> bool:
    return activeDataSegmentGenerator.can_insert(wasm_parser)


def insert_active_data(wasm_parser: WasmParser) -> None:
    new_data_sec = activeDataSegmentGenerator.generate_valid_one(wasm_parser)
    wasm_parser.data_sec_datas.append(new_data_sec)

def generate_a_data_seg(wasm_parser: WasmParser, attr:Optional[DataSegAttr]=None):
    if attr is None:
        attr = choice(list(DataSegAttr))
    if attr == DataSegAttr.passive:
        seg = passiveDataSegmentGenerator.generate_valid_one()
    else:
        try:
            seg = activeDataSegmentGenerator.generate_valid_one(wasm_parser)
        except ValueError:
            seg = passiveDataSegmentGenerator.generate_valid_one()
    return seg


def data_exist(wasm_parser: WasmParser) -> bool:
    return len(wasm_parser.data_sec_datas) > 0

def delete_data(wasm_parser: WasmParser) -> None:
    data_idx = choice(list(range(len(wasm_parser.data_sec_datas))))
    wasm_parser.data_sec_datas.pop(data_idx)


def can_reset_random_data(wasm_parser: WasmParser) -> bool:
    return data_exist(wasm_parser)


def reset_random_data(wasm_parser: WasmParser) -> None:
    new_data_sec = None
    if random() > 0.5:
        if activeDataSegmentGenerator.can_insert(wasm_parser):
            new_data_sec = activeDataSegmentGenerator.generate_valid_one(wasm_parser)
    if new_data_sec is None:
        new_data_sec = passiveDataSegmentGenerator.generate_valid_one()
    data_idx = choice(list(range(len(wasm_parser.data_sec_datas))))
    wasm_parser.data_sec_datas[data_idx] = new_data_sec
