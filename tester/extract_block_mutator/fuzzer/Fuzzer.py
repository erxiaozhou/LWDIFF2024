from pathlib import Path
from typing import Optional, Union
from ..remove_loop import remove_loop
from ..WasmParser import WasmParser
from file_util import get_logger


class Fuzzer:
    def __init__(self) -> None:
        self.logger = None
        
    def init_logger(self, logger_base_dir, logger_name):
        self.logger = get_logger(logger_name, Path(logger_base_dir)/f'{logger_name}.log')

    @property
    def logger_uninitialized(self):
        return self.logger is None
        
    def fuzz_one(self, ori_wasm: Union[Path, str], tgt_wasm_path, parser:Optional[WasmParser]=None, *args, **kwds) -> None:
        raise NotImplementedError

    def get_parser_of_ori_wasm(self, ori_wasm: Union[Path, str], parser:Optional[WasmParser], remove_loop_=False, *args, **kwds) -> WasmParser:
        if parser is not None:
            
            parser = parser.copy()
            if remove_loop_:
                ori_block = parser.func0_block
                new_block = remove_loop(ori_block)
                assert new_block is not None
                parser.func0_insts = new_block.as_insts()
                parser._func0_block = new_block
        else:
            parser =  WasmParser.from_wasm_path(ori_wasm)
            assert parser is not None
        return parser
