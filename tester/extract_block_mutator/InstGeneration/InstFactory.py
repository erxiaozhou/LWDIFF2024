from typing import Optional, Union
from ..InstUtil.ByteInst import ByteImmInst
from ..encode.NGDataPayload import DataPayloadwithName

from ..InstUtil.SpecialImm import UnconstrainedGlobalIdx
from ..InstUtil.Inst import InstWithImm, NoImmInst




class InstFactory:
    generated_opcode_insts = {}

    @staticmethod
    def opcode_inst(opcode):
        if opcode not in InstFactory.generated_opcode_insts:
            InstFactory.generated_opcode_insts[opcode] = NoImmInst(opcode)
        return InstFactory.generated_opcode_insts[opcode]

    @staticmethod
    def generate_global_inst_with_unconstrained_idx(opname, ty):
        assert opname in ['global.get', 'global.set']
        if isinstance(ty, str):
            ty = UnconstrainedGlobalIdx(ty)
        return InstWithImm(opname, ty)



    @staticmethod
    def generate_inst_by_op_and_pre_defined_funcidx(op, imm_part):
        return InstWithImm(op, imm_part)


    @staticmethod
    def generate_binary_info_inst(op, imm_dict:Optional[DataPayloadwithName]=None):
        # print('Generating binary info inst:', op, imm_dict)
        # assert 0
        if imm_dict is None:
            return InstFactory.opcode_inst(op)
        if imm_dict.no_data():
            return InstFactory.opcode_inst(op)
        else:
            return ByteImmInst(op, imm_dict)

    @staticmethod
    def gen_binary_info_inst_high(op, imm_dict:Optional[dict]=None):
        if imm_dict is None:
            return InstFactory.opcode_inst(op)
        if len(imm_dict) == 0:
            return InstFactory.opcode_inst(op)
        else:
            imm_payload = DataPayloadwithName(imm_dict, op)
            return ByteImmInst(op, imm_payload)
    @staticmethod
    def gen_binary_info_inst_high_single_imm(op, imm0):
        if op == 'i32.const'and isinstance(imm0, str):
            raise Exception('imm0 is str')
        imm_payload = DataPayloadwithName({'val': imm0}, op)
        return ByteImmInst(op, imm_payload)
