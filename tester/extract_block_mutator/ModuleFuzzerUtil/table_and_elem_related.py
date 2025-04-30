from typing import Optional
from WasmInfoCfg import ElemSecAttr
from ..WasmParser import WasmParser
from random import choice, randint, random
from .DefGenerator import oneTableDescGenerator
from .DefGenerator import passiveElemSegmentGenerator, declarativeElemSegmentGenerator,activeElemSegmentGenerator
from ..SpecialConst import SpecialDefConst, SpecialModuleConst, SpecialModuleConstGetter


def can_insert_table(wasm_parser: WasmParser) -> bool:
    return SpecialModuleConstGetter(SpecialModuleConst.CurTableNum).get_concrete_value(wasm_parser) < SpecialDefConst.MaxTableNum.get_concrete_value() 

def insert_table(wasm_parser: WasmParser) -> None:
    wasm_parser.defined_table_datas.append(oneTableDescGenerator.generate_valid_one())


def table_exist(wasm_parser: WasmParser) -> bool:
    return SpecialModuleConstGetter(SpecialModuleConst.CurTableNum).get_concrete_value(wasm_parser) > 0


def delete_table(wasm_parser: WasmParser) -> None:
    table_idx = randint(0, SpecialModuleConstGetter(SpecialModuleConst.CurTableNum).get_concrete_value(wasm_parser) -1)
    wasm_parser.defined_table_datas.pop(table_idx)


def reset_random_table(wasm_parser: WasmParser) -> None:
    table_idx = randint(0, SpecialModuleConstGetter(SpecialModuleConst.CurTableNum).get_concrete_value(wasm_parser)-1)
    wasm_parser.defined_table_datas[table_idx] = oneTableDescGenerator.generate_valid_one()


def elem_seg_exist(wasm_parser: WasmParser) -> bool:
    return SpecialModuleConstGetter(SpecialModuleConst.CurElemSegNum).get_concrete_value(wasm_parser) > 0


def reset_random_elem_sec(wasm_parser: WasmParser) -> None:
    elem_idx = randint(0, SpecialModuleConstGetter(SpecialModuleConst.CurElemSegNum).get_concrete_value(wasm_parser)-1)
    new_seg = _generate_a_random_elem_segment(wasm_parser)
    wasm_parser.elem_sec_datas[elem_idx] = new_seg

def _generate_a_random_elem_segment(wasm_parser: WasmParser):
    r = random()
    if r < 1/3:
        seg = passiveElemSegmentGenerator.generate_valid_one(wasm_parser)
    elif r < 2/3:
        seg = declarativeElemSegmentGenerator.generate_valid_one(wasm_parser)
    else:
        seg = activeElemSegmentGenerator.generate_valid_one(wasm_parser)
    return seg


def delete_elem_sec(wasm_parser: WasmParser) -> None:
    elem_idx = choice(list(range(len(wasm_parser.elem_sec_datas))))
    wasm_parser.elem_sec_datas.pop(elem_idx)

def can_insert_passive_elem(wasm_parser: WasmParser) -> bool:
    return passiveElemSegmentGenerator.can_insert(wasm_parser)

def can_insert_declarative_elem(wasm_parser: WasmParser) -> bool:
    return declarativeElemSegmentGenerator.can_insert(wasm_parser)


def can_insert_active_elem(wasm_parser: WasmParser) -> bool:
    return activeElemSegmentGenerator.can_insert(wasm_parser)

def insert_passive_elem(wasm_parser: WasmParser) -> None:
    seg = passiveElemSegmentGenerator.generate_valid_one(wasm_parser)
    wasm_parser.elem_sec_datas.append(seg)

def insert_active_elem(wasm_parser: WasmParser) -> None:
    seg = activeElemSegmentGenerator.generate_valid_one(wasm_parser)
    wasm_parser.elem_sec_datas.append(seg)

def insert_declarative_elem(wasm_parser: WasmParser) -> None:
    seg = declarativeElemSegmentGenerator.generate_valid_one(wasm_parser)
    wasm_parser.elem_sec_datas.append(seg)


def generate_elem_seg(wasm_parser: WasmParser, elem_seg_attr:Optional[ElemSecAttr]=None, ref_type:Optional[str]=None): 
    if ref_type is None:
        ref_type = choice(['funcref', 'externref'])
    if elem_seg_attr is None:
        elem_seg_attr = choice(list(ElemSecAttr))
    if elem_seg_attr == ElemSecAttr.passive:
        seg = passiveElemSegmentGenerator.generate_valid_one(wasm_parser,ref_type=ref_type)
    elif elem_seg_attr == ElemSecAttr.declarative:
        seg = declarativeElemSegmentGenerator.generate_valid_one(wasm_parser,ref_type=ref_type)
    else:
        seg = activeElemSegmentGenerator.generate_valid_one(wasm_parser)
    return seg
