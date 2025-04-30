from typing import List
from .Inst import Inst, is_if_inst


def get_early_exit_position(insts:List[Inst], outer_depth):
    length_cosidering_early_exit2 = len(insts)
    depth = outer_depth
    for idx, inst in enumerate(insts):
        if inst.opcode_text in ['return', 'unreachable']:
            length_cosidering_early_exit2 = idx
            break
        elif inst.opcode_text == 'br':
            if inst.imm_part.val+1 == depth:
                length_cosidering_early_exit2 = idx
                break
        elif inst.opcode_text in ('block', 'loop'):
            depth += 1
        elif is_if_inst(inst):
            depth += 1
        elif inst.opcode_text == 'end':
            depth -= 1
    return length_cosidering_early_exit2
    