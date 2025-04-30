import re
from enum import Enum, auto

class FailedParsingException(Exception):
    pass

class CalcType(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()
    Mod = auto()
