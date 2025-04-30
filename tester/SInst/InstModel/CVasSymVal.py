from typing import Any, List, Optional
from extract_block_mutator.Context import Context
from .SymbolValue import SymbolValue
from .PHEnv import PHEnv


class CVasSymVal(SymbolValue):
    def concrete_val(self):
        raise NotImplementedError
    
    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> tuple[Any, List]:
        return self.concrete_val(), []
