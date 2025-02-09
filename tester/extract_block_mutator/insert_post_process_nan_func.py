from config_inst_info import easy_sound_strategy_need_transfer_result
from typing import List, Tuple

from .InstGeneration.InstFactory import InstFactory
from .InstUtil.SpecialImm import predefinedFuncIdx
from .InstUtil import Inst

inst_name2category = {}

for categoty, inst_names in easy_sound_strategy_need_transfer_result.items():
    for inst_name in inst_names:
        # for predefined_func_name in 
        inst_name2category[inst_name] = categoty

def insert_post_process_nan_func_by_easy_sound_strategy(insts: List[Inst]):
    instrument_pos2_category:List[Tuple[int, str]] = []
    for i, inst in enumerate(insts):
        if inst.opcode_text in inst_name2category:
            categoty = inst_name2category[inst.opcode_text]
            # categoty2instrument_pos.setdefault(categoty, []).append(i)
            instrument_pos2_category.append((i, categoty))
    instrument_pos2_category = instrument_pos2_category[::-1]
    for pos, categoty in instrument_pos2_category:
        if categoty ==  'sure_need_f32':
            # ['can_f32', 'can_f64', 'can_f32x4', 'can_f64x2']
            to_insert_insts = [InstFactory.generate_inst_by_op_and_pre_defined_funcidx('call', predefinedFuncIdx('can_f32'))]
        elif categoty == 'sure_need_f64':
            to_insert_insts = [InstFactory.generate_inst_by_op_and_pre_defined_funcidx('call', predefinedFuncIdx('can_f64'))]
        elif categoty == 'sure_need_v128':
            to_insert_insts = [InstFactory.generate_inst_by_op_and_pre_defined_funcidx('call', predefinedFuncIdx('can_f32x4')), InstFactory.generate_inst_by_op_and_pre_defined_funcidx('call', predefinedFuncIdx('can_f64x2'))]
        else:
            continue
        insts[pos+1:pos+1] = to_insert_insts
