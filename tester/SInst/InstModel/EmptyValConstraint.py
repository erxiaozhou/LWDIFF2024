from random import choice, randint, sample
from typing import List, Union, Optional
from extract_block_mutator.Context import Context
from ..InstModel.PHEnv import PHEnv
from .ValConstraint import ValConstraint


class EmptyValConstraint(ValConstraint):
    def __init__(self):
        # assert 0
        super().__init__(set(), set())

    def get_symbol_constraint(self, context:Optional[Context]=None, ph_env:Optional[PHEnv]=None):
        return True
        