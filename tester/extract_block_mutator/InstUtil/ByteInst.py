
from typing import Any

from extract_block_mutator.encode.byte_define.DecoderID import PartDescMemory

from ..encode.NGDataPayload import DataPayloadwithName
from .Inst import Inst
# CommonDataPayload


class ByteImmInst(Inst):
    def __init__(self, opcode_text:str, imm_dict:DataPayloadwithName) -> None:
        self.opcode_text = opcode_text
        # imm_dict  encode   
        self.imm_part = imm_dict

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.opcode_text} {self.imm_part})'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ByteImmInst):
            return False
        if self.opcode_text != o.opcode_text:
            return False
        return self.imm_part == o.imm_part

    def copy(self):
        return self.__class__(self.opcode_text, self.imm_part.copy())
    

    def get_imm_by_ph(self, imm_ph_repr:str):

        part_desc = PartDescMemory.get_desc(self.opcode_text)
        if part_desc.not_prefix_num == 1:
            return self.imm_part.val
        else:
            print(f'VVVVVVVVV self: {self}, imm_ph_repr: {imm_ph_repr}')
            assert imm_ph_repr.startswith('imm_')
            idx = int(imm_ph_repr[4:])
            attr_name = part_desc.not_fix_part_names[idx]
            return self.imm_part.data[attr_name]