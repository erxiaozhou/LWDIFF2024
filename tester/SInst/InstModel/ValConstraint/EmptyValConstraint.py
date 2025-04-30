from random import choice, randint, sample
from typing import List, Union, Optional
from extract_block_mutator.Context import Context
from ..PHEnv import PHEnv
from .ValConstraint import ValConstraint


class EmptyValConstraint(ValConstraint):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmptyValConstraint, cls).__new__(cls)
            super(EmptyValConstraint, cls._instance).__init__(set(), set())
        return cls._instance
    
    def __init__(self):
        pass
    
    def get_symbol_constraint(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None):
        return True
        