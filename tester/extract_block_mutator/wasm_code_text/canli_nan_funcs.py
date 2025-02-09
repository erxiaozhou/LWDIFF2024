

import copy
from math import nan
from extract_block_mutator.InstGeneration.InstFactory import InstFactory
from extract_block_mutator.encode.new_defined_data_type import Blocktype
from extract_block_mutator.funcTypeFactory import funcTypeFactory
from extract_block_mutator.watFunc import watFunc
# nan
# watFunc
# funcTypeFactory
# InstFactory

f32_can_func = watFunc(
    insts = [
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.opcode_inst('f32.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if',Blocktype(funcTypeFactory.generate_one_func_type_default([],['f32']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f32.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.opcode_inst('end')
    ],
    defined_local_types=[],
    func_ty=funcTypeFactory.generate_one_func_type_default(['f32'], ['f32'])
)

f64_can_func = watFunc(
    insts = [
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.opcode_inst('f64.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if',Blocktype(funcTypeFactory.generate_one_func_type_default([],['f64']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f64.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.opcode_inst('end')
    ],
    defined_local_types=[],
    func_ty=funcTypeFactory.generate_one_func_type_default(['f64'], ['f64'])
)

f32_4_can_func = watFunc(
    insts=[
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.extract_lane', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.tee', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('f32.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], ['f32']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f32.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.replace_lane', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.extract_lane', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.tee', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('f32.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], ['f32']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f32.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.replace_lane', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.extract_lane', 2),
        InstFactory.gen_binary_info_inst_high_single_imm('local.tee', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('f32.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], ['f32']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f32.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.replace_lane', 2),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.extract_lane', 3),
        InstFactory.gen_binary_info_inst_high_single_imm('local.tee', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('f32.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], ['f32']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f32.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('f32x4.replace_lane', 3),
    ],
    defined_local_types=['f32'],
    func_ty=funcTypeFactory.generate_one_func_type_default(['v128'], ['v128'])
)

f64_2_can_func = watFunc(
    insts=[
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('f64x2.extract_lane', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.tee', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('f64.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], ['f64']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f64.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('f64x2.replace_lane', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 0),
        InstFactory.gen_binary_info_inst_high_single_imm('f64x2.extract_lane', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.tee', 1),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('f64.ne'),
        InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(funcTypeFactory.generate_one_func_type_default([], ['f64']))),
        InstFactory.gen_binary_info_inst_high_single_imm('f64.const', nan),
        InstFactory.opcode_inst('else'),
        InstFactory.gen_binary_info_inst_high_single_imm('local.get', 1),
        InstFactory.opcode_inst('end'),
        InstFactory.gen_binary_info_inst_high_single_imm('f64x2.replace_lane', 1)
    ],
    defined_local_types=['f64'],
    func_ty=funcTypeFactory.generate_one_func_type_default(['v128'], ['v128'])
)


pre_defined_func_code ={
  'can_f32': f32_can_func,
  'can_f64': f64_can_func,
  'can_f32x4': f32_4_can_func,
  'can_f64x2': f64_2_can_func
}
def get_process_nan_func(func_name):
    func = pre_defined_func_code[func_name]
    return func.copy()