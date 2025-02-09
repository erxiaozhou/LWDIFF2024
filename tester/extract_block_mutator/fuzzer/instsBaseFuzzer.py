from pathlib import Path

from ..funcTypeFactory import funcTypeFactory
from typing import Dict, List, Optional, Tuple, Union
from ..rewrite_to_ensure_term_easy import reweite_to_ensure_term_easy

from ..blockParser.block import wasmBlock

from ..inst_pose_selector import RandomPosSelector


from ..blockParser.inst_pos_for_insert import inst_pos2type_layers_for_insert, generate_inst_pos2type_layers_for_insert
from .Fuzzer import Fuzzer

from ..InstUtil import Inst
from ..funcType import funcType
from ..parser_to_file_util import parser2wasm
from ..WasmParser import WasmParser
from .util import Action, ActionType

from ..InstUtil.get_early_exit_pos import get_early_exit_position
from ..Context import Context, generate_context_by_out_layers_reuse_data
from ..tool import get_func0_context_from_wat_parser
from time import time


# for the situation that there is no inner block
class instsBaseFuzzer(Fuzzer):
    def __init__(self):
        super().__init__()
        self.pos_selector = RandomPosSelector()
        
    def generate_insts(self, inst_type: funcType, context: Context):
        raise NotImplementedError

    def fuzz_one(self, ori_wasm: Union[Path, str], tgt_wasm_path, parser:Optional[WasmParser]=None, remove_loop_=False):
        t0 = time()
        
        ori_parser = self.get_parser_of_ori_wasm(ori_wasm, parser, remove_loop_)
        assert ori_parser is not None
        if ori_parser is None:
            raise ValueError(f'ori_parser is None; ori_wasm: {ori_wasm}')
        t1 = time()
        if self.logger is not None:

            self.logger.debug(f'time of parsing {Path(ori_wasm).name}: {t1-t0}; inst num: {len(ori_parser.func0_insts)}')
        func0_context = get_func0_context_from_wat_parser(ori_parser)
        
        block = ori_parser.func0_block
        assert block is not None
        assert ori_parser.func0 is not None
        mutation_action = self.select_aciton(ori_parser.func0.insts, func0_context)

        ori_insts = ori_parser.func0_insts
        self.adopt_action(ori_insts, mutation_action, func0_context, block, ori_parser)
        # ori_wasm.func0_insts = ori_insts
        assert ori_insts == ori_parser.func0_insts
        self.process_before_write(ori_parser)
        
        parser2wasm(ori_parser, tgt_wasm_path)
        t2 = time()
        if self.logger is not None:
            self.logger.debug(f'time of mutating {Path(ori_wasm).name}: {t2-t1}')


    def adopt_action(self, insts: List[Inst], action: Action, func0_context: Context, block:wasmBlock, ori_parser: WasmParser):
        # print(f' fkdsanv;kdafjgnojerokne[rfa action: {action}')
        # !  replace 
        action_poss = action.to_replace_indexs
        assert isinstance(action_poss, list) and len(action_poss) == 2
        inst_index = action_poss[0]
        assert isinstance(inst_index, int)
        if action.action_type == ActionType.REPLACE:
            raise DeprecationWarning
        elif action.action_type == ActionType.INSERT:
            pos_log_for_insert = generate_inst_pos2type_layers_for_insert(block)
            outer_laters = inst_pos2type_layers_for_insert(inst_index, pos_log_for_insert)
            # print('!@@#VFDVDFBV=====', outer_laters, action_poss[0], action_poss[1])
            cur_context = generate_context_by_out_layers_reuse_data(func0_context, outer_laters)
        else:
            assert 0, print(action)
        new_insts_type = action.exp_type
        new_insts = self.generate_insts(new_insts_type, cur_context)
        reweite_to_ensure_term_easy(ori_parser, insts, new_insts)
        insts[action_poss[0]:action_poss[1]] = new_insts


    def select_aciton(self, insts: List[Inst], func0_context: Context) -> Action:
        length_considering_early_exit = get_early_exit_position(insts, len(func0_context.label_types))
        pos, pos_attr = self.pos_selector.random_select_pos(insts, length_considering_early_exit)
        
        if self.logger is not None:
            self.logger.debug(f'Inst num: {len(insts)}; pos: {pos}; pos_attr: {pos_attr}, length_considering_early_exit: {length_considering_early_exit}; {insts[length_considering_early_exit] if length_considering_early_exit < len(insts) else None}')
        
        new_type = funcTypeFactory.generate_one_func_type_default([], [])
        return Action(ActionType.INSERT, pos, new_type)

    def process_before_write(self, ori_parser: WasmParser):
        pass
