

import random
from .RandomInstFactory import RandomInstFactory
from .InstFactory import InstFactory
from util.get_random_type import get_random_type


def padding_input_type(existing_layer, expected_layer, context=None):
    common_num = 0
    for ty1, ty2 in zip(existing_layer, expected_layer):
        if ty1 == ty2:
            common_num += 1
        else:
            break
    to_drop = existing_layer[::-1][:len(existing_layer)-common_num]
    inner_layer_to_pad = expected_layer[common_num:]
    insts = []
    # print('===================================================')
    # print(f'existing_layer: {existing_layer}')
    # print(f'expected_layer: {expected_layer}')
    # print(f'common_num: {common_num}')
    # print(f'to_drop: {to_drop}')
    # print(f'inner_layer_to_pad: {inner_layer_to_pad}')
    for ty in to_drop:
        add_inst_drop_operand(insts, ty)
    for ty in inner_layer_to_pad:
        # print(to_drop, insts)
        if random.random() < 0.4 or (ty in ['any']) or (context is None) or (ty not in context.global_val_types):
            insts.append(get_inst_by_require_ty_const(ty))
        else:
            # print('vbkueralvnipeanvnmasmoidm djiodnji')
            possible_global_idxs = [idx for idx, ty_ in enumerate(context.global_val_types) if ty_ == ty]
            idx_ = random.choice(possible_global_idxs)
            new_global_inst = InstFactory.gen_binary_info_inst_high_single_imm('global.get', idx_)
            insts.append(new_global_inst)
        
    return insts

def get_inst_by_require_ty_const(ty):
    if ty == 'i32':
        return RandomInstFactory.generate_random_inst('i32.const')
    if ty == 'i64':
        return RandomInstFactory.generate_random_inst('i64.const')
    if ty == 'f32':
        return RandomInstFactory.generate_random_inst('f32.const')
    if ty == 'f64':
        return RandomInstFactory.generate_random_inst('f64.const')
    if ty == 'v128':
        return RandomInstFactory.generate_random_inst('v128.const')
    if ty == 'funcref':
        return InstFactory.gen_binary_info_inst_high_single_imm('ref.null', 'funcref')
    if ty == 'externref':
        return InstFactory.gen_binary_info_inst_high_single_imm('ref.null', 'externref')
    if ty == 'any':
        return get_inst_by_require_ty_const(get_random_type())
    raise Exception(f'unexpected ty: {ty}')


def add_inst_drop_operand(insts, ty):
    if ty == 'any':
        pass
        # print('&&&&&& insts: ', insts)
    if ty in ['funcref', 'externref']:
        insts.append(InstFactory.opcode_inst('drop'))
    else:
        py2puls_inst_opcode = {
            'i32': 'i32.add',
            'i64': 'i64.add',
            'f32': 'f32.add',
            'f64': 'f64.add',
            'v128': 'i64x2.add',
        }
        new_inst = InstFactory.generate_global_inst_with_unconstrained_idx('global.set', ty=ty)
        index = new_inst.imm_part
        get_inst = InstFactory.generate_global_inst_with_unconstrained_idx('global.get', index)
        plus_inst = InstFactory.opcode_inst(py2puls_inst_opcode[ty])
        extend_insts = [get_inst, plus_inst, new_inst]
        # ! global， global，global
        insts.extend(extend_insts)
        # ! 
