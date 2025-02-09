from enum import Enum, auto
from typing import Optional

class ExpExec(Enum):
    Trap = auto()
    Normal = auto()
    NotSure = auto()

    @classmethod
    def from_trap_bool(cls, trap:Optional[bool]):
        if trap is None:
            return cls.NotSure
        return cls.Normal if not trap else cls.Trap