from ..InstGeneration.InstFactory import InstFactory
from ..InstGeneration.padding_input_type import add_inst_drop_operand


def reverse_op_idxs(op_types, reset_op_idxs):
    op_types = op_types[::-1]
    len_op_types = len(op_types)
    reset_op_idxs = [len_op_types - idx - 1 for idx in reset_op_idxs][::-1]
    return op_types,reset_op_idxs
    
def generate_insts_for_byop(context, max_local, vals, op_types, reset_op_idxs):
    if len(vals) == 0:
        return []
    non_mutation_tys = [ty for idx, ty in enumerate(op_types) if idx not in reset_op_idxs]
    # ====================================reset local
    cur_local_types = context.local_types
    # not exist tys
    not_exist_tys = [ty for ty in non_mutation_tys if ty not in cur_local_types]
    if len(cur_local_types) > max_local:
        new_tys = not_exist_tys
        cur_local_types.extend(new_tys)
        local_idxs = [_get_local_idx(ty, cur_local_types) for ty in non_mutation_tys]
    else:
        new_tys = non_mutation_tys
        ori_local_num = len(cur_local_types)
        cur_local_types.extend(new_tys)
        local_idxs = [ori_local_num + idx for idx in range(len(new_tys))]
    #  drop / store to local ； 
    insts = []
    cur_to_store_op_idx = 0
    for param_idx, param_ty in enumerate(op_types):
        if param_idx in reset_op_idxs:
            add_inst_drop_operand(insts, param_ty)
        else:
            insts.append(InstFactory.gen_binary_info_inst_high_single_imm('local.set', local_idxs[cur_to_store_op_idx]))
            assert param_ty == cur_local_types[local_idxs[cur_to_store_op_idx]]
            cur_to_store_op_idx += 1
    # ====================================reset ops
    set_insts = []
    cur_to_set_op_idx = 0
    cur_to_store_op_idx = 0
    reset_op_idxs = [len(op_types) - idx - 1 for idx in reset_op_idxs]
    
    op_num = len(op_types)
    for param_idx in list(range(op_num)):
        if param_idx in reset_op_idxs:
            val = vals[cur_to_set_op_idx]
            assert val.insts is not None
            set_insts.extend(val.insts)
            cur_to_set_op_idx += 1
        else:
            set_insts.append(InstFactory.gen_binary_info_inst_high_single_imm('local.get', local_idxs[-cur_to_store_op_idx-1]))
            cur_to_store_op_idx += 1
    # print('last three insts', [inst for inst in set_insts[-3:]])
    insts = insts + set_insts#[::-1]
    return insts
    
    
def _get_local_idx(target_ty, cur_types):
    for idx, ty in enumerate(cur_types[::-1]):
        if ty == target_ty:
            return len(cur_types) - idx - 1
    raise ValueError
        