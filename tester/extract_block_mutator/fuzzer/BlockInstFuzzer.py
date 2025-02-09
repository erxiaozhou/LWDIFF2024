from ..blockGenerator.BlockStructFuzzerZ import BlockStructFuzzerZ
from ..blockGenerator.util import block_grammar
from ..InstGeneration.insts_generator import InstsGenerator
from ..funcType import funcType
from ..randomFuncTypeGenerator import randomFuncTypeGenerator
from WasmInfoCfg import base_ty_strs
from ..WasmParser import WasmParser
from .util import Action
from .instsBaseFuzzer import instsBaseFuzzer
from ..Context import Context
from file_util import get_logger
from ..blockGenerator.tool import generate_insts_contain_block_under_ty_req_by_fuzzer
from ..blockGenerator import BlockStructFuzzerOri
from ..insert_post_process_nan_func import insert_post_process_nan_func_by_easy_sound_strategy
from file_util import get_time_string
action_logger = get_logger(__name__, f'/tmp/BlockInstFuzzer_action-{get_time_string()}.log')


# for the situation that there is no inner block
class BlockInstFuzzer(instsBaseFuzzer):
    def __init__(self, skip_local2store=True,
                 inst_generator:InstsGenerator=None,
                 block_fuzzer:BlockStructFuzzerOri=None,
                 type_generator:randomFuncTypeGenerator=None,
                 logger = action_logger
                 ):
        self.skip_local2store = skip_local2store
        self.block_fuzzer = block_fuzzer
        self.inst_generator = inst_generator
        self.type_generator = type_generator
        self.logger = logger
        super().__init__()

    def generate_insts(self, inst_type: funcType, context: Context):
        insts = generate_insts_contain_block_under_ty_req_by_fuzzer(
            self.block_fuzzer, context, inst_type, self.inst_generator, self.type_generator)
        insert_post_process_nan_func_by_easy_sound_strategy(insts)
        return insts

    def select_aciton(self, *args, **kwds) -> Action:
        return super().select_aciton(*args, **kwds)

    def process_before_write(self, ori_parser: WasmParser):
        pass

    @classmethod
    def from_paras(cls, new_code_short_limit=2, new_code_long_limit=10, non_v128=True, no_ereturn=False, no_unreachable=False, skip_local2store=True, min_block_num=5, max_block_num=20, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None, logger=action_logger):
        if ty_str_candidates is None:
            ty_str_candidates = base_ty_strs
        type_generator = randomFuncTypeGenerator(max_param_num=max_param_num, max_result_num=max_result_num, ty_str_candidates=ty_str_candidates)
        return cls(skip_local2store, InstsGenerator.from_insts_features(new_code_short_limit, new_code_long_limit, non_v128=non_v128, no_ereturn=no_ereturn, no_unreachable=no_unreachable), BlockStructFuzzerOri(grammar, min_nonterminals=min_block_num, max_nonterminals=max_block_num), type_generator=type_generator, logger=logger)

    @classmethod
    def from_paras_for_ZStructFuzzer(cls, new_code_short_limit=2, new_code_long_limit=10, non_v128=True, no_ereturn=False, no_unreachable=False, skip_local2store=True, min_depth=15, max_depth=50, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None, logger=action_logger):
        if ty_str_candidates is None:
            ty_str_candidates = base_ty_strs
        type_generator = randomFuncTypeGenerator(max_param_num=max_param_num, max_result_num=max_result_num, ty_str_candidates=ty_str_candidates)
        return cls(skip_local2store, InstsGenerator.from_insts_features(new_code_short_limit, new_code_long_limit, non_v128=non_v128, no_ereturn=no_ereturn, no_unreachable=no_unreachable), BlockStructFuzzerZ(grammar, min_depth=min_depth, max_depth = max_depth), type_generator=type_generator, logger=logger)
