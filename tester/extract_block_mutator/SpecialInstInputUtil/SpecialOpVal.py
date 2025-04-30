from typing import List
from ..InstUtil.Inst import Inst

class SpecialOpVal:
    def __init__(self, ty: str, val_name: str, insts:List[Inst]) -> None:
        self.ty = ty
        self.val_name = val_name
        self.insts = insts
            

    def __repr__(self):
        return f'{self.__class__.__name__}(ty={self.ty}, val_name={self.val_name})'

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, self.__class__)
        return self.ty == __value.ty and self.val_name == __value.val_name 

    def __hash__(self) -> int:
        return hash((self.ty, self.val_name))
