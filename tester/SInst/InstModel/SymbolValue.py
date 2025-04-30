from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Optional
from .PHEnv import PHEnv
from extract_block_mutator.Context import Context

class SymbolValue:
    @abstractmethod
    def get_symbol_and_constraints(self, context: Optional[Context] = None, ph_env: Optional[PHEnv] = None) -> Tuple[Any, List]:
        ...

    @staticmethod
    def is_valid_str(s: str) -> bool:
        ...

