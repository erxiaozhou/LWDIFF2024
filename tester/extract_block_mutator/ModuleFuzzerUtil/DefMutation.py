from ..WasmParser import WasmParser
from typing import Callable
from WasmInfoCfg import SectionType


class Mutation:
    def __init__(self, 
                    name:str,
                    section_type:SectionType,
                    apply_condition_func:Callable[[WasmParser], bool], 
                    apply_func:Callable[[WasmParser], None]) -> None:
        self.apply_condition_func = apply_condition_func
        self.apply_func = apply_func
        self.section_type = section_type
        self.name = name
        
    def can_apply(self, wasm_parzer:WasmParser):
        return self.apply_condition_func(wasm_parzer)
    
    def apply(self, wasm_parzer:WasmParser):
        return self.apply_func(wasm_parzer)
