from enum import Enum
from typing import Protocol


class PHType(Enum):
    IMM = 'imm'
    OPERAND = 'operand'

class PH(Protocol):
    @property
    def ty(self)->str:
        ...
    @property
    def idx(self)->int:
        ...
    @property
    def ph_attr(self):
        ...
