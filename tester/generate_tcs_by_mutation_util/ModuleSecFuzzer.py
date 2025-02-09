import random
import time
from pathlib import Path
from .generate_wasm_tc_util import mutate_BAwithLen, write_wasm_from_dict, BAwithLen
from util.prepare_template import prepare_template
from extract_block_mutator.fuzzer.Fuzzer import Fuzzer
# def mutate

class ModuleSecFuzzer(Fuzzer):
    def __init__(self) -> None:
       super().__init__()

    def fuzz_one(self, ori_wasm, tgt_wasm_path, *args, **kwads):
        sec_template = prepare_template(ori_wasm)
        keys = list(k for k in sec_template.keys() if k != 'pre')
        # print(keys)
        selected_key = random.choice(keys)
        sec_ba = sec_template[selected_key]
        if len(sec_ba) == 0:
            assert self.logger is not None
            self.logger.warning(f'In {ori_wasm}; The length of {selected_key} is 0')
        self.logger.info(f'selected section: {selected_key}, case name: {Path(ori_wasm).stem}')
        ba_with_length = BAwithLen.from_ba_without_length(sec_ba)
        new_ba_with_length = mutate_BAwithLen(ba_with_length, selected_key)
        sec_template[selected_key] = new_ba_with_length.as_vec_encoding()
        write_wasm_from_dict(tgt_wasm_path, sec_template)
