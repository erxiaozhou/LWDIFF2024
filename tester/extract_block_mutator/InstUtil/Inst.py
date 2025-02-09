
from .SpecialImm import SpecialGlobalIdx, SpecialImm, UnconstrainedGlobalIdx
from typing import Any

class Inst:
    opcode_text:str
    imm_part:Any
    text_encoding_rule_with_imm = '{opcode} {imm_part}'
    def __init__(self) -> None:
        raise NotImplementedError

    def get_imm_by_ph(self, imm_ph_repr:str):
        raise NotImplementedError

    def __eq__(self, o: object) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    def copy(self):
        raise DeprecationWarning('To remove')
        return Inst(self.opcode_text, self.imm_part)

    def has_special_global_idx(self):
        return False

    def has_unconstraint_global_idx(self):
        return False

class NoImmInst(Inst):
    def __init__(self, opcode_text:str) -> None:
        # if opcode_text == 'if':
        #     raise Exception('Should not')
        # super().__init__(opcode_text, None)
        self.opcode_text = opcode_text

    def copy(self):
        return self

    def has_special_global_idx(self):
        return False
    
    def has_unconstraint_global_idx(self):
        return False

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Inst):
            return False
        return self.opcode_text == o.opcode_text
    
    def __repr__(self) -> str:
        return f'NoImmInst({self.opcode_text})'

    def __hash__(self) -> int:
        return hash(self.opcode_text)
    
class InstWithImm(Inst):
    def __init__(self, opcode_text:str, imm_part_val:SpecialImm) -> None:
        assert imm_part_val is not None
        self.opcode_text = opcode_text
        self.imm_part = imm_part_val

    def copy(self):
        return InstWithImm(self.opcode_text, self.imm_part)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.opcode_text}, {self.imm_part})'
    
    
    def has_special_global_idx(self):
        # to remove
        return isinstance(self.imm_part, SpecialGlobalIdx)

    def has_unconstraint_global_idx(self):
        # to remove
        return isinstance(self.imm_part, UnconstrainedGlobalIdx)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Inst):
            return False
        return self.opcode_text == o.opcode_text and self.imm_part == o.imm_part
    

def is_if_inst(inst:Inst):
    op_text = inst.opcode_text
    return op_text == 'if' 

blocktype_ops = {'block', 'loop', 'if'}
def imm_is_blocktpye(inst:Inst):
    if inst.opcode_text not in blocktype_ops:
        return False
    return True
