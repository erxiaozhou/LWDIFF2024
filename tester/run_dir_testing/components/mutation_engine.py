from pathlib import Path
from typing import Optional
from extract_block_mutator.fuzzer.BlockInstFuzzer import BlockInstFuzzer
from extract_block_mutator.fuzzer.Fuzzer import Fuzzer
from extract_block_mutator.fuzzer.NaiveModuleFuzzer import ValidModuleFuzzer
from extract_block_mutator.fuzzer.SpecialInstInputFuzzer import SpecialInstInputFuzzer
from extract_block_mutator.blockGenerator.util import block_grammar
from extract_block_mutator.WasmParser import WasmParser
from file_util import check_dir
from generate_tcs_by_mutation_util.generate_tcs_by_mutation_util import Func0ByteFuzzer
from generate_tcs_by_mutation_util.ModuleSecFuzzer import ModuleSecFuzzer
from .CaseNameGenerator import get_new_case_path


class GeneratedMutators:
    _generated_mutators = {}
    _all_supplor_names = [
        'byte_mutate',
        'module_byte_mutate',
        'non_v128_block_mutate',
        'block_mutate',
        'no_return_deep_block',
        'deep_block_mutate',
        'deep_block_mutate2',
        'deep_block_mutate3',
        'no_loop_deep_block_mutate',
        'valid_module_mutate',
        'delete_block',
        'special_op_mutate',
        'delete_return'
    ]
    @staticmethod
    def get_all_action2mutators():
        return GeneratedMutators.generate_enabled_action2mutators(GeneratedMutators._all_supplor_names)
    @staticmethod
    def generate_enabled_action2mutators(action_names:list[str]):
        result = {}
        for name in action_names:
            if name not in GeneratedMutators._generated_mutators:
                mutator = GeneratedMutators.get_mutator_by_name(name)
                GeneratedMutators._generated_mutators[name] = mutator
            result[name] = GeneratedMutators._generated_mutators[name]
        return result

    @staticmethod
    def get_mutator_by_name(name:str) -> Fuzzer:
        if name == 'byte_mutate':
            return Func0ByteFuzzer(check_defined_cals=False)
        elif name == 'module_byte_mutate':
            return ModuleSecFuzzer()
        elif name == 'non_v128_block_mutate':
            return BlockInstFuzzer.from_paras( new_code_short_limit=0, new_code_long_limit=5, non_v128=True, skip_local2store=True, min_block_num=1, max_block_num=3, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None)
        elif name == 'block_mutate':
            return  BlockInstFuzzer.from_paras_for_ZStructFuzzer( new_code_short_limit=1, new_code_long_limit=10, non_v128=True, skip_local2store=True, min_depth=10, max_depth=20, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None)
        elif name == 'no_return_deep_block':
            return BlockInstFuzzer.from_paras( new_code_short_limit=0, new_code_long_limit=5, non_v128=True, no_ereturn=True, skip_local2store=True, min_block_num=10, max_block_num=10, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None)
        elif name == 'deep_block_mutate':
            return BlockInstFuzzer.from_paras_for_ZStructFuzzer( new_code_short_limit=1, new_code_long_limit=10, non_v128=True, skip_local2store=True, min_depth=20, max_depth=50, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None)
        elif name == 'deep_block_mutate2':
            return BlockInstFuzzer.from_paras_for_ZStructFuzzer( new_code_short_limit=1, new_code_long_limit=10, non_v128=True, skip_local2store=True, min_depth=10, max_depth=20, grammar=block_grammar, max_param_num=2, max_result_num=2, ty_str_candidates=None)
        elif name == 'deep_block_mutate3':
            return BlockInstFuzzer.from_paras_for_ZStructFuzzer( new_code_short_limit=0, new_code_long_limit=0, non_v128=True, skip_local2store=True, min_depth=20, max_depth=20, grammar=block_grammar, max_param_num=0, max_result_num=0, ty_str_candidates=None)
        elif name == 'valid_module_mutate':
            return ValidModuleFuzzer()
      
        elif name == 'special_op_mutate':
            return SpecialInstInputFuzzer()
       
        raise ValueError(f'Unknow mutator name {name}')

action2remove_loop_ = {
    'byte_mutate': False,
    'module_byte_mutate': False,
    'non_v128_one_inst_mutate': False,
    'one_inst_mutate': False,
    'non_v128_insts_mutate': False,
    'insts_mutate': False,
    'non_v128_block_mutate': True,
    'block_mutate': True,
    'no_return_deep_block': True,
    'deep_block_mutate': True,
    'deep_block_mutate2':True,
    'deep_block_mutate3':True,
    'no_loop_deep_block_mutate': True,
    'valid_module_mutate': False,
    'delete_block': False,
    'special_imm_mutate': False,
    'special_op_mutate': False,
    'special_op_mutate_debug': False,
    'delete_return': False
}
action2case_name = {
    # ! R ，
    'byte_mutate': 'B',
    'module_byte_mutate': 'M',
    'non_v128_one_inst_mutate': 'C',
    'one_inst_mutate': 'D',
    'non_v128_insts_mutate': 'E',
    'insts_mutate': 'F',
    'non_v128_block_mutate': 'G',
    'block_mutate': 'H',
    'no_return_deep_block': 'I',
    'deep_block_mutate': 'J',
    'no_loop_deep_block_mutate': 'K',
    'valid_module_mutate': 'L',
    'delete_block': 'N',
    'special_imm_mutate': 'O',
    'special_op_mutate': 'P',
    'delete_return': 'Q',
    'deep_block_mutate3': 'R',
    'deep_block_mutate2': 'S',
    'special_op_mutate_debug': 'U'
    
}
class MutationEngine:
    def __init__(self, action2mutators, log_base_dir):
        self.enabled_actions = list(action2mutators.keys())
        self.action2mutators = action2mutators
        self.log_base_dir = check_dir(log_base_dir)

    def get_mutator_by_name(self, name:str) -> Fuzzer:
        return self.action2mutators[name]

    def reset_sop_mutator_by_poss_wraps(self, support_ops=None, pos_candis=None, wraps=None):
        if 'special_op_mutate' in self.action2mutators:
            sop_mutator = SpecialInstInputFuzzer(support_ops, pos_candis, wraps)
            self.action2mutators['special_op_mutate'] = sop_mutator

    def act_mutation(self, ori_path, action, case_batch_size, new_tc_dir, parser:Optional[WasmParser]=None) -> list[str]:
        if action not in self.enabled_actions:
            raise ValueError(f'Unecpected action:{action};; {self.enabled_actions}')
        assert action in self.enabled_actions
        assert ori_path is not None and Path(ori_path).exists()
        action_case_name = action2case_name[action]
        # 
        if action in self.enabled_actions:
            mutator:Fuzzer = self.action2mutators[action]
            if mutator.logger_uninitialized:
                mutator.init_logger(self.log_base_dir, action)
        else:
            raise Exception(f'Unknow action {action}')
        # 
        new_tc_paths = []
        for _ in range(case_batch_size * 10):
            if len(new_tc_paths) >= case_batch_size:
                break
            
            new_path = get_new_case_path(ori_path, new_tc_dir, action_case_name)
            # case,
            paras = {
                'ori_wasm': ori_path,
                'tgt_wasm_path': new_path,
                'remove_loop_': False,
                'parser': parser
            }
            mutator.fuzz_one(**paras)
            if Path(new_path).exists():
                new_tc_paths.append(new_path)
        new_tc_paths = [str(p) for p in new_tc_paths]
        return new_tc_paths
